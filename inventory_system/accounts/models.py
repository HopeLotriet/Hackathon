# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User,  Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import json
from django.db.models import F



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
    is_deleted = models.BooleanField(default=False)
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)

     # New field to store historical sales data
    sales_data = models.JSONField(null=True, blank=True)

    def update_sales_data(self):
        # Fetch historical sales records for this inventory item
        historical_sales = Order.objects.filter(product=self).exclude(order_status='pending').order_by('order_date')

        # Update the sales_data dictionary
        sales_data = {
            'date': [record.order_date.strftime('%Y-%m-%d') for record in historical_sales],
            'quantity_sold': [record.quantity_ordered for record in historical_sales],
        }

        # Save the updated sales_data
        self.sales_data = sales_data
        self.save()

    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    order_id = models.CharField(max_length=100, default="")
    order_date = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=100, default="")
    product = models.CharField(max_length=100, default="")
    quantity_ordered = models.PositiveIntegerField(null=True)
    amount_spent = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id}- {self.order_id} - {self.product} - {self.customer} - {self.quantity_ordered} units - Status: {self.order_status}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # After saving the order, update the corresponding inventory's sales
        inventory = Inventory.objects.get(name=self.product)
        inventory.sales += self.quantity_ordered * inventory.cost_per_item
        inventory.save()
    
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

    order = models.CharField(max_length=255, default="----")
    date_created = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    billing_name = models.CharField(max_length=255)
    billing_address = models.TextField()
    billing_email = models.EmailField()

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_due_date = models.DateField(blank=True, null=True)

    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)


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
        return str(self.amount_due)
    

class customerOrderHistory(models.Model):

    order_id = models.CharField(max_length=100, default="")
    order_date = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=100, default="")
    product = models.CharField(max_length=100, default="")
    quantity_ordered = models.PositiveIntegerField(null=True)
    amount_spent = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True)
    customer_order_status = models.CharField(max_length=100, default='pending', null=True)

    def __str__(self) -> str:
        return str(self.order_id)
    
class cart_records(models.Model):

    item = models.CharField(max_length=100, null=False, blank=False)
    cost_per_item = models.DecimalField(max_digits=19, decimal_places=2, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    total_amount = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=False)
     
    def __str__(self) -> str:
        return str(self.item)
    

class SalesData(models.Model):
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, default=None)
    date = models.DateField()
    quantity_sold = models.IntegerField()


@receiver(post_save, sender=Order)
def update_inventory_sales(sender, instance, **kwargs):
    inventory = Inventory.objects.get(name=instance.product)
    inventory.sales += instance.quantity_ordered * inventory.cost_per_item
    inventory.save()

post_save.connect(update_inventory_sales, sender=Order) 