# 🐛 IssueHub - Lightweight Bug Tracker

A modern, full-stack bug tracking application built with FastAPI and React. IssueHub enables teams to efficiently manage projects, track issues, and collaborate through comments with role-based access control.

![IssueHub](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Setup Instructions](#-setup-instructions)
- [Running the Application](#-running-the-application)
- [Running Tests](#-running-tests)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Key Design Decisions](#-key-design-decisions)
- [Known Limitations](#-known-limitations)

## ✨ Features

### Authentication & Authorization
- ✅ User registration and login with JWT authentication
- ✅ Role-based access control (Project Members & Maintainers)
- ✅ Secure password hashing with bcrypt
- ✅ Protected API routes

### Project Management
- ✅ Create and manage multiple projects
- ✅ Invite team members by email
- ✅ Unique project keys for issue identification (e.g., API-1, API-2)
- ✅ Role-based permissions (Member vs Maintainer)

### Issue Tracking
- ✅ Create, read, update, and delete issues
- ✅ Issue states: Open, In Progress, Resolved, Closed
- ✅ Priority levels: Low, Medium, High, Critical
- ✅ Assign issues to team members
- ✅ Advanced filtering by status, priority, and assignee
- ✅ Full-text search in titles and descriptions
- ✅ Sort by creation date, priority, status, or last updated

### Collaboration
- ✅ Comment threads on issues
- ✅ Real-time issue updates
- ✅ Activity tracking with timestamps

### User Experience
- ✅ Clean, responsive Material Design-inspired UI
- ✅ Toast notifications for user feedback
- ✅ Loading states and spinners
- ✅ Form validation
- ✅ Modal dialogs for create/edit operations

## 📸 Screenshots

### SignUp Page
![SignUp](screenshots/signup.png)

### Login Page
![Login](screenshots/login.png)

### Projects Dashboard
![Projects List](screenshots/projects-list.png)

### Issues List with Filters
![Issues List](screenshots/issues-list.png)

### Issue Detail with Comments
![Issue Detail](screenshots/issue-detail.png)

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose) + bcrypt
- **Validation:** Pydantic v2
- **Testing:** Pytest with test fixtures

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Styling:** Custom CSS with CSS Variables
- **State Management:** React Context API

### DevOps & Tools
- **Version Control:** Git
- **API Documentation:** OpenAPI (Swagger UI)
- **CORS:** Configured for local development

## 🏗 Architecture

### Backend Architecture
```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── auth.py      # Authentication routes
│   │       ├── projects.py  # Project management
│   │       ├── issues.py    # Issue CRUD
│   │       └── comments.py  # Comments
│   ├── core/
│   │   ├── security.py      # JWT & password hashing
│   │   └── deps.py          # Dependency injection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── database.py          # DB connection
│   ├── config.py            # Settings
│   └── main.py              # FastAPI app
├── alembic/                 # Database migrations
├── tests/                   # Pytest tests
```

**Design Pattern:** Clean Architecture with clear separation of concerns
- **Routes:** Handle HTTP requests/responses
- **Models:** Database schema definitions
- **Schemas:** Request/response validation
- **Core:** Business logic and utilities

### Frontend Architecture
```
frontend/
├── src/
│   ├── api/                 # API client & services
│   ├── components/          # Reusable components
│   ├── context/             # React Context (Auth, Toast)
│   ├── pages/               # Page components
│   ├── App.jsx              # Root component & routing
│   └── main.jsx             # Entry point
└── public/
```

**Design Pattern:** Component-based architecture with Context API for global state
- **Pages:** Route-level components
- **Components:** Reusable UI elements
- **Context:** Global state (authentication, notifications)
- **API:** Centralized API calls with interceptors

## 📦 Prerequisites

Ensure you have the following installed:

- **Python:** 3.11 or higher
- **Node.js:** 18.x or higher
- **PostgreSQL:** 15 or higher
- **Git:** Latest version

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd issuehub
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/issuehub_db
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ Important:** Change `SECRET_KEY` in production! Generate one with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Setup Database

**Option A: Local PostgreSQL**
```bash
# Create database
psql -U postgres
CREATE DATABASE issuehub_db;
\q
```

**Option B: Docker**
```bash
docker run --name issuehub-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=issuehub_db \
  -p 5432:5432 \
  -d postgres:15
```

#### Run Migrations
```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### (Optional) Seed Demo Data
```bash
python seed.py
```

This creates:
- 3 demo users (alice@example.com, bob@example.com, charlie@example.com)
- All passwords: `password123`
- 2 projects with issues and comments

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install
```

The frontend uses the backend API at `http://localhost:8000` by default (configured in `src/api/axios.js`).

## 🏃 Running the Application

### Start Backend Server
```bash
cd backend
# Make sure venv is activated
uvicorn app.main:app --reload
```

Backend will run at: **http://localhost:8000**
- API Docs (Swagger): **http://localhost:8000/api/docs**
- ReDoc: **http://localhost:8000/api/redoc**

### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

Frontend will run at: **http://localhost:5173**

### Access the Application

1. Open browser to **http://localhost:5173**
2. Sign up for a new account or use demo credentials:
   - Email: `alice@example.com`
   - Password: `password123`

## 🧪 Running Tests

### Backend Tests
```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

**Test Coverage:**
- Authentication (signup, login, JWT validation)
- Projects (CRUD, member management)
- Issues (CRUD, filtering, search)
- Comments (create, list)
- Authorization & permissions

### Frontend Tests

Frontend tests are not included in the MVP but can be added using:
- **Jest** for unit tests
- **React Testing Library** for component tests
- **Cypress** for E2E tests

## 📚 API Documentation

### Interactive API Docs

Visit **http://localhost:8000/api/docs** for the full interactive Swagger UI.

### Key Endpoints

#### Authentication
```
POST   /api/auth/signup      - Register new user
POST   /api/auth/login       - Login (returns JWT)
GET    /api/me               - Get current user profile
```

#### Projects
```
GET    /api/projects         - List user's projects
POST   /api/projects         - Create project
GET    /api/projects/{id}    - Get project details
POST   /api/projects/{id}/members - Add member
```

#### Issues
```
GET    /api/projects/{id}/issues  - List issues (with filters)
POST   /api/projects/{id}/issues  - Create issue
GET    /api/issues/{id}           - Get issue details
PATCH  /api/issues/{id}           - Update issue
DELETE /api/issues/{id}           - Delete issue (maintainers only)
```

#### Comments
```
GET    /api/issues/{id}/comments  - List comments
POST   /api/issues/{id}/comments  - Add comment
```

### Query Parameters (Issue Filtering)
```
GET /api/projects/{id}/issues?q=login&status=open&priority=high&sort=priority
```

- `q`: Search text (title/description)
- `status`: open | in_progress | resolved | closed
- `priority`: low | medium | high | critical
- `assignee_id`: Filter by assigned user ID
- `sort`: created_at | updated_at | priority | status
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

## 📁 Project Structure
```
issuehub/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Security & dependencies
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── alembic/             # DB migrations
│   ├── tests/               # Pytest tests
│   ├── .env                 # Environment variables
│   ├── requirements.txt
│   └── seed.py
├── frontend/
│   ├── src/
│   │   ├── api/             # API services
│   │   ├── components/      # Reusable components
│   │   ├── context/         # React Context
│   │   ├── pages/           # Page components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🎯 Key Design Decisions

### Backend

**1. FastAPI over Flask/Django**
- **Why:** Modern async support, automatic API documentation, excellent performance, built-in validation with Pydantic
- **Trade-off:** Smaller ecosystem compared to Django

**2. SQLAlchemy ORM**
- **Why:** Flexibility, powerful query building, good PostgreSQL support
- **Trade-off:** More boilerplate than Django ORM

**3. JWT Authentication**
- **Why:** Stateless, scalable, works well with SPAs
- **Trade-off:** Token revocation requires additional infrastructure (acceptable for MVP)

**4. Enum for Status/Priority**
- **Why:** Type safety, prevents invalid values, self-documenting
- **Trade-off:** Schema changes require migrations

### Frontend

**1. React with Vite**
- **Why:** Fast development, HMR, modern tooling, smaller bundle size than CRA
- **Trade-off:** Less opinionated than Next.js

**2. Context API over Redux**
- **Why:** Simpler for MVP scope, built-in, no external dependencies
- **Trade-off:** Not ideal for very complex state management

**3. Axios over Fetch**
- **Why:** Interceptors for auth, better error handling, request/response transformation
- **Trade-off:** Additional dependency

**4. Custom CSS over UI Library**
- **Why:** Full control, no bloat, faster load times, better understanding
- **Trade-off:** More manual work for complex components

## ⚠️ Known Limitations

### Functionality
1. **No email notifications** - Members are added but not notified
2. **No password reset** - Users cannot reset forgotten passwords
3. **No file attachments** - Cannot attach screenshots or logs to issues
4. **No real-time updates** - Page refresh required to see others' changes
5. **Basic pagination UI** - Backend supports it, but no prev/next buttons in frontend
6. **No issue history/audit log** - Can't see who changed what and when
7. **No bulk operations** - Cannot bulk update or delete issues

### Security
1. **No rate limiting** - API calls are not rate-limited
2. **No CSRF protection** - Acceptable for JWT but could be added
3. **Token refresh not implemented** - Users must re-login after 30 minutes
4. **No 2FA** - Single-factor authentication only

### UX
1. **No dark mode** - Single theme only
2. **No keyboard shortcuts** - Mouse-driven interface
3. **No advanced search** - Basic text search only
4. **No saved filters** - Filter preferences not persisted
5. **No notification system** - No in-app or push notifications

### DevOps
1. **No CI/CD pipeline** - Manual deployment
2. **No monitoring/logging** - No error tracking or analytics
3. **No backup strategy** - Database backups not automated
4. **Development environment only** - Not production-ready

## 👥 Team Roles Supported

### Member
- View all issues in projects they belong to
- Create new issues
- Edit their own issues (title, description)
- Add comments to any issue
- Search and filter issues

### Maintainer
- All Member permissions, plus:
- Update any issue (status, priority, assignee)
- Delete issues
- Add/remove project members
- Manage project settings

