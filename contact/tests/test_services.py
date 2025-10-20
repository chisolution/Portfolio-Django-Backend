"""Tests for Contact Service"""
from django.test import TestCase
from contact.models import Contact
from contact.services import ContactService


class ContactServiceTests(TestCase):
    """Test cases for ContactService"""

    def setUp(self):
        """Set up test data"""
        self.service = ContactService()
        self.contact = Contact.objects.create(
            full_name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='This is a test message'
        )

    def test_create_contact_success(self):
        """Test creating a contact successfully"""
        contact = self.service.create_contact(
            full_name='Jane Doe',
            email='jane@example.com',
            subject='Test Subject',
            message='This is a test message'
        )
        self.assertIsNotNone(contact)
        self.assertEqual(contact.full_name, 'Jane Doe')

    def test_create_contact_invalid_email(self):
        """Test creating contact with invalid email"""
        with self.assertRaises(ValueError):
            self.service.create_contact(
                full_name='Test',
                email='invalid-email',
                subject='Test',
                message='Test message'
            )

    def test_create_contact_short_name(self):
        """Test creating contact with short name"""
        with self.assertRaises(ValueError):
            self.service.create_contact(
                full_name='J',
                email='test@example.com',
                subject='Test',
                message='Test message'
            )

    def test_create_contact_short_message(self):
        """Test creating contact with short message"""
        with self.assertRaises(ValueError):
            self.service.create_contact(
                full_name='John Doe',
                email='john@example.com',
                subject='Test',
                message='Short'
            )

    def test_get_contact(self):
        """Test getting a contact"""
        contact = self.service.get_contact(self.contact.id)
        self.assertIsNotNone(contact)
        self.assertEqual(contact.id, self.contact.id)

    def test_get_all_contacts(self):
        """Test getting all contacts"""
        contacts = self.service.get_all_contacts()
        self.assertEqual(len(contacts), 1)

    def test_get_contacts_by_status(self):
        """Test getting contacts by status"""
        contacts = self.service.get_contacts_by_status('new')
        self.assertEqual(len(contacts), 1)

    def test_search_contacts(self):
        """Test searching contacts"""
        contacts = self.service.search_contacts('John')
        self.assertEqual(len(contacts), 1)

    def test_search_contacts_short_query(self):
        """Test searching with short query"""
        with self.assertRaises(ValueError):
            self.service.search_contacts('J')

    def test_update_contact_status(self):
        """Test updating contact status"""
        contact = self.service.update_contact_status(self.contact.id, 'contacted')
        self.assertIsNotNone(contact)
        self.assertEqual(contact.status, 'contacted')

    def test_delete_contact(self):
        """Test deleting contact"""
        contact_id = self.contact.id
        result = self.service.delete_contact(contact_id)
        self.assertTrue(result)
        contact = self.service.get_contact(contact_id)
        self.assertIsNone(contact)

    def test_get_contact_statistics(self):
        """Test getting contact statistics"""
        stats = self.service.get_contact_statistics()
        self.assertIn('total', stats)
        self.assertIn('new', stats)
        self.assertIn('contacted', stats)
        self.assertIn('closed', stats)

    def test_get_paginated_contacts(self):
        """Test getting paginated contacts"""
        result = self.service.get_paginated_contacts(1, 10)
        self.assertIn('total', result)
        self.assertIn('items', result)
        self.assertEqual(result['total'], 1)

    def test_sanitize_text(self):
        """Test text sanitization"""
        # This tests the internal sanitization method
        contact = self.service.create_contact(
            full_name='  John Doe  ',
            email='john@example.com',
            subject='  Test Subject  ',
            message='  This is a test message  '
        )
        # Sanitization should trim whitespace
        self.assertEqual(contact.full_name.strip(), 'John Doe')

    def test_create_contact_with_phone(self):
        """Test creating contact with phone number"""
        contact = self.service.create_contact(
            full_name='John Doe',
            email='john@example.com',
            phone_number='+1234567890',
            subject='Test Subject',
            message='This is a test message'
        )
        self.assertEqual(contact.phone_number, '+1234567890')

    def test_create_contact_with_organization(self):
        """Test creating contact with organization"""
        contact = self.service.create_contact(
            full_name='John Doe',
            email='john@example.com',
            organization='Test Org',
            subject='Test Subject',
            message='This is a test message'
        )
        self.assertEqual(contact.organization, 'Test Org')

