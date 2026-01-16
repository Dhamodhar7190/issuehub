from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        name: User's display name
        email: Unique email for login (used as username)
        password_hash: Bcrypt hashed password (never store plain passwords!)
        created_at: Timestamp when user account was created
        
    Relationships:
        reported_issues: All issues this user has reported
        assigned_issues: All issues assigned to this user
        comments: All comments authored by this user
        project_memberships: Link to projects this user belongs to
    """
    __tablename__ = "users"

    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)  # Index for fast login lookups
    password_hash = Column(String, nullable=False)  # Hashed with bcrypt
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships - SQLAlchemy will handle the joins
    reported_issues = relationship("Issue", back_populates="reporter", foreign_keys="Issue.reporter_id")
    assigned_issues = relationship("Issue", back_populates="assignee", foreign_keys="Issue.assignee_id")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")