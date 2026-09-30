from src.agents.state import HRState

def identify_intent(state:HRState):
    query = state["user_query"].lower()

    if "leave balance" in query:
        state["intent"] = "leave_balance"

    elif "employee" in query:
        state["intent"] = "employee_details"

    elif "holiday" in query:
        state["intent"] = "holiday"

    elif "salary" in query or "payroll" in query:
        state["intent"] = "payroll"

    else:
        state["intent"] = "policy"

    return state