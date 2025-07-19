from motor.motor_asyncio import AsyncIOMotorDatabase
from models.doubt import Doubt, DoubtCreate, DoubtResponse
from services.ai_service import AIService
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DoubtService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ai_service = AIService()
    
    async def create_doubt(self, user_id: str, doubt_data: DoubtCreate) -> DoubtResponse:
        """Create a new doubt and process it with AI"""
        try:
            # Create doubt instance
            doubt = Doubt(
                user_id=user_id,
                question=doubt_data.question,
                subject=doubt_data.subject,
                question_type=doubt_data.question_type,
                image_data=doubt_data.image_data,
                status="processing"
            )
            
            # Insert into database
            await self.db.doubts.insert_one(doubt.dict())
            
            # Process with AI in background (for now, process immediately)
            try:
                if doubt_data.question_type == "image" and doubt_data.image_data:
                    answer = await self.ai_service.process_image_question(
                        doubt_data.question,
                        doubt_data.subject,
                        doubt_data.image_data
                    )
                else:
                    answer = await self.ai_service.process_text_question(
                        doubt_data.question,
                        doubt_data.subject
                    )
                
                # Update doubt with answer
                doubt.answer = answer
                doubt.status = "answered"
                doubt.updated_at = datetime.utcnow()
                
                # Update in database
                await self.db.doubts.update_one(
                    {"id": doubt.id},
                    {"$set": {
                        "answer": answer.dict(),
                        "status": "answered",
                        "updated_at": doubt.updated_at
                    }}
                )
                
            except Exception as ai_error:
                logger.error(f"AI processing error: {str(ai_error)}")
                doubt.status = "failed"
                await self.db.doubts.update_one(
                    {"id": doubt.id},
                    {"$set": {"status": "failed", "updated_at": datetime.utcnow()}}
                )
            
            return DoubtResponse(
                id=doubt.id,
                question=doubt.question,
                subject=doubt.subject,
                question_type=doubt.question_type,
                image_data=doubt.image_data,
                answer=doubt.answer,
                status=doubt.status,
                created_at=doubt.created_at,
                updated_at=doubt.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error creating doubt: {str(e)}")
            raise Exception("Failed to create doubt")
    
    async def get_user_doubts(self, user_id: str, skip: int = 0, limit: int = 50) -> List[DoubtResponse]:
        """Get all doubts for a user"""
        try:
            cursor = self.db.doubts.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            
            doubts = []
            async for doubt_doc in cursor:
                doubt_response = DoubtResponse(
                    id=doubt_doc["id"],
                    question=doubt_doc["question"],
                    subject=doubt_doc["subject"],
                    question_type=doubt_doc["question_type"],
                    image_data=doubt_doc.get("image_data"),
                    answer=doubt_doc.get("answer"),
                    status=doubt_doc["status"],
                    created_at=doubt_doc["created_at"],
                    updated_at=doubt_doc["updated_at"]
                )
                doubts.append(doubt_response)
            
            return doubts
            
        except Exception as e:
            logger.error(f"Error getting user doubts: {str(e)}")
            raise Exception("Failed to get doubts")
    
    async def get_doubt_by_id(self, doubt_id: str, user_id: str) -> Optional[DoubtResponse]:
        """Get a specific doubt by ID"""
        try:
            doubt_doc = await self.db.doubts.find_one({
                "id": doubt_id,
                "user_id": user_id
            })
            
            if not doubt_doc:
                return None
            
            return DoubtResponse(
                id=doubt_doc["id"],
                question=doubt_doc["question"],
                subject=doubt_doc["subject"],
                question_type=doubt_doc["question_type"],
                image_data=doubt_doc.get("image_data"),
                answer=doubt_doc.get("answer"),
                status=doubt_doc["status"],
                created_at=doubt_doc["created_at"],
                updated_at=doubt_doc["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Error getting doubt: {str(e)}")
            return None
    
    async def delete_doubt(self, doubt_id: str, user_id: str) -> bool:
        """Delete a doubt"""
        try:
            result = await self.db.doubts.delete_one({
                "id": doubt_id,
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting doubt: {str(e)}")
            return False