# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_types = [
        ('farmer', 'Farmer'),
        ('customer', 'Customer'),
        ('retail', 'Retail'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=user_types, default='customer')
