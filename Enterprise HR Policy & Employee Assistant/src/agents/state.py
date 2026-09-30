from typing import TypedDict,Optional

class HRState(TypedDict):
    user_query:str
    employee_id:Optional[str]
    intent:Optional[str]
    retrieved_docs:Optional[str]
    tool_result:Optional[dict]
    final_response:Optional[str]