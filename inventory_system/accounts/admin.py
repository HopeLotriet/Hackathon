from django.contrib import admin
from .models import Inventory, CustomerPermissions, StaffPermissions, SupplierPermissions, accountantPermissions, SalesData, Subscriber

# Register your models here.
admin.site.register(Inventory)
admin.site.register(CustomerPermissions)
admin.site.register(StaffPermissions)
admin.site.register(SupplierPermissions)
admin.site.register(accountantPermissions)
admin.site.register(SalesData)
admin.site.register(Subscriber)
