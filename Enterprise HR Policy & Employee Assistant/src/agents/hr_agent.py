from src.agents.graph import graph


def run_agent(query: str):

    state = {
        "user_query": query,
        "employee_id": "EMP001"
    }

    result = graph.invoke(state)

    return result