import time

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage


@tool
def get_leave_balance(employee_id: str):
    """Get the current leave balance of an employee."""
    return "Casual Leave: 12 days annually."


@tool
def search_hr_policy(query: str):
    """Search company HR policies."""
    return "Employees receive 12 Casual Leave days annually."


tools = [
    get_leave_balance,
    search_hr_policy
]


llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,
    num_predict=128
)

llm_with_tools = llm.bind_tools(tools)

messages = [
    SystemMessage(
        content="""
You are an HR assistant.
Use the appropriate tool when needed.
Do not explain your reasoning.
 /no_think
"""
    ),
    HumanMessage(
        content="How many casual leaves are available annually?"
    )
]

start = time.perf_counter()

print("Calling Qwen with tools...")

response = llm_with_tools.invoke(messages)

print("\nResponse:", response.content)
print("\nTool calls:", response.tool_calls)
print("Elapsed:", round(time.perf_counter() - start, 2), "seconds")