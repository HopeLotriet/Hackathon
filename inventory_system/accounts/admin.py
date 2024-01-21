from django.contrib import admin
from .models import Inventory, Order, Invoice, CustomerPermissions, StaffPermissions, SupplierPermissions, accountantPermissions, cart, OrderAmount, cart_records, customerOrderHistory

# Register your models here.
admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(Invoice)
admin.site.register(CustomerPermissions)
admin.site.register(StaffPermissions)
admin.site.register(SupplierPermissions)
admin.site.register(accountantPermissions)
admin.site.register(cart)
admin.site.register(OrderAmount)
admin.site.register(cart_records)
admin.site.register(customerOrderHistory)
