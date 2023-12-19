from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Inventory, Order, Invoice , cart, OrderAmount
from django.shortcuts import get_object_or_404
from .forms import InventoryUpdateForm, AddInventoryForm, OrderForm, UpdateStatusForm, UserInputForm, InvoiceForm, CreateUserForm
from django.contrib import messages
import io
from django_pandas.io import read_frame
import pandas as pd
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
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import uuid
from django.utils import timezone
from datetime import datetime, timedelta

def home(request):
    return render(request, 'accounts/home.html')

def registration(request):
    group_name = ''  # Provide a default value

    if request.method == "POST":
        User = get_user_model()
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            role = form.cleaned_data['role']

            if role == 'customer':
                group_name = 'customer'
            elif role == 'admin':
                group_name = 'admin'
            elif role == 'supplier':
                group_name = 'supplier'
            elif role == 'accountant':
                group_name = 'accountant'

            try:
                group = Group.objects.get(name=group_name)
            except ObjectDoesNotExist:
                # Create the group if it doesn't exist
                group = Group.objects.create(name=group_name)

            user.groups.add(group)

            return redirect('login')

    else:
        form = CreateUserForm()

    context = {
        'form': form,
    }
    return render(request, 'system/registration.html', context)


def products(request):
    inventories = Inventory.objects.all()
    context = {
        "title": "Inventory List",
        "inventories": inventories
    }
    return render(request, 'accounts/products.html', context=context)

@login_required()
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

@login_required()
def per_product(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        'inventory' : inventory
    }
    return render(request, "accounts/per_product.html", context=context)

@login_required()
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

@login_required()
def delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.success(request, "Inventory Deleted")
    return redirect('stock')

@login_required()
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

