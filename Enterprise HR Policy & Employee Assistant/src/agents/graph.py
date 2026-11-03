from typing import Annotated
from typing_extensions import TypedDict

import time
from langchain_ollama import ChatOllama
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from src.agents.tools import call_mcp_tool
from src.Rag.retrieval import Retriever
from src.Rag.embedding import create_vector_store
from src.app_logging.logger import get_logger
from src.mcp.employee_tools import submit_leave_requests



logger=get_logger("agent")
# ============================================================
# STATE


class HRState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    employee_id: str
    leave_confirmed:bool


# ============================================================
# RAG SETUP
# ============================================================

vector_store = create_vector_store()
retriever = Retriever(vector_store)


# ============================================================
# QWEN3
# ============================================================

llm = ChatOllama(
    model="qwen3:4b",
    temperature=0
)


# ============================================================
# TOOLS
# ============================================================

@tool
async def get_employee_details(employee_id: str):
    """Get employee details for a specific employee."""

    result = await call_mcp_tool(
        "get_employee_details",
        {
            "employee_id": employee_id
        }
    )

    if hasattr(result, "data"):
        return result.data

    if hasattr(result, "structured_content"):
        return result.structured_content

    return str(result)


@tool
async def get_leave_balance(employee_id: str):
    """Get the current leave balance of an employee, including casual leave, earned leave and sick leave."""

    result = await call_mcp_tool(
        "get_leave_balance",
        {
            "employee_id": employee_id
        }
    )

    if hasattr(result, "data"):
        return result.data

    if hasattr(result, "structured_content"):
        return result.structured_content

    return str(result)


@tool
async def get_leave_requests(employee_id: str):
    """Get leave requests submitted by an employee."""

    result = await call_mcp_tool(
        "get_leave_requests",
        {
            "employee_id": employee_id
        }
    )

    if hasattr(result, "data"):
        return result.data

    if hasattr(result, "structured_content"):
        return result.structured_content

    return str(result)


@tool
async def get_holidays():
    """Get the company holiday list."""

    result = await call_mcp_tool(
        "get_holidays",
        {}
    )

    if hasattr(result, "data"):
        return result.data

    if hasattr(result, "structured_content"):
        return result.structured_content

    return str(result)


@tool
async def get_latest_payroll(employee_id: str):
    """Get the latest payroll information for an employee."""

    result = await call_mcp_tool(
        "get_latest_payroll",
        {
            "employee_id": employee_id
        }
    )

    if hasattr(result, "data"):
        return result.data

    if hasattr(result, "structured_content"):
        return result.structured_content

    return str(result)

@tool
async def search_hr_policy(query: str):
    """Search company HR policies and return relevant policy information."""

    start = time.perf_counter()

    logger.info(f"RAG_SEARCH_START | query={query}")

    try:
        context = retriever.get_context(
            query,
            k=5
        )

        elapsed = time.perf_counter() - start

        logger.info(
            f"RAG_SEARCH_SUCCESS | elapsed={elapsed:.2f}s "
            f"| context_length={len(str(context))}"
        )

        return context

    except Exception as error:
        logger.exception(f"RAG_SEARCH_ERROR | error={error}")
        raise



@tool
async def apply_for_leave(
    employee_id: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    number_of_days: float,
    reason: str = None
) -> dict:
    """
    Submit a leave request for an employee.

    Use this tool only after the employee has explicitly confirmed
    the leave details.
    """
    result = await call_mcp_tool(
        "submit_leave_requests",
        {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "number_of_days": number_of_days,
            "reason": reason
        }
    )

    if hasattr(result, "data"):
        return result.data

    if hasattr(result, "structured_content"):
        return result.structured_content

    return str(result)
# ============================================================
# TOOL LIST
# ============================================================

tools = [
    get_employee_details,
    get_leave_balance,
    get_leave_requests,
    get_holidays,
    get_latest_payroll,
    search_hr_policy,
    apply_for_leave
]


# Create lookup dictionary
tools_by_name = {
    tool.name: tool
    for tool in tools
}


# Bind tools to Qwen3
llm_with_tools = llm.bind_tools(tools)


# ============================================================
# LLM NODE
# ============================================================


