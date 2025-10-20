"""Tests for Contact Models"""
from django.test import TestCase
from contact.models import Contact
import uuid
import json


class ContactModelTests(TestCase):
    """Test cases for Contact model"""

    def setUp(self):
        """Set up test data"""
        self.contact_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone_number': '+1234567890',
            'subject': 'Test Subject',
            'message': 'This is a test message',
            'organization': 'Test Org'
        }

    def test_create_contact(self):
        """Test creating a contact"""
        contact = Contact.objects.create(**self.contact_data)
        self.assertEqual(contact.full_name, 'John Doe')
        self.assertEqual(contact.email, 'john@example.com')
        self.assertEqual(contact.status, 'new')

    def test_contact_id_is_uuid(self):
        """Test that contact ID is UUID"""
        contact = Contact.objects.create(**self.contact_data)
        self.assertIsInstance(contact.id, uuid.UUID)

    def test_contact_status_choices(self):
        """Test contact status choices"""
        contact = Contact.objects.create(**self.contact_data, status='contacted')
        self.assertEqual(contact.status, 'contacted')

    def test_contact_default_status(self):
        """Test contact default status is 'new'"""
        contact = Contact.objects.create(**self.contact_data)
        self.assertEqual(contact.status, 'new')

    def test_contact_string_representation(self):
        """Test contact string representation"""
        contact = Contact.objects.create(**self.contact_data)
        expected = f"<Contact(id={contact.id}, email={contact.email}, full_name={contact.full_name})>"
        self.assertEqual(str(contact), expected)

    def test_contact_repr(self):
        """Test contact repr"""
        contact = Contact.objects.create(**self.contact_data)
        expected = f"<Contact(id={contact.id}, email={contact.email}, full_name={contact.full_name})>"
        self.assertEqual(repr(contact), expected)

    def test_contact_timestamps(self):
        """Test contact timestamps"""
        contact = Contact.objects.create(**self.contact_data)
        self.assertIsNotNone(contact.created_at)
        self.assertIsNotNone(contact.updated_at)

    def test_contact_optional_fields(self):
        """Test contact with optional fields"""
        contact = Contact.objects.create(
            full_name='Jane Doe',
            email='jane@example.com',
            subject='Test',
            message='Test message'
        )
        self.assertIsNone(contact.phone_number)
        self.assertIsNone(contact.organization)

    def test_get_user_agent_valid_json(self):
        """Test parsing valid user agent JSON"""
        user_agent_data = {'browser': 'Chrome', 'os': 'Windows'}
        contact = Contact.objects.create(
            **self.contact_data,
            user_agent=json.dumps(user_agent_data)
        )
        parsed = contact.get_user_agent()
        self.assertEqual(parsed['browser'], 'Chrome')

    def test_get_user_agent_invalid_json(self):
        """Test parsing invalid user agent JSON"""
        contact = Contact.objects.create(
            **self.contact_data,
            user_agent='invalid json'
        )
        parsed = contact.get_user_agent()
        self.assertEqual(parsed, {})

    def test_get_user_agent_none(self):
        """Test parsing None user agent"""
        contact = Contact.objects.create(**self.contact_data)
        parsed = contact.get_user_agent()
        self.assertEqual(parsed, {})

    def test_contact_ordering(self):
        """Test that contacts are ordered by created_at descending"""
        import time
        contact1 = Contact.objects.create(**self.contact_data)
        time.sleep(0.01)  # Small delay to ensure different timestamps
        contact2_data = self.contact_data.copy()
        contact2_data['email'] = 'jane@example.com'
        contact2 = Contact.objects.create(**contact2_data)
        contacts = list(Contact.objects.all())
        # Most recent should be first (descending order)
        self.assertEqual(contacts[0].id, contact2.id)
        self.assertEqual(contacts[1].id, contact1.id)

    def test_contact_meta_verbose_name(self):
        """Test contact meta verbose name"""
        self.assertEqual(Contact._meta.verbose_name, 'Contact')
        self.assertEqual(Contact._meta.verbose_name_plural, 'Contacts')

    def test_contact_with_file(self):
        """Test contact with file attachment"""
        contact = Contact.objects.create(
            **self.contact_data,
            file_attached='path/to/file.pdf'
        )
        self.assertEqual(contact.file_attached, 'path/to/file.pdf')

    def test_contact_with_ip_address(self):
        """Test contact with IP address"""
        contact = Contact.objects.create(
            **self.contact_data,
            ip_address='192.168.1.1'
        )
        self.assertEqual(contact.ip_address, '192.168.1.1')

    def test_contact_preferred_contact_method(self):
        """Test contact preferred contact method"""
        contact = Contact.objects.create(
            **self.contact_data,
            preferred_contact_method='email'
        )
        self.assertEqual(contact.preferred_contact_method, 'email')

