from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Inventory, Order, Invoice , cart, OrderAmount, customerOrderHistory, cart_records, SalesData
from django.shortcuts import get_object_or_404
from .forms import InventoryUpdateForm, AddInventoryForm, OrderForm, UpdateStatusForm, UserInputForm, InvoiceForm, CreateUserForm, SalesDataUploadForm
from django.contrib import messages
import io
from django_pandas.io import read_frame
import pandas as pd
import plotly
import plotly.express as px
import json
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
import barcode
from barcode.writer import ImageWriter
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from barcode import Code128
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django_filters.views import FilterView
from .filters import StockFilter
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import uuid
import os
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from django.http import JsonResponse
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import csv
from .utils import perform_forecasting_analysis
from django.http import HttpResponseRedirect

def home(request):
    return render(request, 'accounts/home.html')

class StockListView(FilterView):
    filterset_class = StockFilter
    queryset = Inventory.objects.filter(is_deleted=False)
    template_name = 'stock.html'
    paginate_by = 10

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
    
    #before placing another order, clear the temporary hold of cart_record
    cart_record = cart_records.objects.all()
    cart_record.delete()
    
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

    logged_user = request.user
    print(logged_user.last_name)
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

    #block order status once it is changed to delivered
    order = get_object_or_404(Order, id=order_id)
    customer_order = get_object_or_404(customerOrderHistory, id=order_id)
    completion_status = order.order_status 

    if completion_status == "delivered" or completion_status =="Order canceled":
        return redirect("order_list")
    else:
        if request.method == 'POST':
            form = UpdateStatusForm(request.POST)
                    
            if form.is_valid():
                current_status = order.order_status
            
                if current_status != 'Order canceled':
                    #update orderlist status
                    new_status = form.cleaned_data['new_status']
                    order.order_status = new_status
                    order.save()

                    #update customer order status 
                    if new_status == 'shipped':
                        customer_order.customer_order_status = 'shipped'
                    elif new_status == 'delivered':
                        customer_order.customer_order_status = 'delivered'
                    
                    customer_order.save()

                    # Generate update emails
                    status = ""
                    if new_status == "pending":
                        status = ' is currently being processed'
                    elif new_status == "shipped":
                        status = ' has been shipped'
                    else:
                        status = "is delivered"

                    name = request.user.username
                    email_address = request.user.email
                    sender_email = settings.EMAIL_HOST_USER
                    email_body = f"""
                    Hello, {name}!

                    Thank you for placing your order with FarmFresh.

                    Please note that your order {status}.
                    

                    Best regards,
                    FarmFresh
                    """
                    # Create an EmailMessage object
                    email = EmailMessage(
                    'Order status update',
                    email_body,
                    sender_email,
                    [email_address],
                    )

                    # Send the email
                    email.send()

                # Redirect in both cases
                return redirect('order_list')
                
        else:
            form = UpdateStatusForm()

        return render(request, 'accounts/update_status.html', {'form': form, 'order': order})
    
@login_required()
def order_history(request):
    previous_orders = customerOrderHistory.objects.all()
    return render(request, 'accounts/order_history.html', {'orders': previous_orders})

@login_required()
def return_order(request, order_id):
    current_order = get_object_or_404(Order, id=order_id)
    if current_order.order_status != "Order canceled":

        if order_history:
            
            # Sum up items by name
            item_quantities = cart_records.objects.values('item').annotate(each_item_quantity=Sum('quantity'))
            print(item_quantities)

            #add each product back into the inventory
            for item in item_quantities:
                item_name = item['item']
                returning_quantity = item['each_item_quantity']
                inventory_product = get_object_or_404(Inventory, name=item_name)
                ajusted_quantity = inventory_product.quantity_in_stock + returning_quantity
                inventory_product.quantity_in_stock = ajusted_quantity
                inventory_product.save()

            #fetch product from order history and inventory and update their statuses
            returning_order = get_object_or_404(customerOrderHistory, id=order_id)
            returning_orderlist = get_object_or_404(Order, id=order_id)

            returning_orderlist.order_status = "Order canceled"
            returning_orderlist.save()
    
            returning_order.customer_order_status = "Order canceled"
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

@login_required()
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
def create_invoice(request):

    #block placement of order if another one is progress
    previous_order = Order.objects.all().last()
    previous_order_status = previous_order.order_status
    context={}
    if previous_order_status == "delivered":
        #add details for invoice fields
        if request.method == 'POST':
            form = InvoiceForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('order_details')
        else:
            form = InvoiceForm()

        context = {'form': form}

        #save cart entries before clearing
        existing_cart = cart.objects.all()

        for item in existing_cart:
            item_name = item.item
            item_cost = item.cost_per_item
            item_quantity = item.quantity
            price = item.total_amount

            cart_record = cart_records(
                item = item_name,
                cost_per_item =item_cost,
                quantity=item_quantity,
                total_amount=price
            )
            cart_record.save()
        return render(request, 'accounts/create_invoice.html', context)
    else:
        pass
        messages.warning(request, "Placing new order while one is in progress is not allowed!")
        return redirect("products")

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
            return redirect('invoice_detail')
    else:
        form = InvoiceForm(instance=invoice)

    context = {'form': form, 'invoice': invoice}
    return render(request, 'accounts/edit_invoice.html', context)

