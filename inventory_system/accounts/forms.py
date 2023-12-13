from django import forms
from django.forms import ModelForm, ChoiceField, Select, Form
from .models import Inventory, Order, Invoice


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


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'order',
            'total_amount',
            'billing_name',
            'billing_address',
            'billing_email',
            'payment_status',
            'payment_method',
            'payment_due_date',
            'notes',
            'discount_amount',
            'tax_amount',
            'status',
            'pdf_document',
        ]

        widgets = {
            'payment_due_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=Invoice.STATUS_CHOICES),
        }

    def clean(self):
        cleaned_data = super().clean()
        payment_status = cleaned_data.get('payment_status')
        payment_due_date = cleaned_data.get('payment_due_date')

       
        if payment_status == 'paid' and not payment_due_date:
            self.add_error('payment_due_date', 'Payment due date is required for paid invoices.')