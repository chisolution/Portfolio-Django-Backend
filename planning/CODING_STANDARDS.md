# Coding Standards - Django Backend

## Python Code Style

### General Guidelines
- **Python Version**: 3.9+
- **Style Guide**: PEP 8
- **Line Length**: 100 characters (soft limit), 120 (hard limit)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Organized in groups (stdlib, third-party, local)

### Naming Conventions
```python
# Classes: PascalCase
class ContactService:
    pass

# Functions/Methods: snake_case
def get_contact_by_id(contact_id: str) -> Contact:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_MESSAGE_LENGTH = 5000
DEFAULT_RATE_LIMIT = 5

# Private methods: _leading_underscore
def _validate_email(email: str) -> bool:
    pass

# Protected methods: _leading_underscore
def _sanitize_input(text: str) -> str:
    pass
```

---

## Django Best Practices

### Route Organization
```python
# routes/contact_routes.py
from Django import APIRouter, HTTPException, status
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService

router = APIRouter(prefix="/api", tags=["contact"])

@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate) -> ContactResponse:
    """Create a new contact submission."""
    service = ContactService()
    return await service.create_contact(contact)
```

### Dependency Injection
```python
# Use Django's Depends for dependency injection
from Django import Depends

async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@router.get("/projects")
async def get_projects(session: AsyncSession = Depends(get_db_session)):
    pass
```

### Error Handling
```python
# Use HTTPException for API errors
from Django import HTTPException, status

@router.get("/contact/{contact_id}")
async def get_contact(contact_id: str):
    contact = await repository.get_by_id(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact
```

---

## Pydantic Schema Guidelines

### Request Schemas
```python
from pydantic import BaseModel, EmailStr, Field

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=5, max_length=255)
    message: str = Field(..., min_length=10, max_length=5000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "subject": "Interested in your work",
                "message": "I'd like to discuss opportunities..."
            }
        }
```

### Response Schemas
```python
from datetime import datetime
from uuid import UUID

class ContactResponse(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # For SQLAlchemy models
```

---

## SQLAlchemy ORM Guidelines

### Model Definition
```python
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, email={self.email})>"
```

### Repository Pattern
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, contact: Contact) -> Contact:
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact
    
    async def get_by_id(self, contact_id: UUID) -> Contact | None:
        result = await self.session.execute(
            select(Contact).where(Contact.id == contact_id)
        )
        return result.scalar_one_or_none()
```

---

## Service Layer Guidelines

### Business Logic Organization
```python
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact import ContactCreate, ContactResponse

class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository
    
    async def create_contact(self, contact_data: ContactCreate) -> ContactResponse:
        # Validation
        self._validate_contact(contact_data)
        
        # Sanitization
        sanitized_data = self._sanitize_contact(contact_data)
        
        # Business logic
        contact = Contact(**sanitized_data.dict())
        
        # Persistence
        created_contact = await self.repository.create(contact)
        
        return ContactResponse.from_orm(created_contact)
    
    def _validate_contact(self, contact: ContactCreate) -> None:
        """Validate contact data."""
        if len(contact.message) < 10:
            raise ValueError("Message too short")
    
    def _sanitize_contact(self, contact: ContactCreate) -> ContactCreate:
        """Sanitize contact data."""
        # Remove/escape potentially harmful characters
        return contact
```

---

## Testing Guidelines

### Unit Test Structure
```python
import pytest
from app.services.contact_service import ContactService
from app.schemas.contact import ContactCreate

@pytest.mark.asyncio
async def test_create_contact_success():
    # Arrange
    contact_data = ContactCreate(
        name="John Doe",
        email="john@example.com",
        subject="Test",
        message="This is a test message"
    )
    service = ContactService(mock_repository)
    
    # Act
    result = await service.create_contact(contact_data)
    
    # Assert
    assert result.id is not None
    assert result.email == "john@example.com"

@pytest.mark.asyncio
async def test_create_contact_invalid_email():
    # Arrange
    contact_data = ContactCreate(
        name="John Doe",
        email="invalid-email",
        subject="Test",
        message="This is a test message"
    )
    service = ContactService(mock_repository)
    
    # Act & Assert
    with pytest.raises(ValueError):
        await service.create_contact(contact_data)
```

### Integration Test Structure
```python
@pytest.mark.asyncio
async def test_contact_endpoint_post(client: AsyncClient):
    # Arrange
    payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "subject": "Test",
        "message": "This is a test message"
    }
    
    # Act
    response = await client.post("/api/contact", json=payload)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["email"] == "john@example.com"
```

---

## Documentation Guidelines

### Docstring Format (Google Style)
```python
async def create_contact(self, contact_data: ContactCreate) -> ContactResponse:
    """Create a new contact submission.
    
    Args:
        contact_data: Contact information from the form.
    
    Returns:
        ContactResponse: The created contact with ID and timestamp.
    
    Raises:
        ValueError: If contact data is invalid.
        DatabaseError: If database operation fails.
    """
    pass
```

### Inline Comments
```python
# Use comments for WHY, not WHAT
# Good:
# Limit to 5 submissions per IP per hour to prevent spam
if request_count > 5:
    raise RateLimitError()

# Bad:
# Check if request count is greater than 5
if request_count > 5:
    raise RateLimitError()
```

---

## File Organization

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Django app initialization
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Environment configuration
│   │   ├── database.py         # Database setup
│   │   └── cors.py             # CORS configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── contact.py          # Contact ORM model
│   │   └── project.py          # Project ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── contact.py          # Contact Pydantic schemas
│   │   └── project.py          # Project Pydantic schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── contact_routes.py   # Contact endpoints
│   │   ├── project_routes.py   # Project endpoints
│   │   └── health_routes.py    # Health check endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── contact_service.py  # Contact business logic
│   │   ├── project_service.py  # Project business logic
│   │   └── health_service.py   # Health check logic
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py  # Base repository class
│   │   ├── contact_repository.py
│   │   └── project_repository.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py       # Validation utilities
│       └── sanitizers.py       # Sanitization utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   ├── unit/
│   │   ├── test_contact_service.py
│   │   └── test_project_service.py
│   └── integration/
│       ├── test_contact_routes.py
│       └── test_project_routes.py
├── migrations/                 # Alembic migrations
├── .env.example
├── requirements.txt
└── README.md
```

---

## Git Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/dependency changes

### Examples
```
feat(contact): add rate limiting to contact form

Implement rate limiting to prevent spam submissions.
Limit to 5 submissions per IP per hour.

Closes #123
```

---

## Code Review Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Tests written and passing
- [ ] No hardcoded values (use config)
- [ ] Error handling implemented
- [ ] No sensitive data in logs
- [ ] Database queries optimized
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] Response schemas defined