@login_required()
def delete_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()

    cart_entry = cart.objects.all()
    cart_entry.delete()

    order_amount = OrderAmount.objects.all()
    order_amount.delete()
    messages.success(request, "Order canceled")
    return redirect('products')

@login_required()
def mark_invoice_as_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.payment_status = 'paid'
    invoice.save()
    return redirect('invoice_detail', pk=pk)

#generate pdf of invoice
@login_required()
def invoice_pdf(request, pk):
    try:
        # Get the invoice
        invoice = get_object_or_404(Invoice, pk=pk)

        # Create Bytestream buffer
        buf = io.BytesIO()
        # Create a canvas
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

        # Create a text object
        inch = 72.0
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("Helvetica", 14)

        # Add invoice details to the PDF
        textob.textLine(f"Invoice Number: {invoice.pk}")
        textob.textLine(f"Total Amount: {invoice.total_amount}")
        textob.textLine(f"Payment due: {invoice.payment_due_date}")

        textob.textLine(f"Billing name: {invoice.billing_name}")
        textob.textLine(f"Billing address: {invoice.billing_address}")
        textob.textLine(f"Billing email: {invoice.billing_email}")
        textob.textLine(f"Date: {invoice.date_created}")
        textob.textLine(f"Payment method: {invoice.payment_method}")

        # ... (other invoice details)

        # Get the related order details
        order_id = invoice.order
        order_details = get_object_or_404(customerOrderHistory, order_id=order_id)
        textob.textLine(f"Order ID: {order_id}")
        textob.textLine(f"Order status: {order_details.customer_order_status}")

        # ... (other order details)

        orderitems = cart_records.objects.all() 
        textob.textLine(f"Total order quantity: {order_details.quantity_ordered}")
        for item in orderitems:
            textob.textLine(f"Item: {item.quantity} {item.item} {item.cost_per_item} {item.total_amount}")
            # ... (other order item details)

        textob.textLine(f"Delivery instructions: {invoice.notes}")
        # Finish Up
        c.drawText(textob)
        c.showPage()
        c.save()
        buf.seek(0)

        # Save the PDF to the server's filesystem
        file_name = f'invoice_{invoice.pk}_pdf.pdf'
        file_path = os.path.join('pdfs', file_name).replace('\\', '/')

        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(buf.getvalue())

        # Associate the PDF file path with the Invoice model
        invoice.pdf_file = file_path
        invoice.save()

        # Clean up: close the buffer
        buf.close()

        # Return a success response
        return HttpResponse(status=200)

    except Invoice.DoesNotExist:
        # Handle the case when the invoice is not found
        return HttpResponse("Invoice not found.", status=404)
    except Exception as e:
        # Log and handle other exceptions
        return HttpResponse("An error occurred.", status=500)

#finialise order
def confirm_order(request, pk):

    #adjust inventory table
    cart_items = cart.objects.all()

    for item in cart_items:
        product_name = item.item
        inventory = Inventory.objects.get(name=product_name)
        ordered_quantity = item.quantity
        quantity_in_stock = inventory.quantity_in_stock
        inventory.quantity_in_stock = max(0, quantity_in_stock - ordered_quantity)
        inventory.save()

    ##add order to order list :-
    #order_id
    invoice = get_object_or_404(Invoice, pk=pk)
    order = invoice.order
   

    #customer name
    customer_name =invoice.billing_name

    # list of products ordered
    grouped_cart_items = cart.objects.values('item').annotate(item_count=Count('id'))
    item_list = [f"{group['item_count']}-{group['item']}" for group in grouped_cart_items]
    all_items = ', '.join(item_list)
    
    #total quatities ordered
    total_quantity = cart.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity']

    #total amount spent
    amount = invoice.total_amount

    #save order history
    order_entry = Order(
        order_id=order, 
        customer=customer_name,
        product=all_items,
        quantity_ordered=total_quantity,
        amount_spent=amount
        )
    order_entry.save()
    
    customer_order_entry = customerOrderHistory(
        order_id=order, 
        product=all_items,
        quantity_ordered=total_quantity,
        amount_spent=amount
    )
    customer_order_entry.save()

    #Generate invoice pdf
    pdf_response = invoice_pdf(request, pk)

    if pdf_response.status_code == 200:
        pdf_success_message = "Order confirmed successfully."
        request.session['success_message'] = pdf_success_message

    #clear cart
    cart_table = cart.objects.all()
    cart_table.delete()

    order_amount = OrderAmount.objects.all().first()
    order_amount.delete()

    return redirect("confirmation_email", pk=pk)

