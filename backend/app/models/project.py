from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class ProjectRole(str, enum.Enum):
    """
    Enum for project member roles.
    - MEMBER: Can view and create issues, comment
    - MAINTAINER: Full control - can assign, close, delete issues, manage members
    """
    MEMBER = "member"
    MAINTAINER = "maintainer"

class Project(Base):
    """
    Project model - represents a container for issues (like a GitHub repo).
    
    Attributes:
        id: Primary key
        name: Project display name (e.g., "IssueHub Frontend")
        key: Short unique identifier (e.g., "IH" -> issues will be IH-1, IH-2)
        description: Optional project description
        created_at: When the project was created
        
    Relationships:
        issues: All issues belonging to this project
        members: Link table to users with their roles
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)  # e.g., "PROJ" for PROJ-1, PROJ-2
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    """
    Junction table linking Users to Projects with roles.
    This is a many-to-many relationship with extra data (role).
    
    Attributes:
        project_id: Foreign key to projects table
        user_id: Foreign key to users table
        role: Either 'member' or 'maintainer'
        
    Example:
        User "Alice" is a MAINTAINER of Project "Backend API"
        User "Bob" is a MEMBER of Project "Backend API"
    """
    __tablename__ = "project_members"

    # Composite primary key (a user can only have one role per project)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(Enum(ProjectRole), nullable=False, default=ProjectRole.MEMBER)

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")