from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class DoubtAnswer(BaseModel):
    solution: str
    steps: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class Doubt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    question: str
    subject: str
    question_type: str  # "text" or "image"
    image_data: Optional[str] = None  # base64 encoded image
    answer: Optional[DoubtAnswer] = None
    status: str = "processing"  # "processing", "answered", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DoubtCreate(BaseModel):
    question: str
    subject: str
    question_type: str = "text"
    image_data: Optional[str] = None

class DoubtResponse(BaseModel):
    id: str
    question: str
    subject: str
    question_type: str
    image_data: Optional[str] = None
    answer: Optional[DoubtAnswer] = None
    status: str
    created_at: datetime
    updated_at: datetime