import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from models.user import User, UserCreate, UserLogin, UserResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET_KEY", "doubsolver_secret_key_2024")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30 * 24 * 60  # 30 days
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.db.users.find_one({"email": user_data.email})
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Create new user
            hashed_password = self.get_password_hash(user_data.password)
            user = User(
                name=user_data.name,
                email=user_data.email,
                password_hash=hashed_password
            )
            
            # Insert into database
            result = await self.db.users.insert_one(user.dict())
            
            # Return user response
            return UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                created_at=user.created_at
            )
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise Exception("Failed to register user")
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[UserResponse]:
        """Authenticate a user login"""
        try:
            # Find user by email
            user_doc = await self.db.users.find_one({"email": login_data.email})
            if not user_doc:
                return None
            
            # Verify password
            if not self.verify_password(login_data.password, user_doc["password_hash"]):
                return None
            
            # Return user response
            return UserResponse(
                id=user_doc["id"],
                name=user_doc["name"],
                email=user_doc["email"],
                created_at=user_doc["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            user_doc = await self.db.users.find_one({"id": user_id})
            if not user_doc:
                return None
            
            return UserResponse(
                id=user_doc["id"],
                name=user_doc["name"],
                email=user_doc["email"],
                created_at=user_doc["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None