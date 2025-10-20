"""Tests for Auth Repository"""
from django.test import TestCase
from authentication.models import User
from authentication.repositories import UserRepository
import uuid


class UserRepositoryTests(TestCase):
    """Test cases for UserRepository"""

    def setUp(self):
        """Set up test data"""
        self.repo = UserRepository()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Pass123',
            is_staff=True
        )

    def test_create_user(self):
        """Test creating a user via repository"""
        user = self.repo.create(
            username='newuser',
            email='new@example.com',
            password='NewPass123'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')

    def test_get_by_id(self):
        """Test getting user by ID"""
        user = self.repo.get_by_id(self.user1.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1.id)

    def test_get_by_id_not_found(self):
        """Test getting non-existent user by ID"""
        fake_id = uuid.uuid4()
        user = self.repo.get_by_id(fake_id)
        self.assertIsNone(user)

    def test_get_by_username(self):
        """Test getting user by username"""
        user = self.repo.get_by_username('user1')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'user1')

    def test_get_by_username_not_found(self):
        """Test getting non-existent user by username"""
        user = self.repo.get_by_username('nonexistent')
        self.assertIsNone(user)

    def test_get_by_email(self):
        """Test getting user by email"""
        user = self.repo.get_by_email('user1@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'user1@example.com')

    def test_get_by_email_not_found(self):
        """Test getting non-existent user by email"""
        user = self.repo.get_by_email('nonexistent@example.com')
        self.assertIsNone(user)

    def test_get_all(self):
        """Test getting all users"""
        users = self.repo.get_all()
        self.assertEqual(len(users), 2)

    def test_get_active_users(self):
        """Test getting active users"""
        users = self.repo.get_active_users()
        self.assertEqual(len(users), 2)

    def test_get_staff_users(self):
        """Test getting staff users"""
        users = self.repo.get_staff_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'user2')

    def test_get_superusers(self):
        """Test getting superusers"""
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123'
        )
        users = self.repo.get_superusers()
        self.assertEqual(len(users), 1)

    def test_set_password(self):
        """Test setting user password"""
        result = self.repo.set_password(self.user1.id, 'NewPassword123')
        self.assertTrue(result)
        user = self.repo.get_by_id(self.user1.id)
        self.assertTrue(user.check_password('NewPassword123'))

    def test_check_password_correct(self):
        """Test checking correct password"""
        result = self.repo.check_password(self.user1.id, 'Pass123')
        self.assertTrue(result)

    def test_check_password_incorrect(self):
        """Test checking incorrect password"""
        result = self.repo.check_password(self.user1.id, 'WrongPassword')
        self.assertFalse(result)

    def test_activate_user(self):
        """Test activating a user"""
        self.user1.is_active = False
        self.user1.save()
        result = self.repo.activate(self.user1.id)
        self.assertTrue(result)
        user = self.repo.get_by_id(self.user1.id)
        self.assertTrue(user.is_active)

    def test_deactivate_user(self):
        """Test deactivating a user"""
        result = self.repo.deactivate(self.user1.id)
        self.assertTrue(result)
        user = self.repo.get_by_id(self.user1.id)
        self.assertFalse(user.is_active)

    def test_delete_user(self):
        """Test deleting a user"""
        user_id = self.user1.id
        result = self.repo.delete(user_id)
        self.assertTrue(result)
        user = self.repo.get_by_id(user_id)
        self.assertIsNone(user)

    def test_search_users(self):
        """Test searching users"""
        users = self.repo.search('user1')
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'user1')

    def test_update_user(self):
        """Test updating user"""
        user = self.repo.update(self.user1.id, first_name='Updated')
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Updated')

    def test_get_paginated(self):
        """Test getting paginated users"""
        result = self.repo.get_paginated(1, 10)
        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['items']), 2)

    def test_count_active(self):
        """Test counting active users"""
        count = self.repo.count_active()
        self.assertEqual(count, 2)

    def test_count_staff(self):
        """Test counting staff users"""
        count = self.repo.count_staff()
        self.assertEqual(count, 1)

