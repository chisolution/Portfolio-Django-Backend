"""Tests for Contact Repository"""
from django.test import TestCase
from contact.models import Contact
from contact.repositories import ContactRepository
import uuid


class ContactRepositoryTests(TestCase):
    """Test cases for ContactRepository"""

    def setUp(self):
        """Set up test data"""
        self.repo = ContactRepository()
        self.contact1 = Contact.objects.create(
            full_name='John Doe',
            email='john@example.com',
            subject='Test 1',
            message='Test message 1'
        )
        self.contact2 = Contact.objects.create(
            full_name='Jane Doe',
            email='jane@example.com',
            subject='Test 2',
            message='Test message 2',
            status='contacted'
        )

    def test_create_contact(self):
        """Test creating a contact via repository"""
        contact = self.repo.create(
            full_name='Bob Smith',
            email='bob@example.com',
            subject='Test',
            message='Test message'
        )
        self.assertIsNotNone(contact)
        self.assertEqual(contact.full_name, 'Bob Smith')

    def test_get_by_id(self):
        """Test getting contact by ID"""
        contact = self.repo.get_by_id(self.contact1.id)
        self.assertIsNotNone(contact)
        self.assertEqual(contact.id, self.contact1.id)

    def test_get_by_id_not_found(self):
        """Test getting non-existent contact by ID"""
        fake_id = uuid.uuid4()
        contact = self.repo.get_by_id(fake_id)
        self.assertIsNone(contact)

    def test_get_all(self):
        """Test getting all contacts"""
        contacts = self.repo.get_all()
        self.assertEqual(len(contacts), 2)

    def test_get_by_email(self):
        """Test getting contact by email"""
        contacts = self.repo.get_by_email('john@example.com')
        self.assertIsNotNone(contacts)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].email, 'john@example.com')

    def test_get_by_email_not_found(self):
        """Test getting non-existent contact by email"""
        contacts = self.repo.get_by_email('nonexistent@example.com')
        self.assertEqual(len(contacts), 0)

    def test_get_by_status(self):
        """Test getting contacts by status"""
        contacts = self.repo.get_by_status('new')
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].full_name, 'John Doe')

    def test_update_contact(self):
        """Test updating contact"""
        contact = self.repo.update(self.contact1.id, status='contacted')
        self.assertIsNotNone(contact)
        self.assertEqual(contact.status, 'contacted')

    def test_delete_contact(self):
        """Test deleting contact"""
        contact_id = self.contact1.id
        result = self.repo.delete(contact_id)
        self.assertTrue(result)
        contact = self.repo.get_by_id(contact_id)
        self.assertIsNone(contact)

    def test_search_contacts(self):
        """Test searching contacts"""
        contacts = self.repo.search('John')
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0].full_name, 'John Doe')

    def test_search_contacts_by_email(self):
        """Test searching contacts by email"""
        contacts = self.repo.search('jane@example.com')
        self.assertEqual(len(contacts), 1)

    def test_get_paginated(self):
        """Test getting paginated contacts"""
        result = self.repo.get_paginated(1, 10)
        self.assertEqual(result['total'], 2)
        self.assertEqual(len(result['items']), 2)

    def test_count_by_status(self):
        """Test counting contacts by status"""
        count = self.repo.count_by_status('new')
        self.assertEqual(count, 1)

    def test_count_by_status_all(self):
        """Test counting all contacts by status"""
        count_new = self.repo.count_by_status('new')
        count_contacted = self.repo.count_by_status('contacted')
        self.assertEqual(count_new + count_contacted, 2)

    def test_get_recent_contacts(self):
        """Test getting recent contacts"""
        contacts = self.repo.get_all()
        self.assertEqual(len(contacts), 2)

    def test_search_empty_result(self):
        """Test searching with no results"""
        contacts = self.repo.search('nonexistent')
        self.assertEqual(len(contacts), 0)

    def test_get_by_status_empty(self):
        """Test getting contacts with status that has no results"""
        contacts = self.repo.get_by_status('closed')
        self.assertEqual(len(contacts), 0)

