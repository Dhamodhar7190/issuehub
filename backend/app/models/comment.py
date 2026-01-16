from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Comment(Base):
    """
    Comment model - represents a comment/discussion on an issue.
    
    Attributes:
        id: Primary key
        issue_id: Which issue this comment belongs to
        author_id: User who wrote this comment
        body: The comment text content
        created_at: When the comment was posted
        
    Relationships:
        issue: The issue this comment is attached to
        author: User who wrote this comment
        
    Business Rules:
        - Only project members can comment on issues
        - Users can edit/delete their own comments
        - Maintainers can delete any comment in their project
        - Comments cannot be empty
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body = Column(Text, nullable=False)  # Comment content
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")