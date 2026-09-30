import asyncio

from langchain_core.messages import HumanMessage

from src.agents.graph import graph


async def main():

    employee_id = "EMP001"

    print("\n========================================")
    print("      Enterprise HR Assistant")
    print("========================================")
    print("Type your question below.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:

        user_query = input("You: ")

        if user_query.lower() in {"exit", "quit"}:
            print("\nHR Assistant: Goodbye!")
            break

        if not user_query.strip():
            continue

        result = await graph.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content=user_query
                    )
                ],
                "employee_id": employee_id
            }
        )

        final_message = result["messages"][-1]

        print(
            f"\nAssistant: {final_message.content}\n"
        )


if __name__ == "__main__":
    asyncio.run(main())