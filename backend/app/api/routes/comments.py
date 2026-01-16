"""
Comment management routes.

Endpoints:
    GET  /api/issues/{issue_id}/comments - List all comments on an issue
    POST /api/issues/{issue_id}/comments - Add a comment to an issue
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.issue import Issue
from app.models.comment import Comment
from app.models.project import ProjectMember
from app.schemas.comment import CommentCreate, CommentResponse
from app.core.deps import get_current_user

router = APIRouter()


@router.get("/issues/{issue_id}/comments", response_model=List[CommentResponse])
def list_comments(
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all comments on an issue, ordered by creation time (oldest first).
    
    Permissions: Must be a member of the issue's project
    
    Args:
        issue_id: Issue ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List[CommentResponse]: List of comments
        
    Raises:
        404 Not Found: If issue doesn't exist
        403 Forbidden: If user is not a project member
        
    Example:
        GET /api/issues/1/comments
        Headers: Authorization: Bearer <token>
        
        Response 200:
        [
            {
                "id": 1,
                "issue_id": 1,
                "author": {
                    "id": 2,
                    "name": "Bob Smith",
                    "email": "bob@example.com",
                    "created_at": "2024-01-11T09:00:00Z"
                },
                "body": "I'm experiencing the same issue on Chrome 120",
                "created_at": "2024-01-15T11:00:00Z"
            },
            {
                "id": 2,
                "issue_id": 1,
                "author": {
                    "id": 1,
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "created_at": "2024-01-10T08:00:00Z"
                },
                "body": "Thanks for reporting! Looking into this now.",
                "created_at": "2024-01-15T11:30:00Z"
            }
        ]
    """
    # Get issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user is a member of the issue's project
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this issue"
        )
    
    # Get comments ordered by creation time (oldest first, like a conversation)
    comments = db.query(Comment).filter(
        Comment.issue_id == issue_id
    ).order_by(Comment.created_at.asc()).all()
    
    return comments


@router.post("/issues/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    issue_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new comment to an issue.
    
    Permissions: Must be a member of the issue's project
    
    Args:
        issue_id: Issue ID
        comment_data: CommentCreate schema with body text
        current_user: Authenticated user (becomes comment author)
        db: Database session
        
    Returns:
        CommentResponse: Created comment
        
    Raises:
        404 Not Found: If issue doesn't exist
        403 Forbidden: If user is not a project member
        
    Example:
        POST /api/issues/1/comments
        Headers: Authorization: Bearer <token>
        {
            "body": "I've fixed this issue. Deploying now."
        }
        
        Response 201:
        {
            "id": 3,
            "issue_id": 1,
            "author": {
                "id": 1,
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "created_at": "2024-01-10T08:00:00Z"
            },
            "body": "I've fixed this issue. Deploying now.",
            "created_at": "2024-01-15T16:45:00Z"
        }
    """
    # Get issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user is a member of the issue's project
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this issue"
        )
    
    # Create comment
    db_comment = Comment(
        issue_id=issue_id,
        author_id=current_user.id,
        body=comment_data.body
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment