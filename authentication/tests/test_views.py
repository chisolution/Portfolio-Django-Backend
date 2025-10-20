"""Tests for Auth Views/APIs"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User


class AuthAPITests(TestCase):
    """Test cases for Auth API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )

    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123',
            'password_confirm': 'NewPass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/v1/authentication/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'NewPass123',
            'password_confirm': 'DifferentPass123'
        }
        response = self.client.post('/api/v1/authentication/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username"""
        data = {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'Pass123',
            'password_confirm': 'Pass123'
        }
        response = self.client.post('/api/v1/authentication/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123'
        }
        response = self.client.post('/api/v1/authentication/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = self.client.post('/api/v1/authentication/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        data = {
            'username': 'nonexistent',
            'password': 'Pass123'
        }
        response = self.client.post('/api/v1/authentication/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail(self):
        """Test getting user details"""
        response = self.client.get(f'/api/v1/authentication/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_get_user_detail_not_found(self):
        """Test getting non-existent user"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'/api/v1/authentication/users/{fake_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_detail_invalid_id(self):
        """Test getting user with invalid ID format"""
        response = self.client.get('/api/v1/authentication/users/invalid-id/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_users(self):
        """Test listing users"""
        response = self.client.get('/api/v1/authentication/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_list_users_pagination(self):
        """Test listing users with pagination"""
        response = self.client.get('/api/v1/authentication/users/?page=1&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_update_user_patch(self):
        """Test updating user with PATCH"""
        data = {'first_name': 'Updated'}
        response = self.client.patch(f'/api/v1/authentication/users/{self.user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_update_user_put(self):
        """Test updating user with PUT"""
        data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.put(f'/api/v1/authentication/users/{self.user.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        """Test deleting user"""
        response = self.client.delete(f'/api/v1/authentication/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_change_password_success(self):
        """Test changing password"""
        data = {
            'old_password': 'TestPass123',
            'new_password': 'NewPass123',
            'new_password_confirm': 'NewPass123'
        }
        response = self.client.post(
            f'/api/v1/authentication/users/{self.user.id}/change-password/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old(self):
        """Test changing password with wrong old password"""
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPass123',
            'new_password_confirm': 'NewPass123'
        }
        response = self.client.post(
            f'/api/v1/authentication/users/{self.user.id}/change-password/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_user(self):
        """Test activating user"""
        self.user.is_active = False
        self.user.save()
        response = self.client.post(f'/api/v1/authentication/users/{self.user.id}/activate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_active'])

    def test_deactivate_user(self):
        """Test deactivating user"""
        response = self.client.post(f'/api/v1/authentication/users/{self.user.id}/deactivate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])

