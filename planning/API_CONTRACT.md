# API Contract - Django Backend

## Overview
This document defines the complete API contract between the Next.js frontend and Django backend. All endpoints are versioned under `/api/v1/` prefix.

---

## Base URL
```
Development: http://localhost:8000
Production: https://api.portfolio.example.com
```

---

## Authentication

### Public Endpoints
- `POST /api/v1/contact` - Contact form submission (public)
- `GET /api/v1/projects` - Project retrieval (public)
- `GET /api/v1/health` - Health check (public)

### Protected Endpoints
- `GET /api/v1/admin/contacts` - View contact submissions (requires authentication)
- `GET /api/v1/admin/projects` - Manage projects (requires authentication)
- `POST /api/v1/admin/projects` - Create project (requires authentication)
- `PUT /api/v1/admin/projects/{id}` - Update project (requires authentication)
- `DELETE /api/v1/admin/projects/{id}` - Delete project (requires authentication)

### Authentication Method
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <access_token>`
- **Token Expiration**: 24 hours
- **Refresh Token**: 7 days
- **Issued by**: `/api/v1/auth/login` endpoint

---

## Response Format

### Success Response (2xx)
```json
{
  "data": {},
  "status": "success",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

### Error Response (4xx, 5xx)
```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "timestamp": "2025-10-19T12:00:00Z",
  "details": {}
}
```

---

## Endpoints

### 1. POST /api/v1/auth/login
**Purpose**: Admin login with email and password

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "admin@portfolio.com",
  "password": "secure_password_123"
}
```

**Request Validation**:
- `email`: Required, valid email format
- `password`: Required, string, 8+ characters

**Response (200 OK)**:
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  },
  "status": "success",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

**Response (401 Unauthorized)**:
```json
{
  "error": "invalid_credentials",
  "message": "Invalid email or password",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

---

### 2. POST /api/v1/auth/password-reset
**Purpose**: Request password reset via email

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "admin@portfolio.com"
}
```

**Response (200 OK)**:
```json
{
  "data": {
    "message": "Password reset email sent"
  },
  "status": "success",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

---

### 3. POST /api/v1/auth/reset-password
**Purpose**: Reset password with token

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "new_secure_password_123"
}
```

**Response (200 OK)**:
```json
{
  "data": {
    "message": "Password reset successfully"
  },
  "status": "success",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

---

### 4. POST /api/v1/contact
**Purpose**: Submit contact form

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Interested in your work",
  "message": "I'd like to discuss opportunities with your team..."
}
```

**Request Validation**:
- `name`: Required, string, 2-100 characters
- `email`: Required, valid email format
- `subject`: Required, string, 5-255 characters
- `message`: Required, string, 10-5000 characters

**Response (201 Created)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Interested in your work",
    "created_at": "2025-10-19T12:00:00Z"
  },
  "status": "success",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

**Response (422 Unprocessable Entity)**:
```json
{
  "error": "validation_error",
  "message": "Validation failed",
  "timestamp": "2025-10-19T12:00:00Z",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

**Response (429 Too Many Requests)**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "timestamp": "2025-10-19T12:00:00Z",
  "retry_after": 3600
}
```

**Response (500 Internal Server Error)**:
```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

**Rate Limiting**:
- Limit: 5 submissions per IP per hour
- Header: `X-RateLimit-Remaining: 4`
- Header: `X-RateLimit-Reset: 1697808000`

**CORS**:
- Allowed Origins: Frontend domain only
- Allowed Methods: POST
- Allowed Headers: Content-Type

---

### 5. GET /api/v1/projects
**Purpose**: Retrieve curated project metadata

**Request Headers**:
```
Accept: application/json
```

**Query Parameters**: None

