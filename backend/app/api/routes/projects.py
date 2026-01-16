"""
Project management routes.

Endpoints:
    POST /api/projects              - Create a new project
    GET  /api/projects              - List all projects user belongs to
    GET  /api/projects/{id}         - Get project details with members
    POST /api/projects/{id}/members - Add a member to project (maintainers only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectMember, ProjectRole
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectDetailResponse,
    ProjectMemberAdd,
    ProjectMemberResponse
)
from app.core.deps import get_current_user, require_maintainer

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project. Creator automatically becomes a MAINTAINER.
    
    Process:
        1. Check if project key is unique
        2. Create project
        3. Add creator as maintainer
        
    Args:
        project_data: ProjectCreate schema with name, key, description
        current_user: Authenticated user (will be project maintainer)
        db: Database session
        
    Returns:
        ProjectResponse: Created project data
        
    Raises:
        400 Bad Request: If project key already exists
        
    Example:
        POST /api/projects
        Headers: Authorization: Bearer <token>
        {
            "name": "Backend API",
            "key": "API",
            "description": "REST API for IssueHub"
        }
        
        Response 201:
        {
            "id": 1,
            "name": "Backend API",
            "key": "API",
            "description": "REST API for IssueHub",
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    # Check if project key already exists (must be unique)
    existing_project = db.query(Project).filter(Project.key == project_data.key).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project key '{project_data.key}' already exists"
        )
    
    # Create project
    db_project = Project(
        name=project_data.name,
        key=project_data.key,
        description=project_data.description
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Add creator as maintainer
    project_member = ProjectMember(
        project_id=db_project.id,
        user_id=current_user.id,
        role=ProjectRole.MAINTAINER
    )
    db.add(project_member)
    db.commit()
    
    return db_project


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all projects that the current user belongs to (as member or maintainer).
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List[ProjectResponse]: List of projects
        
    Example:
        GET /api/projects
        Headers: Authorization: Bearer <token>
        
        Response 200:
        [
            {
                "id": 1,
                "name": "Backend API",
                "key": "API",
                "description": "REST API for IssueHub",
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "name": "Frontend App",
                "key": "FE",
                "description": "React frontend",
                "created_at": "2024-01-16T09:00:00Z"
            }
        ]
    """
    # Get all projects where user is a member
    projects = db.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).all()
    
    return projects


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed project information including all members.
    
    Permissions: Must be a project member
    
    Args:
        project_id: Project ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ProjectDetailResponse: Project with members list
        
    Raises:
        403 Forbidden: If user is not a project member
        404 Not Found: If project doesn't exist
        
    Example:
        GET /api/projects/1
        Headers: Authorization: Bearer <token>
        
        Response 200:
        {
            "id": 1,
            "name": "Backend API",
            "key": "API",
            "description": "REST API for IssueHub",
            "created_at": "2024-01-15T10:30:00Z",
            "members": [
                {
                    "user": {
                        "id": 1,
                        "name": "Alice Johnson",
                        "email": "alice@example.com",
                        "created_at": "2024-01-10T08:00:00Z"
                    },
                    "role": "maintainer"
                },
                {
                    "user": {
                        "id": 2,
                        "name": "Bob Smith",
                        "email": "bob@example.com",
                        "created_at": "2024-01-11T09:00:00Z"
                    },
                    "role": "member"
                }
            ]
        }
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is a member
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )
    
    return project


@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: int,
    member_data: ProjectMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new member to a project.
    
    Permissions: Only project MAINTAINERS can add members
    
    Process:
        1. Verify requester is a maintainer
        2. Find user by email
        3. Check if already a member
        4. Add to project with specified role
        
    Args:
        project_id: Project ID
        member_data: ProjectMemberAdd schema with email and role
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ProjectMemberResponse: Added member info
        
    Raises:
        403 Forbidden: If requester is not a maintainer
        404 Not Found: If user with email not found
        400 Bad Request: If user is already a member
    """
    # First, check if current user is a maintainer
    requester_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not requester_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )
    
    if requester_member.role != ProjectRole.MAINTAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project maintainers can add members"
        )
    
    # Find user by email
    user = db.query(User).filter(User.email == member_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{member_data.email}' not found"
        )
    
    # Check if user is already a member
    existing_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )
    
    # Add user to project
    new_member = ProjectMember(
        project_id=project_id,
        user_id=user.id,
        role=member_data.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return new_member