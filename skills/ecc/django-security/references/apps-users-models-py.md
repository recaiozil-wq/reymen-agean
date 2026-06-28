---
skill_id: 9e80bfd161a5
usage_count: 1
last_used: 2026-06-16
---
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model for better security."""

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = 'email'  # Use email as username
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email