"""
Tests for projects and issues endpoints.
Tests CRUD operations, permissions, and filtering.
"""

import pytest


@pytest.fixture
def test_project(db, test_user):
    """Create a test project with test user as maintainer."""
    from app.models.project import Project, ProjectMember, ProjectRole
    
    project = Project(
        name="Test Project",
        key="TEST",
        description="A test project"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    member = ProjectMember(
        project_id=project.id,
        user_id=test_user["id"],
        role=ProjectRole.MAINTAINER
    )
    db.add(member)
    db.commit()
    
    return project


@pytest.fixture
def second_user(db):
    """Create a second test user."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        name="Second User",
        email="second@example.com",
        password_hash=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==================== PROJECT TESTS ====================

def test_create_project(client, auth_headers):
    """Test creating a new project."""
    response = client.post(
        "/api/projects",
        headers=auth_headers,
        json={
            "name": "New Project",
            "key": "NEW",
            "description": "Project description"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["key"] == "NEW"
    assert data["description"] == "Project description"


def test_create_project_duplicate_key(client, auth_headers, test_project):
    """Test creating project with duplicate key fails."""
    response = client.post(
        "/api/projects",
        headers=auth_headers,
        json={
            "name": "Another Project",
            "key": test_project.key,  # Duplicate key
            "description": "Description"
        }
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_list_projects(client, auth_headers, test_project):
    """Test listing user's projects."""
    response = client.get("/api/projects", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == test_project.id


def test_get_project_detail(client, auth_headers, test_project):
    """Test getting project details with members."""
    response = client.get(
        f"/api/projects/{test_project.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name
    assert "members" in data


def test_add_project_member(client, auth_headers, test_project, second_user):
    """Test adding a member to project (maintainer only)."""
    response = client.post(
        f"/api/projects/{test_project.id}/members",
        headers=auth_headers,
        json={
            "email": second_user.email,
            "role": "member"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == second_user.email
    assert data["role"] == "member"


def test_add_member_nonexistent_user(client, auth_headers, test_project):
    """Test adding non-existent user fails."""
    response = client.post(
        f"/api/projects/{test_project.id}/members",
        headers=auth_headers,
        json={
            "email": "nobody@example.com",
            "role": "member"
        }
    )
    
    assert response.status_code == 404