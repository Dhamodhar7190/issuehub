"""
Pydantic schemas for Comment-related API requests and responses.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.user import UserResponse


class CommentCreate(BaseModel):
    """
    Schema for creating a new comment.
    
    Used in: POST /api/issues/{id}/comments
    
    Example request:
        {
            "body": "I'm experiencing the same issue on Chrome 120"
        }
        
    Note: 
        - author_id is set automatically from authenticated user
        - issue_id comes from URL path parameter
    """
    body: str = Field(..., min_length=1, max_length=5000, description="Comment text")


class CommentResponse(BaseModel):
    """
    Schema for comment data in API responses.
    
    Used in: GET /api/issues/{id}/comments
    
    Example response:
        {
            "id": 1,
            "issue_id": 5,
            "author": {
                "id": 3,
                "name": "Charlie",
                "email": "charlie@example.com",
                "created_at": "2024-01-12T10:00:00Z"
            },
            "body": "I'm experiencing the same issue...",
            "created_at": "2024-01-15T16:45:00Z"
        }
    """
    id: int
    issue_id: int
    author: UserResponse  # Nested user object
    body: str
    created_at: datetime

    class Config:
        from_attributes = True