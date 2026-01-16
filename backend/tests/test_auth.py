"""
Authentication endpoint tests.
Tests for signup, login, and user profile endpoints.
"""

def test_signup_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "password" not in data
    assert "id" in data


def test_signup_duplicate_email(client, test_user):
    """Test signup fails with duplicate email."""
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "Another User",
            "email": test_user["email"],
            "password": "password123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_signup_invalid_email(client):
    """Test signup validation catches invalid email."""
    response = client.post(
        "/api/auth/signup",
        json={
            "name": "Test",
            "email": "not-an-email",
            "password": "password123"
        }
    )
    
    assert response.status_code == 422


def test_login_success(client, test_user):
    """Test successful login returns JWT token."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login fails with incorrect password."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login fails for non-existent user."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Test authenticated user can get their profile."""
    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


def test_get_current_user_no_auth(client):
    """Test getting profile without token fails."""
    response = client.get("/api/auth/me")
    assert response.status_code == 403


def test_get_current_user_invalid_token(client):
    """Test getting profile with invalid token fails."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401