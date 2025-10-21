"""Tests for Auth Models"""
from django.test import TestCase
from authentication.models import User
import uuid


class UserModelTests(TestCase):
    """Test cases for User model"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('TestPassword123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_user_id_is_uuid(self):
        """Test that user ID is UUID"""
        user = User.objects.create_user(**self.user_data)
        self.assertIsInstance(user.id, uuid.UUID)

    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected = f"<User(id={user.id}, email={user.email}, username={user.username})>"
        self.assertEqual(str(user), expected)

    def test_user_repr(self):
        """Test user repr"""
        user = User.objects.create_user(**self.user_data)
        expected = f"<User(id={user.id}, email={user.email}, username={user.username})>"
        self.assertEqual(repr(user), expected)

    def test_unique_username(self):
        """Test that username must be unique"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)

    def test_unique_email(self):
        """Test that email must be unique"""
        User.objects.create_user(**self.user_data)
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'different_user'
        with self.assertRaises(Exception):
            User.objects.create_user(**duplicate_data)

    def test_user_ordering(self):
        """Test that users are ordered by date_joined descending"""
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Pass123'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Pass123'
        )
        users = list(User.objects.all())
        self.assertEqual(users[0].id, user2.id)
        self.assertEqual(users[1].id, user1.id)

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_is_active_default(self):
        """Test that user is active by default"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_active)

    def test_user_is_staff_default(self):
        """Test that user is not staff by default"""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_staff)

    def test_user_is_superuser_default(self):
        """Test that user is not superuser by default"""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_superuser)

    def test_user_meta_verbose_name(self):
        """Test user meta verbose name"""
        self.assertEqual(User._meta.verbose_name, 'User')
        self.assertEqual(User._meta.verbose_name_plural, 'Users')

    def test_user_password_hashing(self):
        """Test that password is hashed"""
        user = User.objects.create_user(**self.user_data)
        self.assertNotEqual(user.password, 'TestPassword123')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))

    def test_user_with_optional_fields(self):
        """Test creating user with optional fields"""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='TestPassword123',
            first_name='',
            last_name=''
        )
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')

