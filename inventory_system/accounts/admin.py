from django.contrib import admin
from .models import Catalog, Inventory, CustomerPermissions, StaffPermissions, SupplierPermissions, accountantPermissions, SalesData, Subscriber, Rating, Testimonial

# Register your models here.
admin.site.register(Catalog)
admin.site.register(Inventory)
admin.site.register(CustomerPermissions)
admin.site.register(StaffPermissions)
admin.site.register(SupplierPermissions)
admin.site.register(SalesData)
admin.site.register(Subscriber)
admin.site.register(Rating)
admin.site.register(Testimonial)