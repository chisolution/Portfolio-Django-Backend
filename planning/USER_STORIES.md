# User Stories - Django Backend

## Backend User Stories (BE)

### US-BE-01: Contact Form Submission
**ID**: US-BE-01  
**Role**: Potential Employer  
**Goal**: Submit contact details through a secure, validated form  
**Value/Benefit**: I can easily initiate contact with the developer, ensuring the connection is reliable  
**Priority**: MUST HAVE  

**Acceptance Criteria**:
- [ ] POST /api/v1/contact endpoint accepts name, email, subject, message
- [ ] Email validation ensures valid email format
- [ ] Message length validation (min 10, max 5000 characters)
- [ ] Name validation (min 2, max 100 characters)
- [ ] Submission is stored in persistent database
- [ ] Response includes confirmation message and submission ID
- [ ] Response time < 500ms
- [ ] Invalid input returns 422 with descriptive error messages

**Technical Notes**:
- Use Pydantic for validation
- Implement rate limiting to prevent spam (max 5 submissions per IP per hour)
- Sanitize input to prevent XSS/SQL injection
- Log all submissions for monitoring

---

### US-BE-02: Persistent Contact Storage
**ID**: US-BE-02  
**Role**: Developer  
**Goal**: Have contact form submissions securely stored in a persistent database  
**Value/Benefit**: I can reliably track and follow up on all inbound professional leads indefinitely, mitigating hosting provider failure risks  
**Priority**: MUST HAVE  

**Acceptance Criteria**:
- [ ] Contact submissions persisted in Render's free PostgreSQL database
- [ ] Database connection uses connection pooling
- [ ] Submissions survive service restarts
- [ ] Submissions survive Render free tier restarts
- [ ] Database schema includes: id, full_name, email, subject, message, created_at, ip_address
- [ ] Timestamps stored in UTC
- [ ] No data loss during deployment or service interruptions

**Technical Notes**:
- Use SQLAlchemy ORM for database operations
- Implement database connection health checks
- Use Alembic for schema migrations
- Test with external database provider (Supabase/Neon)

---

### US-BE-03: Project Metadata Retrieval
**ID**: US-BE-03  
**Role**: Frontend Application  
**Goal**: Retrieve curated project metadata for dynamic consumption  
**Value/Benefit**: Project data can be updated without redeploying frontend; enables dynamic case study rendering  
**Priority**: MUST HAVE  

**Acceptance Criteria**:
- [ ] GET /api/v1/projects endpoint returns list of projects
- [ ] Each project includes: id, title, description, problem, process, impact, results, technologies, links
- [ ] Response includes live demo link and GitHub repository link
- [ ] Response time < 200ms
- [ ] Response is cached on frontend (ISR/static generation)
- [ ] Projects are ordered by display_order
- [ ] Only published projects are returned (is_published=true)

**Technical Notes**:
- Implement caching headers (Cache-Control: public, max-age=3600)
- Consider pagination for future scalability
- Return data in PPIR format for frontend consumption

---

### US-BE-04: Health Check Monitoring
**ID**: US-BE-04  
**Role**: Render Monitoring System  
**Goal**: Monitor service health and detect failures  
**Value/Benefit**: Service can be automatically restarted if it becomes unhealthy  
**Priority**: SHOULD HAVE  

**Acceptance Criteria**:
- [ ] GET /api/v1/health endpoint returns 200 OK when healthy
- [ ] Health check verifies database connectivity
- [ ] Response includes service status and timestamp
- [ ] Response time < 100ms
- [ ] Returns 503 Service Unavailable if database is unreachable

**Technical Notes**:
- Implement lightweight health check
- Don't perform expensive operations in health check
- Use for Render's health check configuration

---

### US-BE-05: API Documentation
**ID**: US-BE-05  
**Role**: Frontend Developer  
**Goal**: Access comprehensive API documentation  
**Value/Benefit**: I can understand the API contract and integrate with confidence  
**Priority**: SHOULD HAVE  

**Acceptance Criteria**:
- [ ] Swagger/OpenAPI documentation available at /docs
- [ ] All endpoints documented with request/response schemas
- [ ] Example requests and responses provided
- [ ] Error responses documented
- [ ] CORS requirements documented

**Technical Notes**:
- Django auto-generates Swagger docs
- Ensure all Pydantic models have descriptive docstrings
- Include example values in schema definitions

---

### US-BE-06: Admin Authentication
**ID**: US-BE-06
**Role**: Site Owner (Developer)
**Goal**: Securely authenticate to access admin dashboard and manage content
**Value/Benefit**: I can protect sensitive operations and ensure only authorized access to project and contact management
**Priority**: MUST HAVE

**Acceptance Criteria**:
- [ ] POST /api/v1/auth/login endpoint accepts email and password
- [ ] Valid credentials return JWT access token and refresh token
- [ ] Invalid credentials return 401 Unauthorized
- [ ] Access token expires after 24 hours
- [ ] Refresh token expires after 7 days
- [ ] Passwords are hashed with bcrypt (minimum 12 rounds)
- [ ] Failed login attempts are logged
- [ ] Response time < 500ms

