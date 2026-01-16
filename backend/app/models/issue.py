from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class IssueStatus(str, enum.Enum):
    """
    Issue lifecycle states.
    OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED
    """
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IssuePriority(str, enum.Enum):
    """
    Issue priority levels for sorting and filtering.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Issue(Base):
    """
    Issue model - represents a bug, task, or feature request.
    
    Attributes:
        id: Primary key
        project_id: Which project this issue belongs to
        title: Short summary (e.g., "Login button not working")
        description: Detailed explanation, steps to reproduce, etc.
        status: Current state (open, in_progress, resolved, closed)
        priority: Urgency level (low, medium, high, critical)
        reporter_id: User who created this issue
        assignee_id: User responsible for fixing (can be NULL if unassigned)
        created_at: When the issue was created
        updated_at: Last modification time (auto-updates on any change)
        
    Relationships:
        project: The project this issue belongs to
        reporter: User who reported this issue
        assignee: User assigned to fix this issue (optional)
        comments: All comments on this issue
        
    Business Rules:
        - Only project members can create issues
        - Only maintainers can assign/reassign issues
        - Reporter can edit their own issues
        - Maintainers can edit any issue in their project
    """
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(IssueStatus), nullable=False, default=IssueStatus.OPEN, index=True)  # Index for filtering
    priority = Column(Enum(IssuePriority), nullable=False, default=IssuePriority.MEDIUM, index=True)
    
    # Reporter is required (who filed the bug?)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Assignee is optional (unassigned issues are valid)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="issues")
    reporter = relationship("User", back_populates="reported_issues", foreign_keys=[reporter_id])
    assignee = relationship("User", back_populates="assigned_issues", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")