"""
FastAPI dependencies for authentication and authorization.

These functions are used as dependencies in route handlers to:
- Extract and validate JWT tokens
- Get the current logged-in user
- Check if user has required permissions
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.project import ProjectMember, ProjectRole
from app.core.security import decode_access_token

# HTTP Bearer token scheme for Swagger docs
# This makes the "Authorize" button appear in FastAPI docs
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the currently authenticated user from JWT token.
    
    Flow:
        1. Extract token from Authorization header: "Bearer <token>"
        2. Decode and verify token
        3. Look up user in database by email
        4. Return user object
        
    Args:
        credentials: Automatically extracted from "Authorization: Bearer <token>" header
        db: Database session
        
    Returns:
        User object of the authenticated user
        
    Raises:
        HTTPException 401: If token is invalid or user not found
        
    Example usage in a route:
        @app.get("/api/me")
        def get_profile(current_user: User = Depends(get_current_user)):
            return {"name": current_user.name, "email": current_user.email}
    """
    # Extract token from "Bearer <token>"
    token = credentials.credentials
    
    # Decode token to get user email
    email = decode_access_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Look up user in database
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_project_member(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectMember:
    """
    Verify that current user is a member of the specified project.
    
    Args:
        project_id: ID of the project to check
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        ProjectMember object (contains user's role in project)
        
    Raises:
        HTTPException 403: If user is not a member of the project
        
    Example usage:
        @app.get("/api/projects/{project_id}/issues")
        def get_issues(
            project_id: int,
            member: ProjectMember = Depends(get_project_member)
        ):
            # User is guaranteed to be a project member here
            # Can check member.role for permissions
            ...
    """
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )
    
    return member


def require_maintainer(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectMember:
    """
    Verify that current user is a MAINTAINER of the specified project.
    
    Args:
        project_id: ID of the project to check
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        ProjectMember object with MAINTAINER role
        
    Raises:
        HTTPException 403: If user is not a maintainer
        
    Example usage:
        @app.patch("/api/issues/{issue_id}")
        def update_issue(
            issue_id: int,
            maintainer: ProjectMember = Depends(require_maintainer)
        ):
            # User is guaranteed to be a maintainer here
            # Can perform privileged operations
            ...
    """
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project"
        )
    
    if member.role != ProjectRole.MAINTAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project maintainers can perform this action"
        )
    
    return member