**Technical Notes**:
- Use PyJWT for token generation
- Use bcrypt for password hashing
- Implement rate limiting on login endpoint (5 attempts per IP per hour)
- Store user credentials securely in database

---

### US-BE-07: Password Reset
**ID**: US-BE-07
**Role**: Site Owner (Developer)
**Goal**: Reset forgotten password securely
**Value/Benefit**: I can regain access to my account if I forget my password
**Priority**: SHOULD HAVE

**Acceptance Criteria**:
- [ ] POST /api/v1/auth/password-reset accepts email
- [ ] Reset email sent with secure token link
- [ ] Reset token expires after 1 hour
- [ ] POST /api/v1/auth/reset-password accepts token and new password
- [ ] New password must be different from old password
- [ ] Password updated successfully returns 200 OK
- [ ] Invalid or expired token returns 400 Bad Request

**Technical Notes**:
- Use secure random token generation
- Send reset link via email (implement email service)
- Store reset tokens with expiration in database
- Log all password reset attempts

---

### US-BE-08: Contact Submission Management
**ID**: US-BE-08
**Role**: Site Owner (Developer)
**Goal**: View and manage contact form submissions
**Value/Benefit**: I can track all inbound leads and manage their status
**Priority**: MUST HAVE

**Acceptance Criteria**:
- [ ] GET /api/v1/admin/contacts returns all contact submissions (protected)
- [ ] GET /api/v1/admin/contacts/{id} returns single contact (protected)
- [ ] PUT /api/v1/admin/contacts/{id} updates contact status (protected)
- [ ] Contact statuses: new, read, responded
- [ ] Response includes: id, name, email, subject, message, status, created_at
- [ ] Submissions sorted by created_at (newest first)
- [ ] Requires valid JWT token in Authorization header

**Technical Notes**:
- Implement authentication middleware for protected routes
- Use repository pattern for database queries
- Add pagination for large result sets
- Log all admin access

---

### US-BE-09: Project Management
**ID**: US-BE-09
**Role**: Site Owner (Developer)
**Goal**: Create, update, and delete projects in the portfolio
**Value/Benefit**: I can manage my project portfolio without redeploying the frontend
**Priority**: MUST HAVE

**Acceptance Criteria**:
- [ ] POST /api/v1/admin/projects creates new project (protected)
- [ ] PUT /api/v1/admin/projects/{id} updates project (protected)
- [ ] DELETE /api/v1/admin/projects/{id} deletes project (protected)
- [ ] GET /api/v1/admin/projects lists all projects (protected)
- [ ] Project fields: title, description, problem, process, impact, results, technologies, links, dates
- [ ] Project slug must be unique
- [ ] is_published flag controls visibility
- [ ] is_featured flag for featured projects
- [ ] Requires valid JWT token

**Technical Notes**:
- Implement full CRUD operations
- Validate all input fields
- Generate project slug from title
- Support image uploads (store URLs)
- Implement soft deletes (is_deleted flag)

---

### US-BE-10: Database Keep-Alive Service
**ID**: US-BE-10
**Role**: System
**Goal**: Maintain database activity to prevent 90-day inactivity deletion
**Value/Benefit**: Render's free database won't be deleted due to inactivity
**Priority**: MUST HAVE

**Acceptance Criteria**:
- [ ] Background service runs every 24-48 hours
- [ ] Service inserts test record into database
- [ ] Service deletes old test records (>7 days old)
- [ ] Service logs all operations
- [ ] Service handles database connection failures gracefully
- [ ] Service doesn't interfere with normal operations
- [ ] Monitoring alerts if service fails for >72 hours

**Technical Notes**:
- Use APScheduler or similar for scheduling
- Create dedicated keep_alive_logs table
- Implement error handling and retry logic
- Log all keep-alive operations for monitoring

---

## Epic: Contact Form End-to-End Flow

**Epic**: E2E Contact Form Submission  
**Description**: Complete flow from frontend form submission to persistent storage and developer notification  

**Related Stories**:
- US-BE-01: Contact Form Submission
- US-BE-02: Persistent Contact Storage

**Success Criteria**:
- [ ] Frontend can submit form to /api/contact
- [ ] Backend validates and stores submission
- [ ] Submission persists in external database
- [ ] Developer receives notification (email or dashboard)
- [ ] No data loss on service restart

---

## Epic: Dynamic Project Content

**Epic**: Dynamic Project Metadata  
**Description**: Enable project information to be updated without frontend redeployment  

**Related Stories**:
- US-BE-03: Project Metadata Retrieval

**Success Criteria**:
- [ ] Projects can be added/updated in database
- [ ] Frontend fetches projects dynamically
- [ ] Changes visible within cache TTL (1 hour)
- [ ] Supports PPIR narrative structure

