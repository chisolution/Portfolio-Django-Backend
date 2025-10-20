"""Contact Repository Layer - Data Access Abstraction"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from django.db.models import QuerySet, Q
from contact.models import Contact

logger = logging.getLogger(__name__)


class ContactRepository:
    """Repository for Contact model - handles all database operations"""

    @staticmethod
    def create(
        full_name: str,
        email: str,
        subject: str,
        message: str,
        phone_number: Optional[str] = None,
        preferred_contact_method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        organization: Optional[str] = None,
        status: str = 'new'
    ) -> Contact:
        """Create a new contact submission.

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
            status: Status of the contact (default: 'new')

        Returns:
            Contact: The created contact instance
        """
        try:
            contact = Contact.objects.create(
                full_name=full_name,
                email=email,
                subject=subject,
                message=message,
                phone_number=phone_number,
                preferred_contact_method=preferred_contact_method,
                ip_address=ip_address,
                user_agent=user_agent,
                organization=organization,
                status=status
            )
            logger.info(f"Contact created: {contact.id}")
            return contact
        except Exception as e:
            logger.error(f"Error creating contact: {str(e)}")
            raise

    @staticmethod
    def get_by_id(contact_id: UUID) -> Optional[Contact]:
        """Get a contact by ID.

        Args:
            contact_id: UUID of the contact

        Returns:
            Contact or None if not found
        """
        try:
            return Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            logger.warning(f"Contact not found: {contact_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving contact: {str(e)}")
            raise

    @staticmethod
    def get_all() -> QuerySet:
        """Get all contacts.

        Returns:
            QuerySet of all contacts ordered by creation date
        """
        return Contact.objects.all().order_by('-created_at')

    @staticmethod
    def get_by_email(email: str) -> QuerySet:
        """Get contacts by email address.

        Args:
            email: Email address to search for

        Returns:
            QuerySet of contacts with matching email
        """
        return Contact.objects.filter(email=email).order_by('-created_at')

    @staticmethod
    def get_by_status(status: str) -> QuerySet:
        """Get contacts by status.

        Args:
            status: Status to filter by

        Returns:
            QuerySet of contacts with matching status
        """
        return Contact.objects.filter(status=status).order_by('-created_at')

    @staticmethod
    def get_by_date_range(start_date, end_date) -> QuerySet:
        """Get contacts created within a date range.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            QuerySet of contacts within the date range
        """
        return Contact.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        ).order_by('-created_at')

    @staticmethod
    def update(contact_id: UUID, **kwargs) -> Optional[Contact]:
        """Update a contact.

        Args:
            contact_id: UUID of the contact to update
            **kwargs: Fields to update

        Returns:
            Updated Contact or None if not found
        """
        try:
            contact = Contact.objects.get(id=contact_id)
            for key, value in kwargs.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
            contact.save()
            logger.info(f"Contact updated: {contact_id}")
            return contact
        except Contact.DoesNotExist:
            logger.warning(f"Contact not found for update: {contact_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating contact: {str(e)}")
            raise

    @staticmethod
    def delete(contact_id: UUID) -> bool:
        """Delete a contact.

        Args:
            contact_id: UUID of the contact to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.delete()
            logger.info(f"Contact deleted: {contact_id}")
            return True
        except Contact.DoesNotExist:
            logger.warning(f"Contact not found for deletion: {contact_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting contact: {str(e)}")
            raise

    @staticmethod
    def search(query: str) -> QuerySet:
        """Search contacts by name, email, or subject.

        Args:
            query: Search query string

        Returns:
            QuerySet of matching contacts
        """
        return Contact.objects.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query)
        ).order_by('-created_at')

    @staticmethod
    def count_by_status(status: str) -> int:
        """Count contacts by status.

        Args:
            status: Status to count

        Returns:
            Number of contacts with the given status
        """
        return Contact.objects.filter(status=status).count()

    @staticmethod
    def get_paginated(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get paginated contacts.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Dictionary with paginated data and metadata
        """
        total_count = Contact.objects.count()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        contacts = Contact.objects.all().order_by('-created_at')[start_idx:end_idx]

        return {
            'items': list(contacts),
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }