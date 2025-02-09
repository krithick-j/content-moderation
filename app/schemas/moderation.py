from pydantic import BaseModel


class ModerationRequest(BaseModel):
    text: str
    
class ModerationResponse(BaseModel):
    task_id: str

class ModerationResultResponse(BaseModel):
    task_id: str
    result: str
    status: str