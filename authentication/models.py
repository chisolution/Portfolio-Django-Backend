from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Create your models here.

class User(AbstractUser):
    """Custom User model with UUID primary key"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)


    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    def __repr__(self):
        return self.__str__()
