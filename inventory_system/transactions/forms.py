from django import forms
from django.forms import formset_factory
from .models import Supplier, PurchaseBill, PurchaseItem, PurchaseBillDetails 
from accounts.models import Inventory


# form used to select a supplier
class SelectSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_deleted=False)
        self.fields['supplier'].widget.attrs.update({'class': 'textinput form-control'})
    class Meta:
        model = PurchaseBill
        fields = ['supplier']

# form used to render a single stock item form
class PurchaseItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Inventory.objects.filter(is_deleted=False)
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update({'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        self.fields['perprice'].widget.attrs.update({'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})
    class Meta:
        model = PurchaseItem
        fields = ['stock', 'quantity', 'perprice']

# formset used to render multiple 'PurchaseItemForm'
PurchaseItemFormset = formset_factory(PurchaseItemForm, extra=1)

# form used to accept the other details for purchase bill
class PurchaseDetailsForm(forms.ModelForm):
    class Meta:
        model = PurchaseBillDetails
        fields = ['eway','veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']


# form used for supplier
class SupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'textinput form-control', 'pattern' : r'/^[.@&]?[a-zA-Z0-9 ]+[ !.@&()]?[ a-zA-Z0-9!()]+/', 'title' : 'name should contain only letters and numbers and can contain special characters like .@&()! and space'})
        self.fields['phone'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '10', 'pattern': r'^(?:\+27|0)(?:\d{9}|\(\d{3}\)\s?\d{3}\s?\d{3})$', 'title': 'phone number should be 10 digits long and start with 0 or +27'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['reg_no'].widget.attrs.update({'class': 'textinput form-control', 'maxlength': '14', 'pattern' : r'(19|2[0-9])\d{2}/\d{6}/\d{2}', 'title' : 'Registration number should be in the format 19xx/xxxxxx/xx or 20xx/xxxxxx/xx'})

    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'address', 'email', 'reg_no']
        widgets = {
            'address' : forms.Textarea(
                attrs = {
                    'class' : 'textinput form-control',
                    'rows'  : '4'
                }
            )
        }