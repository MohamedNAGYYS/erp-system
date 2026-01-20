from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class CustomerUser(AbstractUser):
    """User Model for ERP Sys"""
    ROLE_CHOICES = [
        ('superadmin', 'Super Administrator'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('sales', 'Sales Representative'),
        ('purchase', 'Purchase Officer'),
        ('inventory', 'Inventory Manager'),
        ('accountant', 'Accountant'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'