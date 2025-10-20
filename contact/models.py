from django.db import models
from django.contrib.auth.models import User
import uuid
import json

# Create your models here.

class Contact(models.Model):
    """Contact Submission Model"""

    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
        )
    full_name = models.CharField(
        max_length=100,
        verbose_name="Full Name"
        )
    email = models.EmailField(
        max_length=100, db_index=True,
        verbose_name="Email"
        )
    phone_number = models.CharField(
        max_length=100, db_index=True,
        blank=True, null=True,
        verbose_name="Phone Number"
        )
    subject = models.CharField(
        max_length=100,
        verbose_name="Subject"
        )
    message = models.TextField(
        verbose_name="Message"
        )
    file_attached = models.FileField(
        upload_to='contact/',
        max_length=500,
        blank=True, null=True,
        verbose_name="File Attached"
        )
    preferred_contact_method = models.CharField(
        max_length=30, null=True,
        verbose_name="Preferred Method"
        )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        max_length=60,
        verbose_name="IP Address"
        )
    user_agent = models.TextField(
        null=True, blank=True,
        verbose_name="User Agent"
        )
    organization = models.CharField(
        max_length=100, null=True,
        verbose_name="Organization"
        )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES,
        default='new', db_index=True,
        verbose_name="Status"
        )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
        )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
        )
    

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
    
    def get_user_agent(self):
        """Parse user agent JSON string to dict"""
        try:
            return json.loads(self.user_agent) if self.user_agent else {}
        except (json.JSONDecodeError, TypeError):
            return {}
         
    def __str__(self):
        return f"<Contact(id={self.id}, email={self.email}, full_name={self.full_name})>"

    def __repr__(self):
        return self.__str__()
