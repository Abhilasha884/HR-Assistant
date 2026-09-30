import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


project_root = Path(__file__).resolve().parents[2]

transport = StdioTransport(
    command=sys.executable,
    args=["-m", "src.mcp.server"],
    cwd=str(project_root),
)

client = Client(transport)


async def call_mcp_tool(tool_name: str, arguments: dict):

    async with client:

        result = await client.call_tool(
            tool_name,
            arguments
        )

        return result


async def main():

    result = await call_mcp_tool(
        "get_employee_details",
        {
            "employee_id": "EMP001"
        }
    )

    print("MCP Result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())