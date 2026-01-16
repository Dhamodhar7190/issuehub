"""
Pydantic schemas for Issue-related API requests and responses.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.issue import IssueStatus, IssuePriority
from app.schemas.user import UserResponse


class IssueCreate(BaseModel):
    """
    Schema for creating a new issue.
    
    Used in: POST /api/projects/{id}/issues
    
    Example request:
        {
            "title": "Login button not responding",
            "description": "When clicking login, nothing happens...",
            "priority": "high",
            "assignee_id": 2
        }
        
    Note: 
        - reporter_id is set automatically from authenticated user
        - status defaults to "open"
    """
    title: str = Field(..., min_length=1, max_length=200, description="Issue title")
    description: Optional[str] = Field(None, max_length=5000, description="Detailed description")
    priority: IssuePriority = Field(default=IssuePriority.MEDIUM, description="Priority level")
    assignee_id: Optional[int] = Field(None, description="User ID to assign (optional)")


class IssueUpdate(BaseModel):
    """
    Schema for updating an existing issue.
    
    Used in: PATCH /api/issues/{id}
    
    Example request (partial update):
        {
            "status": "in_progress",
            "assignee_id": 3
        }
        
    Note: All fields are optional - only provided fields will be updated
    
    Permissions:
        - Reporter can update: title, description
        - Maintainer can update: all fields including status, priority, assignee
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None


class IssueResponse(BaseModel):
    """
    Schema for issue data in API responses.
    
    Used in: GET /api/issues, GET /api/issues/{id}
    
    Example response:
        {
            "id": 1,
            "project_id": 1,
            "title": "Login button not responding",
            "description": "When clicking login...",
            "status": "open",
            "priority": "high",
            "reporter": {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "created_at": "2024-01-10T08:00:00Z"
            },
            "assignee": {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "created_at": "2024-01-10T09:00:00Z"
            },
            "created_at": "2024-01-15T14:30:00Z",
            "updated_at": "2024-01-15T15:00:00Z"
        }
    """
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: IssueStatus
    priority: IssuePriority
    reporter: UserResponse  # Nested user object
    assignee: Optional[UserResponse]  # Can be None if unassigned
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IssueListResponse(BaseModel):
    """
    Schema for paginated list of issues.
    
    Used in: GET /api/projects/{id}/issues
    
    Example response:
        {
            "issues": [...],
            "total": 42,
            "page": 1,
            "page_size": 20
        }
    """
    issues: list[IssueResponse]
    total: int
    page: int = 1
    page_size: int = 20