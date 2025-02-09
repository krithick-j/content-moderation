from pydantic import BaseModel


class ModerationRequest(BaseModel):
    text: str
    
class ModerationResponse(BaseModel):
    task_id: str