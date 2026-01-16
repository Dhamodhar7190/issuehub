"""
Authentication routes for user signup, login, and profile management.

Endpoints:
    POST /api/auth/signup - Register a new user
    POST /api/auth/login  - Login and get JWT token
    GET  /api/me          - Get current user profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Process:
        1. Check if email already exists
        2. Hash the password (never store plain passwords!)
        3. Create user in database
        4. Return user data (without password!)
        
    Args:
        user_data: UserCreate schema with name, email, password
        db: Database session (injected)
        
    Returns:
        UserResponse: Created user data
        
    Raises:
        400 Bad Request: If email already registered
        
    Example:
        POST /api/auth/signup
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "password": "SecurePass123!"
        }
        
        Response 201:
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)  # Hash password!
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Get the ID and created_at from database
    
    return db_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password to get JWT access token.
    
    Process:
        1. Look up user by email
        2. Verify password
        3. Generate JWT token
        4. Return token
        
    Args:
        credentials: UserLogin schema with email, password
        db: Database session (injected)
        
    Returns:
        TokenResponse: JWT access token
        
    Raises:
        401 Unauthorized: If email not found or password incorrect
        
    Example:
        POST /api/auth/login
        {
            "email": "alice@example.com",
            "password": "SecurePass123!"
        }
        
        Response 200:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        
    Frontend usage:
        1. Store token in memory or sessionStorage
        2. Include in requests: Authorization: Bearer <token>
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token with user email as subject
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    
    Requires: Valid JWT token in Authorization header
    
    Args:
        current_user: Injected from JWT token via get_current_user dependency
        
    Returns:
        UserResponse: Current user's profile data
        
    Example:
        GET /api/me
        Headers: Authorization: Bearer <token>
        
        Response 200:
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    return current_user