**Response (200 OK)**:
```json
{
  "data": {
    "projects": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "E-Commerce Platform",
        "description": "Full-stack e-commerce platform with real-time inventory",
        "problem": "Existing system couldn't handle peak traffic during sales",
        "process": "Redesigned architecture using microservices and caching",
        "impact": "Reduced page load time by 60%, improved conversion by 25%",
        "results": "Handled 10x traffic increase during Black Friday",
        "technologies": ["Django", "React", "PostgreSQL", "Redis"],
        "live_demo_url": "https://ecommerce-demo.example.com",
        "github_url": "https://github.com/user/ecommerce-platform",
        "display_order": 1
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Real-Time Analytics Dashboard",
        "description": "Live analytics dashboard with WebSocket updates",
        "problem": "Manual reporting took 2 hours daily",
        "process": "Built real-time dashboard with WebSocket and D3.js",
        "impact": "Eliminated manual reporting, saved 10 hours/week",
        "results": "Executives now have real-time insights",
        "technologies": ["Next.js", "Django", "WebSocket", "D3.js"],
        "live_demo_url": "https://analytics-demo.example.com",
        "github_url": "https://github.com/user/analytics-dashboard",
        "display_order": 2
      }
    ]
  },
  "status": "success",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

**Response (500 Internal Server Error)**:
```json
{
  "error": "internal_server_error",
  "message": "Failed to retrieve projects",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

**Caching**:
- Cache-Control: public, max-age=3600
- ETag support for conditional requests
- Frontend should implement ISR (Incremental Static Regeneration)

**CORS**:
- Allowed Origins: Frontend domain only
- Allowed Methods: GET
- Allowed Headers: Accept

---

### 6. GET /api/v1/health
**Purpose**: Health check for monitoring

**Request Headers**: None

**Response (200 OK)**:
```json
{
  "data": {
    "status": "healthy",
    "database": "connected",
    "uptime_seconds": 3600,
    "version": "1.0.0"
  },
  "status": "success",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "error": "service_unavailable",
  "message": "Service is temporarily unavailable",
  "timestamp": "2025-10-19T12:00:00Z",
  "details": {
    "database": "disconnected"
  }
}
```

**Caching**:
- Cache-Control: no-cache
- Always fetch fresh status

**CORS**:
- Allowed Origins: Any (for monitoring)
- Allowed Methods: GET

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 422 | Input validation failed |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `unauthorized` | 401 | Authentication required |
| `forbidden` | 403 | Access denied |
| `internal_server_error` | 500 | Server error |
| `service_unavailable` | 503 | Service temporarily unavailable |

---

## CORS Configuration

### Allowed Origins
```
https://portfolio.example.com
https://www.portfolio.example.com
http://localhost:3000 (development only)
```

### Allowed Methods
```
GET, POST, OPTIONS
```

### Allowed Headers
```
Content-Type, Accept, Authorization
```

### Exposed Headers
```
X-RateLimit-Remaining, X-RateLimit-Reset
```

### Credentials
```
false (no cookies/auth headers)
```

---

## Rate Limiting

### Contact Form Endpoint
- **Limit**: 5 submissions per IP per hour
- **Window**: 3600 seconds
- **Headers**:
  - `X-RateLimit-Limit: 5`
  - `X-RateLimit-Remaining: 4`
  - `X-RateLimit-Reset: 1697808000`

### Other Endpoints
- No rate limiting (unlimited)

---

## Pagination (Future)

When pagination is needed:

**Query Parameters**:
```
?page=1&limit=10
```

**Response**:
```json
{
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "pages": 10
    }
  }
}
```

---

## Versioning

### Current Version
- API Version: v1
- Base Path: `/api/`

### Future Versioning
If breaking changes needed:
- New endpoints: `/api/v2/`
- Old endpoints: `/api/v1/` (deprecated)
- Deprecation period: 6 months

---

## Frontend Integration Checklist

- [ ] Handle 201 Created response for contact form
- [ ] Handle 422 validation errors with field-level messages
- [ ] Handle 429 rate limit errors with retry-after
- [ ] Handle 500 server errors gracefully
- [ ] Implement caching for /api/projects (ISR)
- [ ] Implement CORS headers correctly
- [ ] Test with actual backend before deployment
- [ ] Monitor error rates in production
- [ ] Implement retry logic for failed requests
- [ ] Log API errors for debugging

---

## Testing

### cURL Examples

**Submit Contact Form**:
```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Test",
    "message": "This is a test message"
  }'
```

**Get Projects**:
```bash
curl -X GET http://localhost:8000/api/projects \
  -H "Accept: application/json"
```

**Health Check**:
```bash
curl -X GET http://localhost:8000/api/health
```

---

## Changelog

### Version 1.0.0 (Initial Release)
- POST /api/contact - Contact form submission
- GET /api/projects - Project metadata retrieval
- GET /api/health - Health check endpoint