#send confirmation email with invoice attached to the customer
def confirmation_email(request, pk):
    message = "checkout successful"

    #Fetch the invoice from database
    invoice = get_object_or_404(Invoice, pk=pk)
    generated_pdf = invoice.pdf_file.path

    #Automated mail update
    name = request.user.username
    email_address = request.user.email
    status = ' is currently being processed'
    sender_email = settings.EMAIL_HOST_USER
    email_body = f"""
    Hello, {name}!

    Thank you for placing your order with FarmFresh.

    Please note that your order {status}.
    Attached is the invoice concerning your order. Please note the payment due date. 

    Best regards,
    FarmFresh
    """
    # Create an EmailMessage object
    email = EmailMessage(
    'Order status update',
    email_body,
    sender_email,
    [email_address],
    )

    # Attach the PDF to the email
    email.attach_file(generated_pdf)

    # Send the email
    email.send()

    pdf_success_message = request.session.pop('success_message', None)

    return render(request, 'accounts/confirm_order.html', {'message': message, "pdf_message":pdf_success_message})

# for cleaning trial runs of invoice
def invoice_history(request):
    invoice_history = Invoice.objects.all()
    invoice_history.delete()
    return redirect("order_list")

#Search for something
def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        inventories = Inventory.objects.filter(name__contains=searched)

        return render(request, 'accounts/search.html', {'searched':searched,
                                                        'inventories': inventories})
    else:
        return render(request, 'accounts/search.html', {})

def generate_sales_report(request):
    # Get all inventory items
    inventories = Inventory.objects.all()

    # Create a response object with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow(['Product', 'Total Sales', 'Quantity Sold', 'Last Sale Date'])

    # Loop through each inventory item and write sales data
    for inventory in inventories:
        writer.writerow([inventory.name, inventory.sales, inventory.quantity_sold, inventory.last_sales_date])

     # Update or create SalesData entries
        SalesData.objects.update_or_create(
            product=inventory,
            date=inventory.last_sales_date,
            defaults={'quantity_sold': inventory.quantity_sold}
        )

    return response

def generate_forecast(request, inventory_id):
    # Fetch historical sales data from the SalesData model
    sales_data = SalesData.objects.values('last_sales_date', 'quantity_sold').order_by('last_sales_date')

    # Create a DataFrame from the sales data
    df = pd.DataFrame(sales_data)

    # Perform forecasting using statsmodels
    model = ExponentialSmoothing(df['quantity_sold'], trend='add', seasonal='add', seasonal_periods=7)
    fit_model = model.fit()

    # Generate forecast values
    forecast_values = fit_model.forecast(steps=7)

    # Pass the forecast values to the template
    context = {
        'forecast_values': forecast_values,
    }

    return render(request, 'forecast_result.html', context)


def perform_forecasting_analysis(sales_data):
    # Assuming sales_data is a DataFrame with columns like 'date' and 'quantity_sold'
    
    # Your forecasting logic here...
    # For example, using Holt-Winters Exponential Smoothing
    model = ExponentialSmoothing(sales_data['quantity_sold'], seasonal='add', seasonal_periods=7)
    result = model.fit()

    # Forecast future values
    forecast_horizon = 30  # You can adjust the forecast horizon as needed
    forecast = result.forecast(steps=forecast_horizon)

    # Return the forecast data or any relevant information
    return forecast

def sales_data(request):
    forecast_data = None  # Initialize forecast_data

    if request.method == 'POST':
        form = SalesDataUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle the uploaded file
            sales_file = request.FILES['sales_file']
            # Example: Use pandas to read the CSV file
            sales_data = pd.read_csv(sales_file)
            
            # Perform forecasting analysis using the sales_data
            # Your forecasting logic here...
            forecast_data = perform_forecasting_analysis(sales_data)

    else:
        form = SalesDataUploadForm()

    return render(request, 'accounts/sales_data.html', {'form': form, 'forecast_data': forecast_data})

def subscription(request):
    if request.method == 'POST':
        email = request.POST.get('emailInput', '')
        # Add validation for the email if needed

        # Send confirmation email
        send_mail(
            'Subscription Confirmation',
            'Thank you for subscribing to FarmFresh! You will receive updates and promotions.',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        # You can also store the email in the database if you want to manage subscribers

        return HttpResponseRedirect(reverse('subscription'))

    return render(request, 'accounts/subscription.html')

