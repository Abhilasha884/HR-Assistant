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


async def main():

    async with client:

       result=await client.call_tool(
           "get_leave_balance",
           {
               "employee_id":"EMP001"
           }
        )
       print("Employee Details")
       print(result)


if __name__ == "__main__":
    asyncio.run(main())