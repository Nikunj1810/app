from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.doubt import DoubtCreate, DoubtResponse
from models.user import UserResponse
from services.doubt_service import DoubtService
from typing import List
import logging

logger = logging.getLogger(__name__)

def create_doubts_router(db: AsyncIOMotorDatabase, get_current_user) -> APIRouter:
    router = APIRouter(prefix="/doubts", tags=["doubts"])
    doubt_service = DoubtService(db)
    
    @router.post("/", response_model=DoubtResponse)
    async def create_doubt(
        doubt_data: DoubtCreate,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Create a new doubt and get AI solution"""
        try:
            doubt = await doubt_service.create_doubt(current_user.id, doubt_data)
            return doubt
            
        except Exception as e:
            logger.error(f"Error creating doubt: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create doubt"
            )
    
    @router.get("/", response_model=List[DoubtResponse])
    async def get_user_doubts(
        skip: int = 0,
        limit: int = 50,
        current_user: UserResponse = Depends(get_current_user)
    ):
        """Get all doubts for the current user"""
        try:
            doubts = await doubt_service.get_user_doubts(
                current_user.id, skip=skip, limit=limit
            )
            return doubts
            
        except Exception as e:
            logger.error(f"Error getting doubts: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get doubts"
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