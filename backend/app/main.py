"""
FastAPI main application entry point.

This file:
- Initializes the FastAPI app
- Configures CORS (Cross-Origin Resource Sharing) for frontend
- Registers all API routes
- Provides root endpoint and health check
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, projects, issues, comments

# Create FastAPI application instance
app = FastAPI(
    title="IssueHub API",
    description="A lightweight bug tracker for teams to manage projects and issues",
    version="1.0.0",
    docs_url="/api/docs",  # Swagger UI at /api/docs
    redoc_url="/api/redoc"  # ReDoc at /api/redoc
)

# Configure CORS - allows frontend (React) to communicate with backend
# In production, replace "*" with your actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # Add your production frontend URL here when deploying
    ],
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Root endpoint - simple welcome message
@app.get("/")
def read_root():
    """
    Root endpoint - provides API information.
    
    Example:
        GET /
        
        Response 200:
        {
            "message": "Welcome to IssueHub API",
            "docs": "/api/docs",
            "version": "1.0.0"
        }
    """
    return {
        "message": "Welcome to IssueHub API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }


# Health check endpoint - useful for monitoring and deployment
@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    
    Example:
        GET /health
        
        Response 200:
        {
            "status": "healthy"
        }
    """
    return {"status": "healthy"}


# Register API routes with prefixes and tags (for organized docs)

# Authentication routes: /api/auth/*
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# Project routes: /api/projects/*
app.include_router(
    projects.router,
    prefix="/api/projects",
    tags=["Projects"]
)

# Issue routes: /api/issues/* and /api/projects/{id}/issues
app.include_router(
    issues.router,
    prefix="/api",
    tags=["Issues"]
)

# Comment routes: /api/issues/{id}/comments
app.include_router(
    comments.router,
    prefix="/api",
    tags=["Comments"]
)


# Run the application
# This is only used when running directly with `python app/main.py`
# In production, use: uvicorn app.main:app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True  # Auto-reload on code changes (dev only!)
    )