from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.chat import ChatMessageCreate, ChatMessageResponse
from models.user import UserResponse
from services.chat_service import ChatService
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def create_chat_router(db: AsyncIOMotorDatabase, get_current_user) -> APIRouter:
    router = APIRouter(prefix="/chat", tags=["chat"])
    chat_service = ChatService(db)
    
    @router.post("/send", response_model=ChatMessageResponse)
    async def send_chat_message(
        message_data: ChatMessageCreate,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Send a message to tutor (POST /api/chat/send)"""
        try:
            message = await chat_service.send_message(current_user.id, message_data)
            return message
            
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message"
            )
    
    @router.get("/messages", response_model=List[ChatMessageResponse])
    async def get_chat_messages(
        doubt_id: Optional[str] = None,
        limit: int = 50,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Get chat messages for current user"""
        try:
            messages = await chat_service.get_chat_messages(
                current_user.id, doubt_id=doubt_id, limit=limit
            )
            return messages
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get messages"
            )
    
    return router