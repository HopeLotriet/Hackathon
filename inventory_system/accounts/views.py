from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Inventory, Order, Invoice
from django.shortcuts import get_object_or_404
from .forms import InventoryUpdateForm, AddInventoryForm, OrderForm, UpdateStatusForm, UserInputForm, InvoiceForm
from django.contrib import messages
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import json
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import barcode
from barcode.writer import ImageWriter
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from barcode import Code128


def home(request):
    return render(request, 'accounts/home.html')

def products(request):
    inventories = Inventory.objects.all()
    context = {
        "title": "Inventory List",
        "inventories": inventories
    }
    return render(request, 'accounts/products.html', context=context)

def stock(request):
    inventories = Inventory.objects.all()

      # Check for low stock items
    low_stock_inventory = inventories.filter(quantity_in_stock__lte=LOW_QUANTITY)

    if low_stock_inventory.exists():
        # Display a message for each low stock item
        for item in low_stock_inventory:
            messages.warning(request, f"Low stock alert: {item.name} - quantity in stock: {item.quantity_in_stock}")

    context = {
        "title": "Inventory List",
        "inventories": inventories
     }
    return render(request, 'accounts/stock.html', context=context)

LOW_QUANTITY = getattr(settings, 'LOW_QUANTITY', 5)

def per_product(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        'inventory' : inventory
    }
    return render(request, "accounts/per_product.html", context=context)

