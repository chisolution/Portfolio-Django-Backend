# Business Rules Document (BRD) - Django Backend

## Rule Set 1: Data Handling & Persistence

### BR-1.1: Render Free Database with Keep-Alive Service (Partial)
- **Rule**: Use Render's free 512MB PostgreSQL database with a periodic keep-alive service that inserts and deletes records to prevent 90-day inactivity deletion
- **Rationale**: Render deletes free databases after 90 days of inactivity. A keep-alive service (running every 24-48 hours) maintains database activity and prevents deletion
- **Enforcement**: Keep-alive service must be implemented and monitored; database activity logs must show regular updates

### BR-1.2: Data Validation & Sanitization
- **Rule**: All incoming data from the frontend MUST be validated and sanitized before storage
- **Rationale**: Prevent SQL injection, XSS attacks, and data corruption
- **Enforcement**: Use Pydantic models for schema validation; implement input sanitization in service layer

### BR-1.3: Contact Form Data Requirements
- **Rule**: Contact form submissions MUST capture: full_name, email, subject, message, timestamp, and IP address
- **Rationale**: Enable follow-up communication and prevent spam
- **Enforcement**: Database schema enforces these fields; API validation rejects incomplete submissions

### BR-1.4: Project Metadata Structure
- **Rule**: Project data MUST follow PPIR format: Problem, Process, Impact, Results
- **Rationale**: Align with portfolio narrative strategy for job hunting
- **Enforcement**: Database schema and API response schema enforce PPIR structure

### BR-1.5: Keep-Alive Service Implementation
- **Rule**: A background service MUST run every 48-72 hours to insert a test record and delete old test records from the database
- **Rationale**: Prevent Render's free database from being deleted due to 90-day inactivity
- **Enforcement**: Service logs all keep-alive operations; monitoring alerts if service fails for >72 hours

## Rule Set 2: API Design & Security

### BR-2.1: Stateless Service Design
- **Rule**: The Django service MUST NOT store any state (sessions, temporary files, cache) within the container
- **Rationale**: Render free tier restarts arbitrarily; persistent state would be lost
- **Enforcement**: No file writes to container; all state managed externally (database or frontend cache)

### BR-2.2: CORS Configuration
- **Rule**: CORS MUST be configured to allow requests only from the Next.js frontend domain
- **Rationale**: Prevent unauthorized API access from other domains
- **Enforcement**: CORS middleware configured with explicit allowed origins

### BR-2.3: Input Validation
- **Rule**: All API endpoints MUST validate input against defined Pydantic schemas
- **Rationale**: Ensure data integrity and prevent malformed requests
- **Enforcement**: Django automatic validation; 422 Unprocessable Entity for invalid input

### BR-2.4: Error Handling
- **Rule**: All errors MUST return appropriate HTTP status codes with descriptive messages
- **Rationale**: Enable frontend to handle errors gracefully
- **Enforcement**: Custom exception handlers for all error scenarios

## Rule Set 3: Performance & Reliability

### BR-3.1: Response Time SLA
- **Rule**: GET endpoints MUST respond within 200ms; POST endpoints within 500ms
- **Rationale**: Ensure responsive user experience on free tier
- **Enforcement**: Performance testing in CI/CD pipeline

### BR-3.2: Health Check Endpoint
- **Rule**: A /api/v1/health endpoint MUST be available for monitoring service status
- **Rationale**: Enable Render to detect service failures and restart if needed
- **Enforcement**: Health check returns 200 OK if database connection is healthy

### BR-3.3: Database Connection Pooling
- **Rule**: Database connections MUST use connection pooling to optimize resource usage
- **Rationale**: Minimize connection overhead on free tier
- **Enforcement**: SQLAlchemy configured with appropriate pool size and timeout

### BR-3.4: Startup Optimization
- **Rule**: Service startup time MUST be < 10 seconds
- **Rationale**: Render may restart service frequently; fast startup ensures availability
- **Enforcement**: Minimize initialization logic; lazy-load non-critical resources

## Rule Set 4: Compliance & Standards

### BR-4.1: WCAG AA Compliance
- **Rule**: All API responses MUST be compatible with WCAG AA accessibility standards
- **Rationale**: Ensure frontend can render accessible content
- **Enforcement**: API documentation includes accessibility guidelines for response data

### BR-4.2: Logging & Monitoring
- **Rule**: All API requests and errors MUST be logged with timestamp, endpoint, status, and duration
- **Rationale**: Enable debugging and performance monitoring
- **Enforcement**: Structured logging middleware implemented

### BR-4.3: API Documentation
- **Rule**: All endpoints MUST be documented with OpenAPI/Swagger specification
- **Rationale**: Enable frontend developers to understand API contract
- **Enforcement**: Django auto-generates Swagger docs at /docs

## Rule Set 5: Authentication & Authorization

### BR-5.1: Admin Authentication
- **Rule**: Site owner MUST authenticate with email and password to access admin endpoints
- **Rationale**: Protect sensitive operations (project management, contact submission viewing)
- **Enforcement**: JWT tokens issued on successful login; all admin endpoints require valid token

### BR-5.2: Password Security
- **Rule**: Passwords MUST be hashed using bcrypt with minimum 12 rounds
- **Rationale**: Protect user credentials from compromise
- **Enforcement**: All password storage uses bcrypt; plaintext passwords never stored

### BR-5.3: Password Reset
- **Rule**: Admin MUST be able to reset password via email verification
- **Rationale**: Enable account recovery if password is forgotten
- **Enforcement**: Reset tokens expire after 1 hour; email verification required

### BR-5.4: Token Expiration
- **Rule**: JWT tokens MUST expire after 24 hours; refresh tokens after 7 days
- **Rationale**: Limit exposure if token is compromised
- **Enforcement**: Token expiration enforced in authentication middleware

## Rule Set 6: Testing & Quality

### BR-6.1: Test Coverage
- **Rule**: All business logic MUST have unit tests with minimum 80% code coverage
- **Rationale**: Ensure reliability and prevent regressions
- **Enforcement**: pytest with coverage reporting in CI/CD

### BR-6.2: Integration Testing
- **Rule**: All API endpoints MUST have integration tests against test database
- **Rationale**: Verify end-to-end functionality
- **Enforcement**: pytest fixtures for test database setup/teardown

### BR-6.3: Database Migrations
- **Rule**: All schema changes MUST use Alembic migrations
- **Rationale**: Enable version control and rollback capability
- **Enforcement**: No direct schema modifications; all changes via migration scripts

