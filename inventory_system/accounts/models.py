# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail


class CustomUser(AbstractUser):
    user_types = [
        ('farmer', 'Farmer'),
        ('customer', 'Customer'),
        ('retail', 'Retail'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=user_types, default='customer')


class Inventory(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    cost_per_item = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)
    quantity_in_stock = models.IntegerField(null=False, blank=False)
    quantity_sold = models.IntegerField(null=False, blank=False)
    sales = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)
    stock_date = models.DateField(auto_now_add=True)
    last_sales_date = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    product = models.CharField(max_length=100, default="")
    customer = models.CharField(max_length=100, default="")
    quantity_ordered = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id}- {self.product} - {self.customer} - {self.quantity_ordered} units - Status: {self.order_status}"