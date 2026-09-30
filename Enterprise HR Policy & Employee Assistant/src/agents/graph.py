from typing import Annotated
from typing_extensions import TypedDict

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

from src.agents.tools import call_mcp_tool
from src.Rag.retrieval import Retriever
from src.Rag.embedding import create_vector_store
from src.app_logging.logger import get_logger



logger=get_logger("agent")
# ============================================================
# STATE


class HRState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    employee_id: str


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
def search_hr_policy(query: str):
    """Search company HR policies and return relevant policy information."""

    context = retriever.get_context(
        query,
        k=5
    )

    return context


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
"""
    )

    response = await llm_with_tools.ainvoke(
        [
            system_message
        ] + state["messages"]
    )

    return {
        "messages": [response]
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
        return "tool_node"

    return END


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
        "tool_node": "tool_node",
        END: END
    }
)


# TOOL → LLM

graph_builder.add_edge(
    "tool_node",
    "llm_call"
)


graph = graph_builder.compile()