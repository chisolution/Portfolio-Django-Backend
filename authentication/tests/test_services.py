"""Tests for Auth Service"""
from django.test import TestCase
from authentication.models import User
from authentication.services import UserService


class UserServiceTests(TestCase):
    """Test cases for UserService"""

    def setUp(self):
        """Set up test data"""
        self.service = UserService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )

    def test_create_user_success(self):
        """Test creating a user successfully"""
        user = self.service.create_user(
            username='newuser',
            email='new@example.com',
            password='NewPass123'
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'newuser')

    def test_create_user_duplicate_username(self):
        """Test creating user with duplicate username"""
        with self.assertRaises(ValueError):
            self.service.create_user(
                username='testuser',
                email='different@example.com',
                password='Pass123'
            )

    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email"""
        with self.assertRaises(ValueError):
            self.service.create_user(
                username='different',
                email='test@example.com',
                password='Pass123'
            )

    def test_create_user_invalid_username(self):
        """Test creating user with invalid username"""
        with self.assertRaises(ValueError):
            self.service.create_user(
                username='ab',
                email='new@example.com',
                password='Pass123'
            )

    def test_create_user_invalid_email(self):
        """Test creating user with invalid email"""
        with self.assertRaises(ValueError):
            self.service.create_user(
                username='newuser',
                email='invalid-email',
                password='Pass123'
            )

    def test_create_user_weak_password(self):
        """Test creating user with weak password"""
        with self.assertRaises(ValueError):
            self.service.create_user(
                username='newuser',
                email='new@example.com',
                password='weak'
            )

    def test_get_user(self):
        """Test getting a user"""
        user = self.service.get_user(self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user.id)

    def test_get_user_by_username(self):
        """Test getting user by username"""
        user = self.service.get_user_by_username('testuser')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_get_user_by_email(self):
        """Test getting user by email"""
        user = self.service.get_user_by_email('test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

    def test_authenticate_success(self):
        """Test successful authentication"""
        user = self.service.authenticate('testuser', 'TestPass123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_authenticate_wrong_password(self):
        """Test authentication with wrong password"""
        user = self.service.authenticate('testuser', 'WrongPassword')
        self.assertIsNone(user)

    def test_authenticate_nonexistent_user(self):
        """Test authentication with non-existent user"""
        user = self.service.authenticate('nonexistent', 'Pass123')
        self.assertIsNone(user)

    def test_authenticate_inactive_user(self):
        """Test authentication with inactive user"""
        self.user.is_active = False
        self.user.save()
        user = self.service.authenticate('testuser', 'TestPass123')
        self.assertIsNone(user)

    def test_change_password_success(self):
        """Test changing password successfully"""
        result = self.service.change_password(
            self.user.id,
            'TestPass123',
            'NewPass123'
        )
        self.assertTrue(result)

    def test_change_password_wrong_old_password(self):
        """Test changing password with wrong old password"""
        result = self.service.change_password(
            self.user.id,
            'WrongPassword',
            'NewPass123'
        )
        self.assertFalse(result)

    def test_change_password_weak_new_password(self):
        """Test changing password with weak new password"""
        with self.assertRaises(ValueError):
            self.service.change_password(
                self.user.id,
                'TestPass123',
                'weak'
            )

    def test_reset_password(self):
        """Test resetting password"""
        result = self.service.reset_password(self.user.id, 'NewPass123')
        self.assertTrue(result)

    def test_deactivate_user(self):
        """Test deactivating user"""
        result = self.service.deactivate_user(self.user.id)
        self.assertTrue(result)
        user = self.service.get_user(self.user.id)
        self.assertFalse(user.is_active)

    def test_activate_user(self):
        """Test activating user"""
        self.user.is_active = False
        self.user.save()
        result = self.service.activate_user(self.user.id)
        self.assertTrue(result)
        user = self.service.get_user(self.user.id)
        self.assertTrue(user.is_active)

    def test_delete_user(self):
        """Test deleting user"""
        user_id = self.user.id
        result = self.service.delete_user(user_id)
        self.assertTrue(result)
        user = self.service.get_user(user_id)
        self.assertIsNone(user)

    def test_get_user_statistics(self):
        """Test getting user statistics"""
        stats = self.service.get_user_statistics()
        self.assertIn('total', stats)
        self.assertIn('active', stats)
        self.assertIn('staff', stats)
        self.assertEqual(stats['total'], 1)

    def test_get_paginated_users(self):
        """Test getting paginated users"""
        result = self.service.get_paginated_users(1, 10)
        self.assertIn('total', result)
        self.assertIn('items', result)
        self.assertEqual(result['total'], 1)

