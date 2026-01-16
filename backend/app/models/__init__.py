"""
Models package - contains all SQLAlchemy database models.

Import order matters! Base must be imported first, then models in dependency order.
"""
from app.database import Base
from app.models.user import User
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.comment import Comment

# Export all models for easy importing
__all__ = [
    "Base",
    "User",
    "Project",
    "ProjectMember",
    "ProjectRole",
    "Issue",
    "IssueStatus",
    "IssuePriority",
    "Comment"
]