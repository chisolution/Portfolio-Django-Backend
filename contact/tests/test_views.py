"""Tests for Contact Views/APIs"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from contact.models import Contact


class ContactAPITests(TestCase):
    """Test cases for Contact API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.contact = Contact.objects.create(
            full_name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='This is a test message'
        )

    def test_create_contact_success(self):
        """Test successful contact creation"""
        data = {
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        response = self.client.post('/api/v1/contact/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['full_name'], 'Jane Doe')

    def test_create_contact_invalid_email(self):
        """Test contact creation with invalid email"""
        data = {
            'full_name': 'Jane Doe',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        response = self.client.post('/api/v1/contact/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contact_short_message(self):
        """Test contact creation with short message"""
        data = {
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'subject': 'Test',
            'message': 'Short'
        }
        response = self.client.post('/api/v1/contact/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_contacts(self):
        """Test listing contacts"""
        response = self.client.get('/api/v1/contact/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['count'], 1)

    def test_list_contacts_pagination(self):
        """Test listing contacts with pagination"""
        response = self.client.get('/api/v1/contact/?page=1&page_size=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data['data'])

    def test_list_contacts_filter_by_status(self):
        """Test listing contacts filtered by status"""
        response = self.client.get('/api/v1/contact/?status=new')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['count'], 1)

    def test_get_contact_detail(self):
        """Test getting contact details"""
        response = self.client.get(f'/api/v1/contact/{self.contact.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['full_name'], 'John Doe')

    def test_get_contact_detail_not_found(self):
        """Test getting non-existent contact"""
        fake_id = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'/api/v1/contact/{fake_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_contact_detail_invalid_id(self):
        """Test getting contact with invalid ID format"""
        response = self.client.get('/api/v1/contact/invalid-id/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_contact_patch(self):
        """Test updating contact with PATCH"""
        data = {'status': 'contacted'}
        response = self.client.patch(f'/api/v1/contact/{self.contact.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'contacted')

    def test_update_contact_put(self):
        """Test updating contact with PUT"""
        data = {'status': 'closed'}
        response = self.client.put(f'/api/v1/contact/{self.contact.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_contact(self):
        """Test deleting contact"""
        response = self.client.delete(f'/api/v1/contact/{self.contact.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_contacts(self):
        """Test searching contacts"""
        response = self.client.get('/api/v1/contact/search/?query=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data['data'])

    def test_search_contacts_no_query(self):
        """Test searching without query parameter"""
        response = self.client.get('/api/v1/contact/search/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_contacts_with_status_filter(self):
        """Test searching contacts with status filter"""
        response = self.client.get('/api/v1/contact/search/?query=John&status=new')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact_statistics(self):
        """Test getting contact statistics"""
        response = self.client.get('/api/v1/contact/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data['data'])

    def test_create_contact_with_optional_fields(self):
        """Test creating contact with optional fields"""
        data = {
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone_number': '+1234567890',
            'subject': 'Test Subject',
            'message': 'This is a test message',
            'organization': 'Test Org'
        }
        response = self.client.post('/api/v1/contact/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['phone_number'], '+1234567890')

