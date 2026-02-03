import jwt
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models.user import User
from services.database import database


class AuthService:
    """Service for user authentication."""
    
    def __init__(self):
        """Initialize the auth service."""
        self.users_collection = database.get_collection("users")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using werkzeug."""
        return generate_password_hash(password)
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return check_password_hash(password_hash, password)
    
    def _generate_token(self, user_id: str, email: str) -> str:
        """Generate a JWT token for the user."""
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
    
    def register(self, email: str, password: str, name: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Register a new user.
        
        Returns:
            Tuple of (user_data, error_message)
        """
        if self.users_collection is None:
            return None, "Database not connected"
        
        # Validate input
        if not email or not password:
            return None, "Email and password are required"
        
        if len(password) < 6:
            return None, "Password must be at least 6 characters"
        
        # Check if user already exists
        existing_user = self.users_collection.find_one({"email": email.lower()})
        if existing_user:
            return None, "User with this email already exists"
        
        # Create user
        user = User(
            email=email.lower(),
            password_hash=self._hash_password(password),
            name=name
        )
        
        # Insert into database
        result = self.users_collection.insert_one(user.to_dict())
        user_id = str(result.inserted_id)
        
        # Generate token
        token = self._generate_token(user_id, user.email)
        
        return {
            "user_id": user_id,
            "email": user.email,
            "name": user.name,
            "token": token
        }, None
    
    def login(self, email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Login a user.
        
        Returns:
            Tuple of (user_data, error_message)
        """
        if self.users_collection is None:
            return None, "Database not connected"
        
        # Validate input
        if not email or not password:
            return None, "Email and password are required"
        
        # Find user
        user_doc = self.users_collection.find_one({"email": email.lower()})
        if not user_doc:
            return None, "Invalid email or password"
        
        user = User.from_dict(user_doc)
        
        # Verify password
        if not self._verify_password(password, user.password_hash):
            return None, "Invalid email or password"
        
        # Generate token
        token = self._generate_token(user._id, user.email)
        
        return {
            "user_id": user._id,
            "email": user.email,
            "name": user.name,
            "token": token
        }, None
    
    def verify_token(self, token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Verify a JWT token.
        
        Returns:
            Tuple of (payload, error_message)
        """
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"


# Singleton instance
auth_service = AuthService()
