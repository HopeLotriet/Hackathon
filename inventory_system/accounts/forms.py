from django.forms import ModelForm, ChoiceField, Select, Form
from .models import Inventory, Order

class InventoryUpdateForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ["name", "cost_per_item", "quantity_in_stock", "quantity_sold"]


class AddInventoryForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ["name", "cost_per_item", "quantity_in_stock", "quantity_sold"]

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'customer','quantity_ordered']

class UpdateStatusForm(Form):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    new_status = ChoiceField(choices=STATUS_CHOICES, widget=Select(attrs={'class': 'form-control'}))