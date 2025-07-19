from motor.motor_asyncio import AsyncIOMotorDatabase
from models.chat import ChatMessage, ChatMessageCreate, ChatMessageResponse
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def send_message(self, user_id: str, message_data: ChatMessageCreate) -> ChatMessageResponse:
        """Send a message in chat"""
        try:
            # Create chat message
            chat_message = ChatMessage(
                user_id=user_id,
                message=message_data.message,
                doubt_id=message_data.doubt_id,
                sender_type="user"
            )
            
            # Insert into database
            await self.db.chat_messages.insert_one(chat_message.dict())
            
            # Auto-reply for demo purposes (in real app, this would be human tutor or AI)
            auto_reply = ChatMessage(
                user_id="system",
                message="Thank you for your message! A tutor will respond shortly.",
                doubt_id=message_data.doubt_id,
                sender_type="tutor"
            )
            
            await self.db.chat_messages.insert_one(auto_reply.dict())
            
            return ChatMessageResponse(
                id=chat_message.id,
                message=chat_message.message,
                sender_type=chat_message.sender_type,
                timestamp=chat_message.timestamp,
                doubt_id=chat_message.doubt_id
            )
            
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
            raise Exception("Failed to send message")
    
    async def get_chat_messages(self, user_id: str, doubt_id: Optional[str] = None, limit: int = 50) -> List[ChatMessageResponse]:
        """Get chat messages for a user"""
        try:
            # Build query
            query = {"$or": [{"user_id": user_id}, {"sender_type": "tutor"}]}
            if doubt_id:
                query["doubt_id"] = doubt_id
            
            cursor = self.db.chat_messages.find(query).sort("timestamp", -1).limit(limit)
            
            messages = []
            async for msg_doc in cursor:
                message_response = ChatMessageResponse(
                    id=msg_doc["id"],
                    message=msg_doc["message"],
                    sender_type=msg_doc["sender_type"],
                    timestamp=msg_doc["timestamp"],
                    doubt_id=msg_doc.get("doubt_id")
                )
                messages.append(message_response)
            
            return list(reversed(messages))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            raise Exception("Failed to get chat messages")