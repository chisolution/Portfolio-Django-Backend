"""Contact Service Layer - Business Logic"""
import logging
import re
from typing import Optional, Dict, Any, List
from uuid import UUID

from contact.models import Contact
from contact.repositories import ContactRepository

logger = logging.getLogger(__name__)


class ContactService:
    """Service for Contact business logic"""

    def __init__(self):
        """Initialize the service with repository"""
        self.repository = ContactRepository()

    def create_contact(
        self,
        full_name: str,
        email: str,
        subject: str,
        message: str,
        phone_number: Optional[str] = None,
        preferred_contact_method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        organization: Optional[str] = None
    ) -> Contact:
        """Create a new contact submission with validation and sanitization.

        Args:
            full_name: Contact's full name
            email: Contact's email address
            subject: Subject of the contact
            message: Message content
            phone_number: Optional phone number
            preferred_contact_method: Optional preferred contact method
            ip_address: Optional IP address of the requester
            user_agent: Optional user agent string
            organization: Optional organization name

        Returns:
            Contact: The created contact instance

        Raises:
            ValueError: If validation fails
        """
        # Validate input
        self._validate_contact_input(full_name, email, subject, message)

        # Sanitize input
        full_name = self._sanitize_text(full_name)
        email = self._sanitize_email(email)
        subject = self._sanitize_text(subject)
        message = self._sanitize_text(message)

        if phone_number:
            phone_number = self._sanitize_phone(phone_number)

        if organization:
            organization = self._sanitize_text(organization)

        # Create contact
        contact = self.repository.create(
            full_name=full_name,
            email=email,
            subject=subject,
            message=message,
            phone_number=phone_number,
            preferred_contact_method=preferred_contact_method,
            ip_address=ip_address,
            user_agent=user_agent,
            organization=organization,
            status='new'
        )

        logger.info(f"Contact created successfully: {contact.id}")
        return contact

    def get_contact(self, contact_id: UUID) -> Optional[Contact]:
        """Get a contact by ID.

        Args:
            contact_id: UUID of the contact

        Returns:
            Contact or None if not found
        """
        return self.repository.get_by_id(contact_id)

    def get_all_contacts(self) -> List[Contact]:
        """Get all contacts.

        Returns:
            List of all contacts
        """
        return list(self.repository.get_all())

    def get_contacts_by_status(self, status: str) -> List[Contact]:
        """Get contacts by status.

        Args:
            status: Status to filter by

        Returns:
            List of contacts with the given status
        """
        valid_statuses = ['new', 'contacted', 'closed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        return list(self.repository.get_by_status(status))

    def search_contacts(self, query: str) -> List[Contact]:
        """Search contacts by name, email, or subject.

        Args:
            query: Search query string

        Returns:
            List of matching contacts
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")

        return list(self.repository.search(query))

    def update_contact_status(self, contact_id: UUID, status: str) -> Optional[Contact]:
        """Update contact status.

        Args:
            contact_id: UUID of the contact
            status: New status

        Returns:
            Updated Contact or None if not found

        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = ['new', 'contacted', 'closed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        return self.repository.update(contact_id, status=status)

    def delete_contact(self, contact_id: UUID) -> bool:
        """Delete a contact.

        Args:
            contact_id: UUID of the contact to delete

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(contact_id)

    def get_contact_statistics(self) -> Dict[str, Any]:
        """Get contact statistics.

        Returns:
            Dictionary with contact statistics
        """
        return {
            'total': len(self.repository.get_all()),
            'new': self.repository.count_by_status('new'),
            'contacted': self.repository.count_by_status('contacted'),
            'closed': self.repository.count_by_status('closed')
        }

    def get_paginated_contacts(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get paginated contacts.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Dictionary with paginated data
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        return self.repository.get_paginated(page, page_size)

    # Validation methods
    def _validate_contact_input(
        self,
        full_name: str,
        email: str,
        subject: str,
        message: str
    ) -> None:
        """Validate contact input.

        Args:
            full_name: Contact's full name
            email: Contact's email address
            subject: Subject of the contact
            message: Message content

        Raises:
            ValueError: If validation fails
        """
        if not full_name or len(full_name.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters")

        if len(full_name) > 100:
            raise ValueError("Full name must not exceed 100 characters")

        if not self._is_valid_email(email):
            raise ValueError("Invalid email address")

        if not subject or len(subject.strip()) < 5:
            raise ValueError("Subject must be at least 5 characters")

        if len(subject) > 100:
            raise ValueError("Subject must not exceed 100 characters")

        if not message or len(message.strip()) < 10:
            raise ValueError("Message must be at least 10 characters")

        if len(message) > 5000:
            raise ValueError("Message must not exceed 5000 characters")

    # Sanitization methods
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text input by removing/escaping harmful characters.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Strip whitespace
        text = text.strip()

        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

        return text

    def _sanitize_email(self, email: str) -> str:
        """Sanitize email address.

        Args:
            email: Email to sanitize

        Returns:
            Sanitized email
        """
        return email.strip().lower()

    def _sanitize_phone(self, phone: str) -> str:
        """Sanitize phone number by removing non-digit characters.

        Args:
            phone: Phone number to sanitize

        Returns:
            Sanitized phone number
        """
        # Keep only digits, +, -, (, ), and spaces
        return re.sub(r'[^\d+\-() ]', '', phone).strip()

    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid.

        Args:
            email: Email to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def get_filtered_contacts(
        self,
        page: int = 1,
        page_size: int = 12,
        status: Optional[str] = None,
        preferred_contact_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get filtered and paginated contacts.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Status to filter by
            preferred_contact_method: Preferred contact method to filter by

        Returns:
            Dictionary with filtered and paginated data
        """
        if page < 1:
            raise ValueError("Page number must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("Page size must be between 1 and 100")

        return self.repository.get_filtered(
            page=page,
            page_size=page_size,
            status=status,
            preferred_contact_method=preferred_contact_method
        )
