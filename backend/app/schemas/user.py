"""
Pydantic schemas for User-related API requests and responses.

Schemas define:
- What data the API accepts (request models)
- What data the API returns (response models)
- Validation rules for each field
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for user registration (signup).
    
    Used in: POST /api/auth/signup
    
    Example request body:
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "password": "SecurePass123!"
        }
    """
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    email: EmailStr = Field(..., description="Valid email address for login")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")


class UserLogin(BaseModel):
    """
    Schema for user login.
    
    Used in: POST /api/auth/login
    
    Example request body:
        {
            "email": "alice@example.com",
            "password": "SecurePass123!"
        }
    """
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.
    
    Used in: GET /api/me, and nested in other responses
    
    Note: NEVER include password_hash in responses!
    
    Example response:
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        # Allows Pydantic to work with SQLAlchemy models
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Schema for authentication token response.
    
    Used in: POST /api/auth/login (successful login)
    
    Example response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        
    Frontend usage:
        - Store access_token in memory or secure storage
        - Send in Authorization header: "Bearer <access_token>"
    """
    access_token: str
    token_type: str = "bearer"