@login_required()
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
    df['quantity_sold'] = df['quantity_sold'].astype(int)
    best_performing_product_df = df.groupby(by="name").sum().sort_values(by="quantity_sold")
    colors = px.colors.qualitative.Set3[:len(best_performing_product_df)]
    best_performing_product = px.bar(best_performing_product_df, 
                                    x = best_performing_product_df.index, 
                                    y = best_performing_product_df.quantity_sold,
                                    color=best_performing_product_df.index,
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

#adding items to cart for customers
def view_cart(request):
    cart_items = cart.objects.all()
    amount = OrderAmount.objects.all()
    return render(request, 'accounts/cart.html', {'items': cart_items, 'amount': amount})

def add_to_cart(request, item_id):
    #add items to cart
    item = get_object_or_404(Inventory, id=item_id)
    item_name = item.name
    item_cost = item.cost_per_item
    quantities = 1
    

    new_entry = cart(item = item_name, cost_per_item = item_cost, quantity=quantities, total_amount=item_cost)
    new_entry.save()

   # Retrieve all instances of OrderAmount
    existing_amounts = OrderAmount.objects.all()

    if existing_amounts.exists():
        existing_amount = existing_amounts.first()
        existing_amount.amount_due += item_cost
        existing_amount.save()
    else:
        # If no instances exist, create a new one
        new_price = OrderAmount(amount_due=item_cost)
        new_price.save()

    messages.success(request, "Item added to cart")
    return redirect("products")

def delete_from_cart(request, item_id):
    #remove from cart
    item = get_object_or_404(cart, id=item_id)
    item_cost = item.total_amount
    
    #decrease total price
    existing_amount = OrderAmount.objects.all().first()
    existing_amount.amount_due -= item_cost
    
    
    item.delete()
    existing_amount.save() 
    
    messages.success(request, "Item removed from cart")

  
    return redirect('view_cart')

def increase_cart_quantity(request, item_id):
    item = get_object_or_404(cart, id=item_id)
    
    #increase quantity
    new_quantity=item.quantity
    new_quantity = new_quantity + 1
    item.quantity = new_quantity

    #increase total_amount
    price = item.cost_per_item
    new_amount = item.total_amount
    new_amount = new_amount + price
    item.total_amount = new_amount

    item.save()

    #increase total price
    existing_amount = OrderAmount.objects.all().first()
    existing_amount.amount_due += price
    existing_amount.save()
    
    
    return redirect("view_cart")

def decrease_cart_quantity(request, item_id):
    item = get_object_or_404(cart, id=item_id)
    existing_amount = OrderAmount.objects.all().first()
    
    new_quantity=item.quantity
    new_amount = item.total_amount
    price = item.cost_per_item

    if new_quantity > 0 and new_amount > 0  and existing_amount.amount_due > 0:
        #decrease quantity
        new_quantity = new_quantity - 1
        item.quantity = new_quantity

        #decrease price
        new_amount = new_amount - price
        item.total_amount = new_amount

        #decrease total price
        existing_amount.amount_due -= price
        
        item.save()
        existing_amount.save()

    elif new_quantity <=0 and new_amount <= 0:
        item.delete()

    elif existing_amount.amount_due <= 0:
        item.delete()
        all_amounts = OrderAmount.objects.all()
        all_amounts.delete()

    return redirect("view_cart")

def delete_cart(request):
    cart_entry = cart.objects.all()
    cart_entry.delete()

    cart_amount = OrderAmount.objects.all()
    cart_amount.delete()
    messages.success(request, "Cart cleared!")
    return redirect("view_cart")


#Order management
@login_required()
def order_list(request):
    order_lists = Order.objects.all()
    print(order_lists)
    return render(request, 'accounts/order_list.html', {'orders': order_lists})

@login_required()
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

@login_required()
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

@login_required()
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


@login_required()
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


def marketing(request):
    context = {}
    return render(request, 'accounts/marketing.html', context)

def profile(request):
    context = {}
    return render(request, 'accounts/profile.html', context)

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

@login_required()
def invoicing(request):
    invoices = Invoice.objects.all()

    context = {
        'invoices': invoices,
    }

    return render(request, 'accounts/invoicing.html', context)

@login_required()

@login_required()
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            return redirect('order_details')
    else:
        form = InvoiceForm()

    context = {'form': form}
    return render(request, 'accounts/create_invoice.html', context)

def order_details(request):
    # Get the last created invoice
    invoice = Invoice.objects.all().last()

    #fetch required information
    #billing name
    logged_user = request.user
    customer_name = f"{logged_user.first_name} {logged_user.last_name}"

    # order id
    prefix = 'ORDER'
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_part = uuid.uuid4().hex[:6].upper()
    order_id = f'{prefix}-{timestamp}-{random_part}'

    #billing email
    email = logged_user.email

    #payment date
    due_date = datetime.now().date() + timedelta(days=7)

    #Amount due
    order_amount = OrderAmount.objects.all().first()
    payment_amount = order_amount.amount_due

    # Update invoice entry
    invoice.order = order_id
    invoice.billing_name = customer_name
    invoice.billing_email = email
    invoice.payment_due_date = due_date
    invoice.total_amount = payment_amount
    invoice.save()
    return redirect('invoice_detail')

@login_required()
def invoice_detail(request):
    invoice = Invoice.objects.all().last()
    context = {'invoice': invoice}
    return render(request, 'accounts/invoice_detail.html', context)


@login_required()
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

@login_required()
def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    return redirect('invoicing')

@login_required()
def mark_invoice_as_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.payment_status = 'paid'
    invoice.save()
    return redirect('invoice_detail', pk=pk)

def invoice_pdf(request, pk):
    #get the invoice
    invoice = get_object_or_404(Invoice, pk=pk)
    # Create Bytestream buffer
    buf = io.BytesIO()
    # Create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # Create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    # Add invoice details to the PDF
    textob.textLine(f"Invoice Number: {invoice.pk}")
    textob.textLine(f"Total Amount: {invoice.total_amount}")
    textob.textLine(f"Billing Name: {invoice.billing_name}")
    textob.textLine(f"Billing Address: {invoice.billing_address}")
    textob.textLine(f"Billing Email: {invoice.billing_email}")
    textob.textLine(f"Payment Status: {invoice.payment_status}")
    textob.textLine(f"Payment Method: {invoice.payment_method}")
    textob.textLine(f"Payment Due Date: {invoice.payment_due_date}")
    textob.textLine(f"Notes: {invoice.notes}")
    textob.textLine(f"Status: {invoice.status}")

    # Get the related order details
    order = invoice.order
    textob.textLine(f"Order ID: {order.id}")
    textob.textLine(f"Order Date: {order.order_date}")
    textob.textLine(f"Product: {order.product}")
    textob.textLine(f"Customer: {order.customer}")
    textob.textLine(f"Quantity Ordered: {order.quantity_ordered}")
    textob.textLine(f"Order Status: {order.order_status}")

    orderitems = order.orderitem_set.all()
    for item in orderitems:
        textob.textLine(f"Item: {item.name}")
        textob.textLine(f"Quantity: {item.quantity}")
        textob.textLine(f"Cost Per Item: {item.cost_per_item}")


    # Finish Up
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)


    # Return the PDF as a response
    return FileResponse(buf, as_attachment=True, filename=f'invoice_{invoice.pk}_pdf.pdf')

