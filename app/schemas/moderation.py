from pydantic import BaseModel
from pydantic import BaseModel, Json


class ModerationRequest(BaseModel):
    text: str
    
class ModerationResponse(BaseModel):
    task_id: str

class ModerationResultResponse(BaseModel):
    task_id: str
    result: dict
    status: str