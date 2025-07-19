from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    doubt_id: Optional[str] = None  # Link to specific doubt/question
    message: str
    sender_type: str = "user"  # "user" or "tutor" or "system"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class ChatMessageCreate(BaseModel):
    message: str
    doubt_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    id: str
    message: str
    sender_type: str
    timestamp: datetime
    doubt_id: Optional[str] = None