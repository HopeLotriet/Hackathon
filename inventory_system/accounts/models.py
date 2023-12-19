# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User,  Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


class CustomUser(AbstractUser):
    user_types = [
        ('accountant', 'Accountant'),
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
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
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)

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
    
class Invoice(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    billing_name = models.CharField(max_length=255)
    billing_address = models.TextField()
    billing_email = models.EmailField()

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_due_date = models.DateField(blank=True, null=True)

    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    


    def __str__(self):
        return f"Invoice #{self.pk}"
    
# Create your models here.
class CustomerPermissions(models.Model):
    class Meta:
        permissions = (
            ("view_cart", "Can view cart"),
            ("add_to_cart", "Can add items to cart"),
            ("remove_from_cart", "Can remove items from cart"),
            ("update_cart", "Can update cart"),
            ("clear_cart", "Can clear cart"),
            ("checkout", "Can proceed to checkout"),
            ("view_order_history", "Can view order history"),
            ("view_product_details", "Can view product details"),
        )

class StaffPermissions(models.Model):
    class Meta:
        permissions = (
            ("view_dashboard", "Can view dashboard"),
            ("manage_orders", "Can manage orders"),
            ("manage_products", "Can manage products"),
            ("view_products", "Manage products"),
            ("view_inventory", "Manage inventory")
            # Add more permissions as needed
        )

class SupplierPermissions(models.Model):
    class Meta:
        permissions = (
            ("view_inventory", "Manage inventory"),
            ("add_products", "Add products to inventory")
            # Add more permissions as needed
        )

class accountantPermissions(models.Model):
  
    class Meta:
        permissions = (
            ("view_records", "Manage records"),
            ("add_record", "Add record"),
            ("update_record", "Update records"),
            # Add more permissions as needed
        )

class cart(models.Model):
    item = models.CharField(max_length=100, null=False, blank=False)
    cost_per_item = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    total_amount = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)

    def __str__(self) -> str:
        return self.item
    
class OrderAmount(models.Model):
    amount_due = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)

    def __str__(self) -> str:
        return self.amount_due