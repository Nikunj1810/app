from motor.motor_asyncio import AsyncIOMotorDatabase
from models.doubt import Doubt, DoubtCreate, DoubtResponse
from services.ai_service import AIService
from services.ocr_service import OCRService
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DoubtService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ai_service = AIService()
        self.ocr_service = OCRService()
    
    async def create_doubt(self, user_id: str, doubt_data: DoubtCreate) -> DoubtResponse:
        """Create a new doubt and process it with AI"""
        try:
            # Initialize OCR data
            ocr_data = None
            
            # If it's an image question, extract OCR data for additional context
            if doubt_data.question_type == "image" and doubt_data.image_data:
                ocr_result = self.ocr_service.extract_text_from_base64(doubt_data.image_data)
                if ocr_result["success"]:
                    ocr_data = {
                        "extracted_text": ocr_result["extracted_text"],
                        "confidence_scores": ocr_result["confidence_scores"],
                        "preprocessing_used": ocr_result["preprocessing_used"],
                        "average_confidence": ocr_result.get("average_confidence", 0)
                    }
                    logger.info(f"OCR extraction successful: {len(ocr_result['extracted_text'])} characters extracted")
            
            # Create doubt instance
            doubt = Doubt(
                user_id=user_id,
                question=doubt_data.question,
                subject=doubt_data.subject,
                question_type=doubt_data.question_type,
                image_data=doubt_data.image_data,
                ocr_data=ocr_data,
                status="processing"
            )
            
            # Insert into database
            await self.db.doubts.insert_one(doubt.dict())
            
            # Process with AI in background (for now, process immediately)
            try:
                if doubt_data.question_type == "image" and doubt_data.image_data:
                    # For image questions, use enhanced question with OCR context
                    enhanced_question = doubt_data.question
                    if ocr_data and ocr_data["extracted_text"]:
                        context_info = f"\n\nOCR extracted text (confidence: {ocr_data.get('average_confidence', 0):.1f}%): {ocr_data['extracted_text']}"
                        enhanced_question += context_info
                    
                    answer = await self.ai_service.process_image_question(
                        enhanced_question,
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
                ocr_data=doubt.ocr_data,
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