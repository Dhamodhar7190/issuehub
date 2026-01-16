"""
Security utilities for authentication and authorization.

Handles:
- Password hashing (bcrypt) - never store plain passwords!
- Password verification
- JWT token creation and validation
- Token payload structure
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Password hashing context using bcrypt
# bcrypt is slow by design - makes brute force attacks impractical
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The password user entered (e.g., "mypassword123")
        hashed_password: The bcrypt hash from database (e.g., "$2b$12$...")
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> stored_hash = "$2b$12$abcd..."  # From database
        >>> verify_password("correct", stored_hash)  # Returns True
        >>> verify_password("wrong", stored_hash)    # Returns False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Bcrypt hashed password string
        
    Example:
        >>> get_password_hash("mypassword123")
        "$2b$12$KIXxKj9V.../hashed_string..."
        
    Note:
        - Same password will generate different hashes each time (bcrypt uses salt)
        - This is intentional and secure
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for authentication.
    
    Args:
        data: Dictionary to encode in token (usually {"sub": user_email})
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
        
    Token Structure:
        {
            "sub": "user@example.com",  # Subject (user identifier)
            "exp": 1234567890            # Expiration timestamp
        }
        
    Example:
        >>> token = create_access_token({"sub": "alice@example.com"})
        >>> # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        
    Security:
        - Token is signed with SECRET_KEY from settings
        - Cannot be modified without secret
        - Expires after ACCESS_TOKEN_EXPIRE_MINUTES (default: 30 minutes)
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and verify a JWT token, extracting the user email.
    
    Args:
        token: JWT token string
        
    Returns:
        User email (subject) if token is valid, None otherwise
        
    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> decode_access_token(token)
        "alice@example.com"
        
    Returns None if:
        - Token is expired
        - Token signature is invalid
        - Token is malformed
        - Subject (email) is missing
    """
    try:
        # Decode and verify token signature
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            return None
            
        return email
        
    except JWTError:
        # Token is invalid, expired, or malformed
        return None