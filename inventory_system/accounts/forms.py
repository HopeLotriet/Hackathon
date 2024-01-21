from django import forms
from django.forms import ModelForm, ChoiceField, Select, Form
from .models import Inventory, Order, Invoice, SalesData
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class InventoryUpdateForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ["name", "cost_per_item", "quantity_in_stock", "quantity_sold", "image"]


class AddInventoryForm(ModelForm):
    barcode = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Barcode'}))
    image = forms.ImageField(required=False)

    class Meta:
        model = Inventory
        fields = ["name", "cost_per_item", "quantity_in_stock", "quantity_sold", "barcode", "image"]

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

class UserInputForm(forms.Form):
    user_input = forms.CharField(label='user_name', max_length=100)

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'billing_address',
            'payment_method',
            'notes',
        ]

    def clean(self):
        cleaned_data = super().clean()
        payment_status = cleaned_data.get('payment_status')
        payment_due_date = cleaned_data.get('payment_due_date')

       
        if payment_status == 'paid' and not payment_due_date:
            self.add_error('payment_due_date', 'Payment due date is required for paid invoices.')

class SalesDataUploadForm(forms.Form):
    sales_data = forms.FileField()
