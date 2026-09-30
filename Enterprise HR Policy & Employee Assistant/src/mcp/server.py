from fastmcp import FastMCP
from src.mcp.employee_tools import get_employee_details,get_leave_balance,get_leave_requests,get_holidays,check_holiday,get_payroll,get_latest_payroll,create_session,get_session,update_session_activity,close_session,submit_leave_requests,cancel_leave_request,approve_leave_request,reject_leave_request
mcp=FastMCP("HR Assistant MCP server")

@mcp.tool
def test()->str:
    """Testing server"""
    return "Server is working correctly"


mcp.tool(get_employee_details)
mcp.tool(get_leave_balance)
mcp.tool(get_leave_requests)
mcp.tool(get_holidays)
mcp.tool(check_holiday)
mcp.tool(get_payroll)
mcp.tool(get_latest_payroll)
mcp.tool(create_session)
mcp.tool(get_session)
mcp.tool(update_session_activity)
mcp.tool(close_session)
mcp.tool(submit_leave_requests)
mcp.tool(cancel_leave_request)
mcp.tool(approve_leave_request)
mcp.tool(reject_leave_request)
if __name__ == "__main__":
    mcp.run()