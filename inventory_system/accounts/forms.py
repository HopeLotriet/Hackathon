from django import forms
from django.forms import ModelForm, ChoiceField, Select, Form
from .models import Inventory, Order, Invoice
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class InventoryUpdateForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ["name", "cost_per_item", "quantity_in_stock", "quantity_sold"]


class AddInventoryForm(ModelForm):
    barcode = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'Barcode'}))

    class Meta:
        model = Inventory
        fields = ["name", "cost_per_item", "quantity_in_stock", "quantity_sold", "barcode"]

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

class RegistrationForm(UserCreationForm):
    # Add additional fields if necessary
    # For example: email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
