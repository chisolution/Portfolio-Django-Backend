"""Auth Repository Layer - Data Access Abstraction"""
import logging
from typing import Optional, Dict, Any
from uuid import UUID

from django.db.models import QuerySet, Q
from auth.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User model - handles all database operations"""

    @staticmethod
    def create(
        username: str,
        email: str,
        first_name: str = "",
        last_name: str = "",
        password: str = "",
        is_active: bool = True,
        is_staff: bool = False,
        is_superuser: bool = False
    ) -> User:
        """Create a new user.

        Args:
            username: Unique username
            email: Unique email address
            first_name: User's first name
            last_name: User's last name
            password: User's password (will be hashed)
            is_active: Whether user is active
            is_staff: Whether user is staff
            is_superuser: Whether user is superuser

        Returns:
            User: The created user instance
        """
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_active=is_active,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            logger.info(f"User created: {user.id}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    @staticmethod
    def get_by_id(user_id: UUID) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: UUID of the user

        Returns:
            User or None if not found
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"User not found: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            raise

    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: Username to search for

        Returns:
            User or None if not found
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(f"User not found with username: {username}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by username: {str(e)}")
            raise

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: Email address to search for

        Returns:
            User or None if not found
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"User not found with email: {email}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user by email: {str(e)}")
            raise

    @staticmethod
    def get_all() -> QuerySet:
        """Get all users.

        Returns:
            QuerySet of all users ordered by date joined
        """
        return User.objects.all().order_by('-date_joined')

    @staticmethod
    def get_active_users() -> QuerySet:
        """Get all active users.

        Returns:
            QuerySet of active users
        """
        return User.objects.filter(is_active=True).order_by('-date_joined')

    @staticmethod
    def get_staff_users() -> QuerySet:
        """Get all staff users.

        Returns:
            QuerySet of staff users
        """
        return User.objects.filter(is_staff=True).order_by('-date_joined')

    @staticmethod
    def get_superusers() -> QuerySet:
        """Get all superusers.

        Returns:
            QuerySet of superusers
        """
        return User.objects.filter(is_superuser=True).order_by('-date_joined')

    @staticmethod
    def search(query: str) -> QuerySet:
        """Search users by username, email, first name, or last name.

        Args:
            query: Search query string

        Returns:
            QuerySet of matching users
        """
        return User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).order_by('-date_joined')

    @staticmethod
    def update(user_id: UUID, **kwargs) -> Optional[User]:
        """Update a user.

        Args:
            user_id: UUID of the user to update
            **kwargs: Fields to update

        Returns:
            Updated User or None if not found
        """
        try:
            user = User.objects.get(id=user_id)
            for key, value in kwargs.items():
                if hasattr(user, key) and key != 'password':
                    setattr(user, key, value)
            user.save()
            logger.info(f"User updated: {user_id}")
            return user
        except User.DoesNotExist:
            logger.warning(f"User not found for update: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise

    @staticmethod
    def set_password(user_id: UUID, password: str) -> bool:
        """Set a user's password.

        Args:
            user_id: UUID of the user
            password: New password

        Returns:
            True if successful, False if user not found
        """
        try:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            logger.info(f"Password updated for user: {user_id}")
            return True
        except User.DoesNotExist:
            logger.warning(f"User not found for password update: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error updating password: {str(e)}")
            raise

    @staticmethod
    def check_password(user_id: UUID, password: str) -> bool:
        """Check if a password is correct for a user.

        Args:
            user_id: UUID of the user
            password: Password to check

        Returns:
            True if password is correct, False otherwise
        """
        try:
            user = User.objects.get(id=user_id)
            return user.check_password(password)
        except User.DoesNotExist:
            logger.warning(f"User not found for password check: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error checking password: {str(e)}")
            raise

    @staticmethod
    def deactivate(user_id: UUID) -> bool:
        """Deactivate a user.

        Args:
            user_id: UUID of the user to deactivate

        Returns:
            True if successful, False if user not found
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            logger.info(f"User deactivated: {user_id}")
            return True
        except User.DoesNotExist:
            logger.warning(f"User not found for deactivation: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            raise

    @staticmethod
    def activate(user_id: UUID) -> bool:
        """Activate a user.

        Args:
            user_id: UUID of the user to activate

        Returns:
            True if successful, False if user not found
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            logger.info(f"User activated: {user_id}")
            return True
        except User.DoesNotExist:
            logger.warning(f"User not found for activation: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error activating user: {str(e)}")
            raise

    @staticmethod
    def delete(user_id: UUID) -> bool:
        """Delete a user.

        Args:
            user_id: UUID of the user to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            logger.info(f"User deleted: {user_id}")
            return True
        except User.DoesNotExist:
            logger.warning(f"User not found for deletion: {user_id}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise

    @staticmethod
    def get_paginated(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get paginated users.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Dictionary with paginated data and metadata
        """
        total_count = User.objects.count()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        users = User.objects.all().order_by('-date_joined')[start_idx:end_idx]

        return {
            'items': list(users),
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }

    @staticmethod
    def count_active() -> int:
        """Count active users.

        Returns:
            Number of active users
        """
        return User.objects.filter(is_active=True).count()

    @staticmethod
    def count_staff() -> int:
        """Count staff users.

        Returns:
            Number of staff users
        """
        return User.objects.filter(is_staff=True).count()
