from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.doubt import DoubtCreate, DoubtResponse, ImageQuestionCreate
from models.user import UserResponse
from services.doubt_service import DoubtService
from services.ocr_service import OCRService
from typing import List, Optional
import logging
import base64
import aiofiles
import tempfile
import os
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TextQuestionRequest(BaseModel):
    question: str
    subject: str

class ImageUploadResponse(BaseModel):
    success: bool
    message: str
    ocr_text: Optional[str] = None
    image_base64: Optional[str] = None
    processing_info: Optional[dict] = None

logger = logging.getLogger(__name__)

def create_doubts_router(db: AsyncIOMotorDatabase, get_current_user) -> APIRouter:
    router = APIRouter(prefix="/questions", tags=["questions"])  # Changed prefix to match requirements
    doubt_service = DoubtService(db)
    ocr_service = OCRService()
    
    @router.post("/text", response_model=DoubtResponse)
    async def create_text_question(
        request: TextQuestionRequest,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Process a text-based question (POST /api/questions/text)"""
        try:
            doubt_data = DoubtCreate(
                question=request.question,
                subject=request.subject,
                question_type="text"
            )
            doubt = await doubt_service.create_doubt(current_user.id, doubt_data)
            return doubt
            
        except Exception as e:
            logger.error(f"Error creating text question: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process text question"
            )
    
    @router.post("/image", response_model=DoubtResponse)
    async def create_image_question(
        file: UploadFile = File(...),
        question: str = Form(""),
        subject: str = Form("mathematics"),
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Process an image-based question with OCR (POST /api/questions/image)"""
        try:
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(allowed_types)}"
                )
            
            # Check file size (10MB limit)
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size too large. Maximum allowed: 10MB"
                )
            
            # Convert to base64
            image_base64 = base64.b64encode(content).decode('utf-8')
            
            # Validate image
            validation_result = ocr_service.validate_image(image_base64)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid image file: {validation_result.get('error', 'Unknown error')}"
                )
            
            # Extract text using OCR
            ocr_result = ocr_service.extract_text_from_base64(image_base64)
            
            # Prepare question text
            final_question = question.strip()
            if ocr_result["success"] and ocr_result["extracted_text"]:
                if final_question:
                    final_question += f"\n\nExtracted text from image: {ocr_result['extracted_text']}"
                else:
                    final_question = f"Please solve this problem from the image: {ocr_result['extracted_text']}"
            elif not final_question:
                final_question = "Please analyze and solve the problem shown in this image."
            
            # Create doubt with image and OCR data
            doubt_data = DoubtCreate(
                question=final_question,
                subject=subject,
                question_type="image",
                image_data=image_base64
            )
            
            doubt = await doubt_service.create_doubt(current_user.id, doubt_data)
            return doubt
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating image question: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process image question"
            )
    
    @router.get("/user/{user_id}", response_model=List[DoubtResponse])
    async def get_user_question_history(
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Get question history for a specific user (GET /api/questions/user/:userId)"""
        try:
            # Check if current user is requesting their own data or has admin privileges
            if current_user.id != user_id:
                # For now, users can only access their own data
                # In future, you might add admin role checking here
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You can only access your own question history"
                )
            
            doubts = await doubt_service.get_user_doubts(
                user_id, skip=skip, limit=limit
            )
            return doubts
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user questions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get question history"
            )
    
    @router.get("/{doubt_id}", response_model=DoubtResponse)
    async def get_doubt(
        doubt_id: str,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Get a specific doubt by ID"""
        try:
            doubt = await doubt_service.get_doubt_by_id(doubt_id, current_user.id)
            if not doubt:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doubt not found"
                )
            return doubt
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting doubt: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get doubt"
            )
    
    @router.delete("/{doubt_id}")
    async def delete_doubt(
        doubt_id: str,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Delete a doubt"""
        try:
            success = await doubt_service.delete_doubt(doubt_id, current_user.id)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doubt not found"
                )
            
            return {
                "success": True,
                "message": "Doubt deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting doubt: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete doubt"
            )
    
    # Public endpoint for demo (no auth required)
    @router.post("/demo", response_model=DoubtResponse)
    async def create_demo_doubt(doubt_data: DoubtCreate):
        """Create a demo doubt without authentication"""
        try:
            # Use a demo user ID
            demo_user_id = "demo_user"
            doubt = await doubt_service.create_doubt(demo_user_id, doubt_data)
            return doubt
            
        except Exception as e:
            logger.error(f"Error creating demo doubt: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create demo doubt"
            )
    
    return router