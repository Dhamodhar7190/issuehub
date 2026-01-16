"""
API routes package.

Imports all route modules for easy registration in main app.
"""

from app.api.routes import auth, projects, issues, comments

__all__ = ["auth", "projects", "issues", "comments"]