def update(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        updateForm = InventoryUpdateForm(data=request.POST)
        if updateForm.is_valid():
            inventory.name = updateForm.data['name']
            inventory.quantity_in_stock = updateForm.data['quantity_in_stock']
            inventory.quantity_sold = updateForm.data['quantity_sold']
            inventory.cost_per_item = updateForm.data['cost_per_item']
            inventory.sales = float(inventory.cost_per_item) * float(inventory.quantity_sold)
            inventory.save()
            messages.success(request, "Update Successful")
            return redirect(reverse('per_product', kwargs={'pk': pk}))
    else:
        updateForm = InventoryUpdateForm(instance=inventory)

    return render(request, 'accounts/inventory_update.html', {'form' : updateForm})

def delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.success(request, "Inventory Deleted")
    return redirect('stock')

def add_product(request):
    if request.method == "POST":
        updateForm = AddInventoryForm(data=request.POST)
        if updateForm.is_valid():
            new_inventory = updateForm.save(commit=False)
            new_inventory.sales = float(updateForm.data['cost_per_item']) * float(updateForm.data['quantity_sold'])

            # Generate barcode and save it to the new inventory item
            barcode_data = new_inventory.name + " " + str(new_inventory.cost_per_item)  # You can modify this based on your barcode data
            code128 = Code128(barcode_data, writer=ImageWriter())
            image = code128.render()

            # Convert the barcode image to PNG format
            image_io = BytesIO()
            image.save(image_io, format='PNG')
            image_file = ContentFile(image_io.getvalue())
            new_inventory.barcode.save(f'barcode_{barcode_data}.png', image_file, save=False)

            new_inventory.save()

            messages.success(request, "Successfully Added Product")
            return redirect('stock')  # You can adjust the redirect URL

    else:
        updateForm = AddInventoryForm()

    return render(request, 'accounts/inventory_add.html', {'form': updateForm})


def dashboard(request):
    inventories = Inventory.objects.all()
    df = read_frame(inventories)
    
    # sales graph
    print(df.columns)
    sales_graph_df = df.groupby(by="last_sales_date", as_index=False, sort=False)['sales'].sum()
    print(sales_graph_df.sales)
    print(sales_graph_df.columns)
    sales_graph = px.line(sales_graph_df, x = sales_graph_df.last_sales_date, y = sales_graph_df.sales, title="Sales Trend")
    sales_graph = json.dumps(sales_graph, cls=plotly.utils.PlotlyJSONEncoder)

    
    # best performing product
    best_performing_product_df = df.groupby(by="name").sum().sort_values(by="quantity_sold")
    best_performing_product = px.bar(best_performing_product_df, 
                                    x = best_performing_product_df.index, 
                                    y = best_performing_product_df.quantity_sold, 
                                    title="Best Performing Product"
                                )
    best_performing_product = json.dumps(best_performing_product, cls=plotly.utils.PlotlyJSONEncoder)


    # best performing product in sales
    sales_graph_df_per_product_df = df.groupby(by="name", as_index=False, sort=False)['sales'].sum()
    best_performing_product_per_product = px.pie(sales_graph_df_per_product_df, 
                                    names = "name", 
                                    values = "sales", 
                                    title="Product Performance By Sales",
                                    # https://plotly.com/python/discrete-color/
                                    color_discrete_sequence=px.colors.qualitative.Bold,
                                )
    best_performing_product_per_product = json.dumps(best_performing_product_per_product, cls=plotly.utils.PlotlyJSONEncoder)


     # Most Product In Stock
    most_product_in_stock_df = df.groupby(by="name").sum().sort_values(by="quantity_in_stock")
    most_product_in_stock = px.pie(most_product_in_stock_df, 
                                    names = most_product_in_stock_df.index, 
                                    values = most_product_in_stock_df.quantity_in_stock, 
                                    title="Most Product In Stock"
                                )
    most_product_in_stock = json.dumps(most_product_in_stock, cls=plotly.utils.PlotlyJSONEncoder)

    context = {
        "sales_graph": sales_graph,
        "best_performing_product": best_performing_product,
        "most_product_in_stock": most_product_in_stock,
        "best_performing_product_per_product": best_performing_product_per_product
    }

    return render(request,"accounts/dashboard.html", context=context)

#Order management
def order_list(request):
    order_lists = Order.objects.all()
    print(order_lists)
    return render(request, 'accounts/order_list.html', {'orders': order_lists})

def create_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            product_name = order.product
            name = order.customer
            status = ' is currently being processed'

            try:
                # Retrieve the product from the database based on the name
                inventory = Inventory.objects.get(name=product_name)

                # Retrieve the current quantity in stock
                quantity_in_stock = inventory.quantity_in_stock

                # Subtract the ordered quantity from the quantity in stock
                ordered_quantity = order.quantity_ordered
                inventory.quantity_in_stock = max(0, quantity_in_stock - ordered_quantity)

                #Automated mail update
                email_body = f"""
                Hello, {name}!

                Thank you for placing your order with FarmFresh.

                Please note that your order {status}.

                Best regards,
                FarmFresh
                """
                email = send_mail(
                    'Order status update',
                    email_body,
                    'from@example.com',
                    #make it dynamic once registration is complete
                    ['amogelangmonnanyana@gmail.com']  
                    )
                
                # Save the updated inventory back to the database
                inventory.save()

                # Now save the order with the updated inventory quantity in stock
                order.save()

                # Add a success message to be displayed to the user
                messages.success(request, "Order created successfully.")
                return redirect('order_list')

            except Inventory.DoesNotExist:
                messages.error(request, f"Product '{product_name}' not found in inventory.")
        else:
            messages.error(request, "Invalid order form. Please check your inputs.")

    else:
        order_form = OrderForm()
    
    return render(request, 'accounts/create_order.html', {'form': order_form, 'messages': messages.get_messages(request)})

def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    name = order.customer
    
    if request.method == 'POST':
        form = UpdateStatusForm(request.POST)
                
        if form.is_valid():
            current_status = order.order_status
            
            if current_status != 'Order canceled':
                new_status = form.cleaned_data['new_status']
                order.order_status = new_status
                order.save()

                # Generate update emails
                status = ""
                if new_status == "pending":
                    status = ' is currently being processed'
                elif new_status == "shipped":
                    status = ' has been shipped'
                else:
                    status = "is delivered"

                email_body = f"""
                Hello, {name}!

                Thank you for placing your order with FarmFresh.

                Please note that your order {status}.

                Best regards,
                FarmFresh
                """
                    
                email = send_mail(
                    'Order status update',
                    email_body,
                    'from@example.com',
                    # Make it dynamic once registration is complete
                    ['amogelangmonnanyana@gmail.com']
                )

            # Redirect in both cases
            return redirect('order_list')
            
    else:
        form = UpdateStatusForm()

    return render(request, 'accounts/update_status.html', {'form': form, 'order': order})

def order_history(request):
    previous_orders = []
    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            # Do something with the user input, for example, save it to the database
            user_name = form.cleaned_data['user_input']
            previous_orders = Order.objects.filter(customer=user_name)
    else:
        form = UserInputForm()

    return render(request, 'accounts/order_history.html', {'form':form ,'orders': previous_orders})



def return_order(request, order_id):
    current_order = get_object_or_404(Order, id=order_id)
    if current_order.order_status != "Order canceled":

        if order_history:
            returning_order = get_object_or_404(Order, id=order_id)

            product_name = returning_order.product
            inventory = get_object_or_404(Inventory, name=product_name)

            quantity_in_stock = inventory.quantity_in_stock
            returning_quantity = returning_order.quantity_ordered
            inventory.quantity_in_stock = max(0, quantity_in_stock + returning_quantity)
            inventory.save()  # Save the updated inventory

            returning_order.order_status = "Order canceled"
            returning_order.save()
    else:
        pass

    return redirect('order_history')



#to be completed
def marketing(request):
    context = {}
    return render(request, 'accounts/marketing.html', context)

def invoicing(request):
    context = {}
    return render(request, 'accounts/invoicing.html', context)

def profile(request):
    context = {}
    return render(request, 'accounts/profile.html', context)


def reports(request):
    context = {}
    return render(request, 'accounts/reports.html', context)

def about(request):
    context = {}
    return render(request, 'accounts/about.html', context)

def is_farmer(user):
    return user.groups.filter(name='Farmers').exists()

@login_required
@user_passes_test(is_farmer, login_url='/accounts/login/')
def farmer_dashboard(request):
    # Your farmer-specific view logic
    return render(request, 'accounts/farmer_dashboard.html')

def invoicing(request):
    invoices = Invoice.objects.all()

    context = {
        'invoices': invoices,
    }

    return render(request, 'accounts/invoicing.html', context)

def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()

    context = {'form': form}
    return render(request, 'accounts/create_invoice.html', context)

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {'invoice': invoice}
    return render(request, 'accounts/invoice_detail.html', context)

def edit_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('invoice_detail', pk=pk)
    else:
        form = InvoiceForm(instance=invoice)

    context = {'form': form, 'invoice': invoice}
    return render(request, 'accounts/edit_invoice.html', context)

def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    return redirect('invoicing')

def mark_invoice_as_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.payment_status = 'paid'
    invoice.save()
    return redirect('invoice_detail', pk=pk)

