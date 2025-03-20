from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext

from app.db.session import Base

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """User model for authentication.

    Attributes:
        id: Primary key
        username: Username for the authentication
        email: Email address for the user
        hashed_password: Password hash for the user
        is_active: Whether the user is active
        created_at: When the user was created
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    transitions = relationship(
        "MoodTransition",
        back_populates="user")
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password):
        """Generate password hash."""
        return pwd_context.hash(password)