"""
Seed script to populate database with demo data.

Creates:
- 3 users (Alice, Bob, Charlie)
- 2 projects (Backend API, Frontend App)
- 10-15 issues with various statuses
- Several comments

Run with: python seed.py
"""

from app.database import SessionLocal
from app.models.user import User
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.issue import Issue, IssueStatus, IssuePriority
from app.models.comment import Comment
from app.core.security import get_password_hash

def seed_database():
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # Create users
        print("Creating users...")
        alice = User(
            name="Alice Johnson",
            email="alice@example.com",
            password_hash=get_password_hash("password123")
        )
        bob = User(
            name="Bob Smith",
            email="bob@example.com",
            password_hash=get_password_hash("password123")
        )
        charlie = User(
            name="Charlie Davis",
            email="charlie@example.com",
            password_hash=get_password_hash("password123")
        )
        
        db.add_all([alice, bob, charlie])
        db.commit()
        db.refresh(alice)
        db.refresh(bob)
        db.refresh(charlie)
        print(f"✅ Created 3 users")
        
        # Create projects
        print("Creating projects...")
        backend_project = Project(
            name="Backend API",
            key="API",
            description="REST API for IssueHub"
        )
        frontend_project = Project(
            name="Frontend App",
            key="FE",
            description="React frontend application"
        )
        
        db.add_all([backend_project, frontend_project])
        db.commit()
        db.refresh(backend_project)
        db.refresh(frontend_project)
        print(f"✅ Created 2 projects")
        
        # Add project members
        print("Adding project members...")
        members = [
            ProjectMember(project_id=backend_project.id, user_id=alice.id, role=ProjectRole.MAINTAINER),
            ProjectMember(project_id=backend_project.id, user_id=bob.id, role=ProjectRole.MEMBER),
            ProjectMember(project_id=frontend_project.id, user_id=alice.id, role=ProjectRole.MEMBER),
            ProjectMember(project_id=frontend_project.id, user_id=charlie.id, role=ProjectRole.MAINTAINER),
        ]
        db.add_all(members)
        db.commit()
        print(f"✅ Added project members")
        
        # Create issues
        print("Creating issues...")
        issues = [
            # Backend issues
            Issue(
                project_id=backend_project.id,
                title="Login endpoint returns 500 error",
                description="When posting invalid credentials, should return 401 but returns 500",
                status=IssueStatus.OPEN,
                priority=IssuePriority.HIGH,
                reporter_id=bob.id,
                assignee_id=alice.id
            ),
            Issue(
                project_id=backend_project.id,
                title="Add pagination to issues list",
                description="Currently returns all issues, need to add page/limit parameters",
                status=IssueStatus.IN_PROGRESS,
                priority=IssuePriority.MEDIUM,
                reporter_id=alice.id,
                assignee_id=alice.id
            ),
            Issue(
                project_id=backend_project.id,
                title="JWT tokens expire too quickly",
                description="30 minutes is too short, should be at least 2 hours",
                status=IssueStatus.RESOLVED,
                priority=IssuePriority.LOW,
                reporter_id=bob.id,
                assignee_id=alice.id
            ),
            Issue(
                project_id=backend_project.id,
                title="Database connection pool exhausted",
                description="Under heavy load, running out of database connections",
                status=IssueStatus.OPEN,
                priority=IssuePriority.CRITICAL,
                reporter_id=alice.id,
                assignee_id=None
            ),
            Issue(
                project_id=backend_project.id,
                title="Add input validation for email field",
                description="Need to validate email format before saving to database",
                status=IssueStatus.OPEN,
                priority=IssuePriority.MEDIUM,
                reporter_id=bob.id,
                assignee_id=None
            ),
            # Frontend issues
            Issue(
                project_id=frontend_project.id,
                title="Login button not centered on mobile",
                description="Button alignment is off on screens smaller than 768px",
                status=IssueStatus.OPEN,
                priority=IssuePriority.LOW,
                reporter_id=charlie.id,
                assignee_id=None
            ),
            Issue(
                project_id=frontend_project.id,
                title="Issue list doesn't update after creating issue",
                description="Need to refresh page to see newly created issues",
                status=IssueStatus.IN_PROGRESS,
                priority=IssuePriority.HIGH,
                reporter_id=alice.id,
                assignee_id=charlie.id
            ),
            Issue(
                project_id=frontend_project.id,
                title="Add loading spinners",
                description="Show loading state when fetching data from API",
                status=IssueStatus.RESOLVED,
                priority=IssuePriority.MEDIUM,
                reporter_id=charlie.id,
                assignee_id=charlie.id
            ),
            Issue(
                project_id=frontend_project.id,
                title="Implement dark mode",
                description="Add toggle for dark/light theme preference",
                status=IssueStatus.OPEN,
                priority=IssuePriority.LOW,
                reporter_id=alice.id,
                assignee_id=None
            ),
            Issue(
                project_id=frontend_project.id,
                title="Add toast notifications",
                description="Show success/error messages for user actions",
                status=IssueStatus.CLOSED,
                priority=IssuePriority.HIGH,
                reporter_id=charlie.id,
                assignee_id=charlie.id
            ),
        ]
        
        db.add_all(issues)
        db.commit()
        
        # Refresh to get IDs
        for issue in issues:
            db.refresh(issue)
        
        print(f"✅ Created {len(issues)} issues")
        
        # Create comments
        print("Creating comments...")
        comments = [
            Comment(
                issue_id=issues[0].id,
                author_id=alice.id,
                body="I'll look into this today. Probably missing error handling."
            ),
            Comment(
                issue_id=issues[0].id,
                author_id=bob.id,
                body="Thanks! It's blocking our testing."
            ),
            Comment(
                issue_id=issues[1].id,
                author_id=alice.id,
                body="Working on this now. Will use standard page/page_size params."
            ),
            Comment(
                issue_id=issues[6].id,
                author_id=charlie.id,
                body="I think we need to invalidate the cache after POST requests."
            ),
            Comment(
                issue_id=issues[6].id,
                author_id=alice.id,
                body="Good point! I'll add that to the fix."
            ),
            Comment(
                issue_id=issues[9].id,
                author_id=charlie.id,
                body="Completed! Toast notifications are now working across the app."
            ),
        ]
        
        db.add_all(comments)
        db.commit()
        print(f"✅ Created {len(comments)} comments")
        
        print("\n🎉 Database seeded successfully!")
        print("\n📝 Demo Credentials:")
        print("   Email: alice@example.com | Password: password123 (Backend Maintainer)")
        print("   Email: bob@example.com | Password: password123 (Backend Member)")
        print("   Email: charlie@example.com | Password: password123 (Frontend Maintainer)")
        print("\n🚀 You can now login with any of these accounts!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()