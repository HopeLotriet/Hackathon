from django.contrib import admin
from .models import Inventory, Order, Invoice

# Register your models here.
admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(Invoice)

