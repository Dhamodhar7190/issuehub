"""
Pydantic schemas for Project-related API requests and responses.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserResponse
from app.models.project import ProjectRole


class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.
    
    Used in: POST /api/projects
    
    Example request:
        {
            "name": "Backend API",
            "key": "API",
            "description": "REST API for IssueHub"
        }
        
    Note: Project creator automatically becomes a MAINTAINER
    """
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    key: str = Field(..., min_length=2, max_length=10, description="Project key (e.g., 'API' for API-1, API-2)")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")


class ProjectMemberAdd(BaseModel):
    """
    Schema for adding a member to a project.
    
    Used in: POST /api/projects/{id}/members
    
    Example request:
        {
            "email": "bob@example.com",
            "role": "member"
        }
        
    Note: Only MAINTAINERS can add members
    """
    email: str = Field(..., description="Email of user to add")
    role: ProjectRole = Field(default=ProjectRole.MEMBER, description="Role: 'member' or 'maintainer'")


class ProjectMemberResponse(BaseModel):
    """
    Schema for project member information in responses.
    
    Example:
        {
            "user": {
                "id": 2,
                "name": "Bob Smith",
                "email": "bob@example.com",
                "created_at": "2024-01-10T08:00:00Z"
            },
            "role": "member"
        }
    """
    user: UserResponse
    role: ProjectRole

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    """
    Schema for project data in API responses.
    
    Used in: GET /api/projects, GET /api/projects/{id}
    
    Example response:
        {
            "id": 1,
            "name": "Backend API",
            "key": "API",
            "description": "REST API for IssueHub",
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    id: int
    name: str
    key: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """
    Schema for detailed project information including members.
    
    Used in: GET /api/projects/{id} (when detailed view is needed)
    
    Example response:
        {
            "id": 1,
            "name": "Backend API",
            "key": "API",
            "description": "REST API for IssueHub",
            "created_at": "2024-01-15T10:30:00Z",
            "members": [
                {
                    "user": {"id": 1, "name": "Alice", ...},
                    "role": "maintainer"
                },
                {
                    "user": {"id": 2, "name": "Bob", ...},
                    "role": "member"
                }
            ]
        }
    """
    members: List[ProjectMemberResponse] = []

    class Config:
        from_attributes = True