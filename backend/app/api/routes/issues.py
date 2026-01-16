"""
Issue management routes.

Endpoints:
    GET    /api/projects/{project_id}/issues - List issues with filtering/sorting
    POST   /api/projects/{project_id}/issues - Create a new issue
    GET    /api/issues/{issue_id}            - Get issue details
    PATCH  /api/issues/{issue_id}            - Update an issue
    DELETE /api/issues/{issue_id}            - Delete an issue
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from app.database import get_db
from app.models.user import User
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.project import ProjectMember, ProjectRole
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse, IssueListResponse
from app.core.deps import get_current_user, get_project_member

router = APIRouter()


@router.get("/projects/{project_id}/issues", response_model=IssueListResponse)
def list_issues(
    project_id: int,
    q: Optional[str] = Query(None, description="Search in title and description"),
    status: Optional[IssueStatus] = Query(None, description="Filter by status"),
    priority: Optional[IssuePriority] = Query(None, description="Filter by priority"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee user ID"),
    sort: Optional[str] = Query("created_at", description="Sort by: created_at, priority, status, updated_at"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    member: ProjectMember = Depends(get_project_member),
    db: Session = Depends(get_db)
):
    """
    List all issues in a project with filtering, search, sorting, and pagination.
    
    Permissions: Must be a project member
    
    Query Parameters:
        - q: Search text (searches title and description)
        - status: Filter by status (open, in_progress, resolved, closed)
        - priority: Filter by priority (low, medium, high, critical)
        - assignee_id: Filter by assigned user ID
        - sort: Sort field (created_at, priority, status, updated_at)
        - page: Page number (default: 1)
        - page_size: Items per page (default: 20, max: 100)
        
    Args:
        project_id: Project ID
        member: Project member (injected, ensures user has access)
        db: Database session
        
    Returns:
        IssueListResponse: Paginated list of issues
        
    Example:
        GET /api/projects/1/issues?status=open&priority=high&sort=priority&page=1
        Headers: Authorization: Bearer <token>
        
        Response 200:
        {
            "issues": [
                {
                    "id": 1,
                    "project_id": 1,
                    "title": "Critical bug in login",
                    "description": "...",
                    "status": "open",
                    "priority": "high",
                    "reporter": {...},
                    "assignee": {...},
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            ],
            "total": 42,
            "page": 1,
            "page_size": 20
        }
    """
    # Start with base query
    query = db.query(Issue).filter(Issue.project_id == project_id)
    
    # Apply search filter (search in title and description)
    if q:
        search_filter = or_(
            Issue.title.ilike(f"%{q}%"),
            Issue.description.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
    
    # Apply status filter
    if status:
        query = query.filter(Issue.status == status)
    
    # Apply priority filter
    if priority:
        query = query.filter(Issue.priority == priority)
    
    # Apply assignee filter
    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)
    
    # Apply sorting
    if sort == "created_at":
        query = query.order_by(Issue.created_at.desc())
    elif sort == "updated_at":
        query = query.order_by(Issue.updated_at.desc())
    elif sort == "priority":
        # Sort by priority: critical > high > medium > low
        priority_order = {
            IssuePriority.CRITICAL: 0,
            IssuePriority.HIGH: 1,
            IssuePriority.MEDIUM: 2,
            IssuePriority.LOW: 3
        }
        query = query.order_by(Issue.priority)
    elif sort == "status":
        query = query.order_by(Issue.status)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    issues = query.offset(offset).limit(page_size).all()
    
    return {
        "issues": issues,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/projects/{project_id}/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    project_id: int,
    issue_data: IssueCreate,
    current_user: User = Depends(get_current_user),
    member: ProjectMember = Depends(get_project_member),
    db: Session = Depends(get_db)
):
    """
    Create a new issue in a project.
    
    Permissions: Must be a project member
    
    Process:
        1. Verify assignee (if provided) is a project member
        2. Create issue with current user as reporter
        3. Default status is "open"
        
    Args:
        project_id: Project ID
        issue_data: IssueCreate schema
        current_user: Authenticated user (becomes reporter)
        member: Project member validation (injected)
        db: Database session
        
    Returns:
        IssueResponse: Created issue
        
    Raises:
        400 Bad Request: If assignee is not a project member
        
    Example:
        POST /api/projects/1/issues
        Headers: Authorization: Bearer <token>
        {
            "title": "Login button not responding",
            "description": "When clicking login, nothing happens",
            "priority": "high",
            "assignee_id": 2
        }
        
        Response 201:
        {
            "id": 1,
            "project_id": 1,
            "title": "Login button not responding",
            "description": "When clicking login, nothing happens",
            "status": "open",
            "priority": "high",
            "reporter": {...},
            "assignee": {...},
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    """
    # If assignee is specified, verify they are a project member
    if issue_data.assignee_id:
        assignee_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == issue_data.assignee_id
        ).first()
        
        if not assignee_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a project member"
            )
    
    # Create issue
    db_issue = Issue(
        project_id=project_id,
        title=issue_data.title,
        description=issue_data.description,
        priority=issue_data.priority,
        reporter_id=current_user.id,  # Current user is the reporter
        assignee_id=issue_data.assignee_id,
        status=IssueStatus.OPEN  # Default status
    )
    
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    
    return db_issue


@router.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific issue.
    
    Permissions: Must be a member of the issue's project
    
    Args:
        issue_id: Issue ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        IssueResponse: Issue details
        
    Raises:
        404 Not Found: If issue doesn't exist
        403 Forbidden: If user is not a project member
        
    Example:
        GET /api/issues/1
        Headers: Authorization: Bearer <token>
        
        Response 200:
        {
            "id": 1,
            "project_id": 1,
            "title": "Login button not responding",
            ...
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
    
    return issue


@router.patch("/issues/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an issue (partial update).
    
    Permissions:
        - Reporter: Can update title, description
        - Maintainer: Can update all fields (status, priority, assignee)
        
    Args:
        issue_id: Issue ID
        issue_update: IssueUpdate schema (all fields optional)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        IssueResponse: Updated issue
        
    Raises:
        404 Not Found: If issue doesn't exist
        403 Forbidden: If user lacks permission
        
    Example:
        PATCH /api/issues/1
        Headers: Authorization: Bearer <token>
        {
            "status": "in_progress",
            "assignee_id": 3
        }
        
        Response 200:
        {
            "id": 1,
            "status": "in_progress",
            "assignee_id": 3,
            ...
        }
    """
    # Get issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check project membership
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this issue"
        )
    
    # Determine what user can update based on role
    is_reporter = issue.reporter_id == current_user.id
    is_maintainer = member.role == ProjectRole.MAINTAINER
    
    # Update fields based on permissions
    update_data = issue_update.dict(exclude_unset=True)  # Only fields that were provided
    
    for field, value in update_data.items():
        # Reporter can only update title and description
        if field in ["title", "description"]:
            if is_reporter or is_maintainer:
                setattr(issue, field, value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the reporter or maintainers can update this field"
                )
        # Only maintainers can update status, priority, assignee
        elif field in ["status", "priority", "assignee_id"]:
            if is_maintainer:
                setattr(issue, field, value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only maintainers can update status, priority, or assignee"
                )
    
    db.commit()
    db.refresh(issue)
    
    return issue


@router.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an issue.
    
    Permissions: Only project MAINTAINERS can delete issues
    
    Args:
        issue_id: Issue ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        204 No Content (empty response)
        
    Raises:
        404 Not Found: If issue doesn't exist
        403 Forbidden: If user is not a maintainer
        
    Example:
        DELETE /api/issues/1
        Headers: Authorization: Bearer <token>
        
        Response 204: (no content)
    """
    # Get issue
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )
    
    # Check if user is a maintainer
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == issue.project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member or member.role != ProjectRole.MAINTAINER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project maintainers can delete issues"
        )
    
    # Delete issue (cascade will delete comments)
    db.delete(issue)
    db.commit()
    
    return None