# accounts/models.py
from django.db import models
from orders.models import Order


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
    image = models.ImageField(upload_to='images/', null=True, blank=True)


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


class SalesData(models.Model):
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, default=None)
    date = models.DateField()
    quantity_sold = models.IntegerField()

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    receive_marketing_emails = models.BooleanField(default=True)

    def __str__(self):
        return self.email