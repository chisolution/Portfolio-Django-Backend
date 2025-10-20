"""Auth Service Layer - Business Logic"""
import logging
import re
from typing import Optional, Dict, Any, List
from uuid import UUID

from auth.models import User
from auth.repositories import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service for User business logic"""

    def __init__(self):
        """Initialize the service with repository"""
        self.repository = UserRepository()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        is_active: bool = True,
        is_staff: bool = False,
        is_superuser: bool = False
    ) -> User:
        """Create a new user with validation.

        Args:
            username: Unique username
            email: Unique email address
            password: User's password
            first_name: User's first name
            last_name: User's last name
            is_active: Whether user is active
            is_staff: Whether user is staff
            is_superuser: Whether user is superuser

        Returns:
            User: The created user instance

        Raises:
            ValueError: If validation fails
        """
        # Validate input
        self._validate_user_input(username, email, password, first_name, last_name)

        # Check if user already exists
        if self.repository.get_by_username(username):
            raise ValueError(f"Username '{username}' already exists")

        if self.repository.get_by_email(email):
            raise ValueError(f"Email '{email}' already exists")

        # Create user
        user = self.repository.create(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser
        )

        logger.info(f"User created successfully: {user.id}")
        return user

    def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: UUID of the user

        Returns:
            User or None if not found
        """
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: Username to search for

        Returns:
            User or None if not found
        """
        return self.repository.get_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: Email address to search for

        Returns:
            User or None if not found
        """
        return self.repository.get_by_email(email)

    def get_all_users(self) -> List[User]:
        """Get all users.

        Returns:
            List of all users
        """
        return list(self.repository.get_all())

    def get_active_users(self) -> List[User]:
        """Get all active users.

        Returns:
            List of active users
        """
        return list(self.repository.get_active_users())

    def get_staff_users(self) -> List[User]:
        """Get all staff users.

        Returns:
            List of staff users
        """
        return list(self.repository.get_staff_users())

    def get_superusers(self) -> List[User]:
        """Get all superusers.

        Returns:
            List of superusers
        """
        return list(self.repository.get_superusers())

    def search_users(self, query: str) -> List[User]:
        """Search users by username, email, first name, or last name.

        Args:
            query: Search query string

        Returns:
            List of matching users
        """
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")

        return list(self.repository.search(query))

    def update_user(self, user_id: UUID, **kwargs) -> Optional[User]:
        """Update a user.

        Args:
            user_id: UUID of the user to update
            **kwargs: Fields to update (excluding password)

        Returns:
            Updated User or None if not found
        """
        return self.repository.update(user_id, **kwargs)

    def change_password(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        """Change a user's password.

        Args:
            user_id: UUID of the user
            old_password: Current password
            new_password: New password

        Returns:
            True if successful, False if old password is incorrect or user not found

        Raises:
            ValueError: If new password is invalid
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return False

        # Verify old password
        if not self.repository.check_password(user_id, old_password):
            logger.warning(f"Failed password change attempt for user: {user_id}")
            return False

        # Validate new password
        self._validate_password(new_password)

        # Set new password
        return self.repository.set_password(user_id, new_password)

    def reset_password(self, user_id: UUID, new_password: str) -> bool:
        """Reset a user's password (admin only).

        Args:
            user_id: UUID of the user
            new_password: New password

        Returns:
            True if successful, False if user not found

        Raises:
            ValueError: If new password is invalid
        """
        # Validate new password
        self._validate_password(new_password)

        return self.repository.set_password(user_id, new_password)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user.

        Args:
            username: Username
            password: Password

        Returns:
            User if authentication successful, None otherwise
        """
        user = self.repository.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: user not found - {username}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {username}")
            return None

        if not self.repository.check_password(user.id, password):
            logger.warning(f"Authentication failed: invalid password - {username}")
            return None

        logger.info(f"User authenticated successfully: {user.id}")
        return user

    def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate a user.

        Args:
            user_id: UUID of the user to deactivate

        Returns:
            True if successful, False if user not found
        """
        return self.repository.deactivate(user_id)

    def activate_user(self, user_id: UUID) -> bool:
        """Activate a user.

        Args:
            user_id: UUID of the user to activate

        Returns:
            True if successful, False if user not found
        """
        return self.repository.activate(user_id)

    def delete_user(self, user_id: UUID) -> bool:
        """Delete a user.

        Args:
            user_id: UUID of the user to delete

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(user_id)

    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics.

        Returns:
            Dictionary with user statistics
        """
        return {
            'total': len(self.repository.get_all()),
            'active': self.repository.count_active(),
            'staff': self.repository.count_staff()
        }

    def get_paginated_users(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get paginated users.

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
    def _validate_user_input(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str
    ) -> None:
        """Validate user input.

        Args:
            username: Username
            email: Email address
            password: Password
            first_name: First name
            last_name: Last name

        Raises:
            ValueError: If validation fails
        """
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")

        if len(username) > 100:
            raise ValueError("Username must not exceed 100 characters")

        if not self._is_valid_email(email):
            raise ValueError("Invalid email address")

        self._validate_password(password)

        if first_name and len(first_name) > 100:
            raise ValueError("First name must not exceed 100 characters")

        if last_name and len(last_name) > 100:
            raise ValueError("Last name must not exceed 100 characters")

    def _validate_password(self, password: str) -> None:
        """Validate password strength.

        Args:
            password: Password to validate

        Raises:
            ValueError: If password is invalid
        """
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if len(password) > 128:
            raise ValueError("Password must not exceed 128 characters")

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")

    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid.

        Args:
            email: Email to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
