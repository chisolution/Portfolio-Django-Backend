# System Design - Django Backend

## Architecture Overview

### High-Level Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js Frontend (Vercel)                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Contact Form Component  │  Projects Component           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTPS/CORS │
                              │
┌─────────────────────────────────────────────────────────────────┐
│              Django Backend (Render - Free Tier)               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Routes Layer (Presentation)                         │  │
│  │  - POST /api/contact                                     │  │
│  │  - GET /api/projects                                     │  │
│  │  - GET /api/health                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Service Layer (Business Logic)                          │  │
│  │  - ContactService (validation, sanitization)             │  │
│  │  - ProjectService (retrieval, formatting)                │  │
│  │  - HealthService (monitoring)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Repository Layer (Data Access)                          │  │
│  │  - ContactRepository                                     │  │
│  │  - ProjectRepository                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Database Connection Pool (SQLAlchemy)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    PostgreSQL │ Connection
                              │
┌─────────────────────────────────────────────────────────────────┐
│     External PostgreSQL Database (Supabase/Neon - Persistent)   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tables:                                                 │  │
│  │  - contacts (id, name, email, subject, message, ...)     │  │
│  │  - projects (id, title, problem, process, impact, ...)   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## N-Tier Architecture Layers

### Layer 1: Presentation Layer (Routes)
**Location**: `backend/app/routes/`

**Responsibility**: Handle HTTP requests/responses, input validation, error handling

**Components**:
- `contact_routes.py` - Contact form endpoints
- `project_routes.py` - Project retrieval endpoints
- `health_routes.py` - Health check endpoint

**Key Characteristics**:
- Thin layer - minimal business logic
- Uses Pydantic schemas for request/response validation
- Returns appropriate HTTP status codes
- Delegates to service layer

---

### Layer 2: Service Layer (Business Logic)
**Location**: `backend/app/services/`

**Responsibility**: Implement business logic, validation, sanitization, orchestration

**Components**:
- `contact_service.py` - Contact form processing
- `project_service.py` - Project data retrieval and formatting
- `health_service.py` - Health monitoring

**Key Characteristics**:
- Contains all business rules
- Performs input validation and sanitization
- Orchestrates repository calls
- Implements rate limiting
- Handles error scenarios

---

### Layer 3: Repository Layer (Data Access)
**Location**: `backend/app/repositories/`

**Responsibility**: Database operations, query building, transaction management

**Components**:
- `contact_repository.py` - CRUD operations for contacts
- `project_repository.py` - Query operations for projects
- `base_repository.py` - Common repository functionality

**Key Characteristics**:
- Encapsulates database queries
- Uses SQLAlchemy ORM
- Implements connection pooling
- Handles database transactions
- No business logic

---

### Layer 4: Data Layer (Models & Schemas)
**Location**: `backend/app/models/` and `backend/app/schemas/`

**Responsibility**: Define data structures and database models

**Components**:
- `models/contact.py` - Contact database model
- `models/project.py` - Project database model
- `schemas/contact.py` - Contact request/response schemas
- `schemas/project.py` - Project response schema

**Key Characteristics**:
- SQLAlchemy ORM models for database
- Pydantic models for API validation
- Clear separation of concerns

---

## Database Schema

### Contacts Table
```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'new'  -- new, read, responded
);

CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_created_at ON contacts(created_at DESC);
```

### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    problem TEXT NOT NULL,
    process TEXT NOT NULL,
    impact TEXT NOT NULL,
    results TEXT NOT NULL,
    technologies TEXT[] NOT NULL,
    live_demo_url VARCHAR(500),
    github_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_projects_display_order ON projects(display_order);
```

---

## API Endpoints Specification

### 1. POST /api/contact
**Purpose**: Submit contact form

**Request**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Interested in your work",
  "message": "I'd like to discuss opportunities..."
}
```

**Response (200)**:
```json
{
  "id": "uuid",
  "message": "Thank you for your submission",
  "status": "success"
}
```

**Response (422)**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

---

### 2. GET /api/projects
**Purpose**: Retrieve project metadata

**Query Parameters**: None (returns all curated projects)

**Response (200)**:
```json
{
  "projects": [
    {
      "id": "uuid",
      "title": "Project Title",
      "description": "Brief description",
      "problem": "Problem statement",
      "process": "Process description",
      "impact": "Impact description",
      "results": "Results/metrics",
      "technologies": ["Django", "React", "PostgreSQL"],
      "live_demo_url": "https://...",
      "github_url": "https://..."
    }
  ]
}
```

---

### 3. GET /api/health
**Purpose**: Health check for monitoring

**Response (200)**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T12:00:00Z",
  "database": "connected",
  "uptime_seconds": 3600
}
```

**Response (503)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-19T12:00:00Z",
  "database": "disconnected",
  "error": "Cannot connect to database"
}
```

---

## Configuration Management

### Environment Variables
```
DATABASE_URL=postgresql://user:password@host:port/dbname
FRONTEND_URL=https://portfolio.example.com
ENVIRONMENT=production
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=3600
```

### Settings Structure
- `config/settings.py` - Pydantic settings for environment variables
- `config/database.py` - Database connection configuration
- `config/cors.py` - CORS configuration

---

## Error Handling Strategy

### Error Categories
1. **Validation Errors (422)** - Invalid input
2. **Not Found (404)** - Resource not found
3. **Rate Limit (429)** - Too many requests
4. **Server Errors (500)** - Unexpected errors
5. **Service Unavailable (503)** - Database unavailable

### Error Response Format
```json
{
  "error": "error_code",
  "message": "Human-readable message",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

---

## Performance Considerations

### Caching Strategy
- **GET /api/projects**: Cache-Control: public, max-age=3600 (1 hour)
- **GET /api/health**: Cache-Control: no-cache (always fresh)
- **POST /api/contact**: No caching

### Database Optimization
- Connection pooling: min 5, max 20 connections
- Query optimization: indexes on frequently queried columns
- Pagination: prepare for future scalability

### Startup Optimization
- Lazy load non-critical resources
- Pre-warm database connection pool
- Target startup time: < 10 seconds

---

## Security Measures

1. **Input Validation**: Pydantic schemas validate all inputs
2. **Sanitization**: Remove/escape potentially harmful characters
3. **CORS**: Restrict to frontend domain only
4. **Rate Limiting**: Prevent spam (5 submissions per IP per hour)
5. **Error Handling**: Don't expose sensitive information
6. **Logging**: Log all requests for monitoring
7. **HTTPS**: Enforce in production

---

## Testing Strategy

### Unit Tests
- Service layer business logic
- Validation functions
- Error handling

### Integration Tests
- API endpoints with test database
- Database operations
- End-to-end flows

### Performance Tests
- Response time benchmarks
- Load testing on free tier
- Stress testing (restart scenarios)

### Test Coverage Target: 85%+

