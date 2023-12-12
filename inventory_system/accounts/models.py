# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
# from products.models import Product

class CustomUser(AbstractUser):
    user_types = [
        ('farmer', 'Farmer'),
        ('customer', 'Customer'),
        ('retail', 'Retail'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=user_types, default='customer')


# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity = models.PositiveIntegerField()

# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('shipped', 'Shipped'),
#         ('delivered', 'Delivered'),
#     ]

#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     customer = models.ForeignKey(User, on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     timestamp = models.DateTimeField(auto_now_add=True)

# class Supplier(models.Model):
#     name = models.CharField(max_length=255)
#     # Add other supplier-related fields

# @receiver(post_save, sender=Order)
# def send_order_email(sender, instance, **kwargs):
#     subject = 'Order Confirmation'
#     message = f'Your order for {instance.product.name} has been {instance.status}.'
#     from_email = 'your@email.com'
#     to_email = instance.customer.email
#     send_mail(subject, message, from_email, [to_email])

# # Add other models as needed (e.g., Customer, Invoice, etc.)

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