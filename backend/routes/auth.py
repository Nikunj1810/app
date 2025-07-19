from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserCreate, UserLogin, UserResponse
from services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

def create_auth_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["authentication"])
    auth_service = AuthService(db)
    
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
        """Get current authenticated user"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        payload = auth_service.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user = await auth_service.get_user_by_id(payload.get("sub"))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    @router.post("/register", response_model=dict)
    async def register(user_data: UserCreate):
        """Register a new user"""
        try:
            user = await auth_service.register_user(user_data)
            access_token = auth_service.create_access_token(data={"sub": user.id})
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user": user,
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    @router.post("/login", response_model=dict)
    async def login(login_data: UserLogin):
        """Authenticate user login"""
        try:
            user = await auth_service.authenticate_user(login_data)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            access_token = auth_service.create_access_token(data={"sub": user.id})
            
            return {
                "success": True,
                "message": "Login successful",
                "user": user,
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    @router.get("/me", response_model=UserResponse)
    async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
        """Get current user information"""
        return current_user
    
    @router.post("/logout")
    async def logout(current_user: UserResponse = Depends(get_current_user)):
        """Logout user (client should remove token)"""
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    
    # Export get_current_user for use in other routes
    router.get_current_user = get_current_user
    
    return router