async def llm_call(state: HRState):

    start = time.perf_counter()

    logger.info(
        f"LLM_START | employee_id={state['employee_id']} "
        f"| messages={len(state['messages'])}"
    )

    system_message = SystemMessage(
        content=f"""
You are an Enterprise HR Assistant.

The current employee ID is:
{state["employee_id"]}

You have access to tools for employee information,
leave information, holidays, payroll and company HR policies.

Use the appropriate tool when the user's question requires
information from the employee database or company policy documents.

Important rules:

- Use tools instead of guessing.
- For employee-specific information, use the employee ID provided above.
- For leave balance questions, use the leave balance tool.
- For employee details, use the employee details tool.
- For leave request questions, use the leave requests tool.
- For holiday questions, use the holidays tool.
- For salary or payroll questions, use the payroll tool.
- For company HR policy questions, use the HR policy search tool.
- Do not invent information.
- After receiving tool results, answer the employee clearly.
- Do not mention internal tools, MCP, RAG, embeddings or vector databases.
- Give a normal natural-language answer.
Leave Application Rules
1. When an employee wants to apply for leave, collect:
   - Leave type
   - Start date
   - End date
   - Number of leave days
   - Reason (optional)
2. Resolve relative dates such as "tomorrow" into YYYY-MM-DD format.
3. Use the employee_id from the current session state.
   Never ask the LLM to invent or change the employee_id.

4. Before submitting, show the employee the complete leave details.

5. Ask the employee for explicit confirmation before submitting.
6. Call apply_for_leave only after the employee confirms.
7. If the employee has not confirmed, do not call apply_for_leave.
8. After calling the tool:
   - If the response contains an error, explain the error.
   - If submission succeeds, confirm the request ID and submitted details.
   - Never claim a request was submitted unless the tool confirms success.
"""
    )

    try:
        response = await llm_with_tools.ainvoke(
            [system_message] + state["messages"]
        )

        elapsed = time.perf_counter() - start

        logger.info(
            f"LLM_SUCCESS | employee_id={state['employee_id']} "
            f"| elapsed={elapsed:.2f}s "
            f"| tool_calls={len(response.tool_calls)}"
        )

        return {
            "messages": [response]
        }

    except Exception:
        logger.exception(
            f"LLM_ERROR | employee_id={state['employee_id']}"
        )
        raise


#============================================================
#  Confirmation node
#============================================================


async def confirm_leave(state: HRState):

    last_message = state["messages"][-1]

    leave_tool_call = next(
        (
            call for call in last_message.tool_calls
            if call["name"] == "apply_for_leave"
        ),
        None
    )

    if not leave_tool_call:
        return {"leave_confirmed": False}

    leave_details = dict(leave_tool_call["args"])
    leave_details["employee_id"] = state["employee_id"]

    confirmation = interrupt({
        "question": "Please confirm your leave application.",
        "leave_details": leave_details
    })

    if confirmation is True:
        return {"leave_confirmed": True}

    return {
        "leave_confirmed": False,
        "messages": [
            ToolMessage(
                content="The employee cancelled the leave application. No leave was submitted.",
                tool_call_id=leave_tool_call["id"]
            )
        ]
    }
# ============================================================
# TOOL NODE
# ============================================================

async def tool_node(state: HRState):

    results = []

    last_message = state["messages"][-1]

    employee_id = state["employee_id"]

    for tool_call in last_message.tool_calls:

        tool_name = tool_call["name"]

        logger.info(
            f"TOOL_CALL | employee_id={employee_id} "
            f"| tool={tool_name}"
        )

        tool = tools_by_name[tool_name]

        try:

            observation = await tool.ainvoke(
                tool_call["args"]
            )

            logger.info(
                f"TOOL_SUCCESS | employee_id={employee_id} "
                f"| tool={tool_name}"
            )

        except Exception as error:

            logger.error(
                f"TOOL_ERROR | employee_id={employee_id} "
                f"| tool={tool_name} "
                f"| error={str(error)}"
            )

            raise

        results.append(
            ToolMessage(
                content=str(observation),
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": results}

# ============================================================
# ROUTING AFTER LLM
# ============================================================

def should_continue(state: HRState):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        if any(
            call['name']=="apply_for_leave"
            for call in last_message.tool_calls
        ):
            return "confirm_leave"
        return "tool_node"

    return END

def route_after_confirmation(state: HRState):

    if state.get("leave_confirmed") is True:
        return "tool_node"

    return "llm_call"

# ============================================================
# BUILD GRAPH
# ============================================================

graph_builder = StateGraph(HRState)


graph_builder.add_node(
    "llm_call",
    llm_call
)


graph_builder.add_node(
    "tool_node",
    tool_node
)

graph_builder.add_node(
    "confirm_leave",
    confirm_leave
)

# START → LLM

graph_builder.add_edge(
    START,
    "llm_call"
)


# LLM → TOOL or END

graph_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "confirm_leave": "confirm_leave",
        "tool_node": "tool_node",
        END: END
    }
)

graph_builder.add_conditional_edges(
    "confirm_leave",
    route_after_confirmation,
    {
        "tool_node": "tool_node",
        "llm_call": "llm_call"
    }
)
# TOOL → LLM

graph_builder.add_edge(
    "tool_node",
    "llm_call"
)

checkpointer=InMemorySaver()
graph = graph_builder.compile(
    checkpointer=checkpointer
)