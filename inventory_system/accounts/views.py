from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from .models import Inventory, SalesData
from orders.models import OrderAmount
from django.shortcuts import get_object_or_404
from .forms import InventoryUpdateForm, AddInventoryForm
from django.contrib import messages
from django_pandas.io import read_frame
import pandas as pd
import plotly
import plotly.express as px
import json
from django.conf import settings
from django.core.mail import send_mail
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from barcode.codex import Code128
from django_filters.views import FilterView
from .filters import StockFilter
import csv
from matplotlib import pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

@login_required
def home(request):
    logged_user = request.user
    request.session['old_username'] = logged_user.username
    if OrderAmount.objects.filter(customer=logged_user).exists():
        cart_record = get_object_or_404(OrderAmount, customer=logged_user)
        request.session['cart_count'] = cart_record.cart_count
    else:
        request.session['cart_count'] = 0
    return render(request, 'accounts/home.html')

def logout(request):
    return render(request, 'users/login.html')

class StockListView(FilterView):
    filterset_class = StockFilter
    queryset = Inventory.objects.filter(is_deleted=False)
    template_name = 'stock.html'
    paginate_by = 10

login_required
def products(request):
    inventories = Inventory.objects.all()
    context = {
        "title": "Inventory List",
        "inventories": inventories
    }
    return render(request, 'orders/products.html', context=context)

@login_required
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

@login_required
def per_product(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        'inventory' : inventory
    }
    return render(request, "accounts/per_product.html", context=context)

@login_required
def update(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        updateForm = InventoryUpdateForm(request.POST, request.FILES, instance=inventory)
        if updateForm.is_valid():
            inventory.name = updateForm.data['name']
            inventory.quantity_in_stock = updateForm.data['quantity_in_stock']
            inventory.quantity_sold = updateForm.data['quantity_sold']
            inventory.cost_per_item = updateForm.data['cost_per_item']
            inventory.sales = float(inventory.cost_per_item) * float(inventory.quantity_sold)
            inventory.save()
            inventory.image = updateForm['image']
            messages.success(request, "Update Successful")
            return redirect(reverse('per_product', kwargs={'pk': pk}))
    else:
        updateForm = InventoryUpdateForm(instance=inventory)

    return render(request, 'accounts/inventory_update.html', {'form' : updateForm})

@login_required
def delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.success(request, "Inventory Deleted")
    return redirect('stock')

@login_required
def add_product(request):
    if request.method == "POST":
        updateForm = AddInventoryForm(request.POST, request.FILES)
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

@login_required
def dashboard(request):
    inventories = Inventory.objects.all()
    
    # Check if the inventories are empty
    if not inventories:
        # Handle case where inventory is empty
        context = {
            "message": "No data available for dashboard."
        }
        return render(request, "accounts/empty_dashboard.html", context=context)
    
    # Convert Inventory queryset to DataFrame
    df = read_frame(inventories)

       
    # sales graph
    print(df.columns)
    
    sales_graph_df = df.groupby(by="last_sales_date", as_index=False, sort=False)['sales'].sum()
    print(sales_graph_df.sales)
    print(sales_graph_df.columns)
    plt.ylim(0,)
    plt.xlim(0,)
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



login_required
def marketing(request):
    context = {}
    return render(request, 'accounts/marketing.html', context)

def profile(request):
    context = {}
    return render(request, 'accounts/profile.html', context)

login_required
def profile(request):
        
    return render(request, 'accounts/profile.html')

login_required
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



#Search for something
@login_required
def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        inventories = Inventory.objects.filter(name__contains=searched)

        return render(request, 'accounts/search.html', {'searched': searched, 'inventories': inventories})
    else:
        return render(request, 'accounts/search.html', {})

@login_required
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

@login_required
def subscription(request):
    if request.method == 'POST':
        email = request.POST.get('emailInput', '')
        # Add validation for the email if needed

        # Send confirmation email
        send_mail(
            'Subscription Confirmation',
            'Thank you for subscribing to FarmFresh! You will receive updates and promotions.',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        # You can also store the email in the database if you want to manage subscribers

        return HttpResponseRedirect(reverse('subscription'))

    return render(request, 'accounts/subscription.html')

from django.contrib.auth import logout

@login_required
def logout(request):
    return render(request, 'system/login.html')

def analyze_sales_data(request):
    # Get the data from the Inventory model
    inventories = Inventory.objects.all()
    sales_df = pd.DataFrame(list(inventories.values('last_sales_date', 'sales')))
    sales_df['last_sales_date'] = pd.to_datetime(sales_df['last_sales_date'])

    # Convert 'sales' column to numeric, handling errors by setting them to NaN
    sales_df['sales'] = pd.to_numeric(sales_df['sales'], errors='coerce')

    # Drop rows with NaN values in the 'sales' column
    sales_df = sales_df.dropna(subset=['sales'])

    # Continue with the time series analysis
    df = sales_df.set_index('last_sales_date')
    df_monthly = df.resample('M').sum()

    # Perform time series analysis
    model = ARIMA(df_monthly['sales'], order=(1, 1, 1))
    results = model.fit()

    # Generate future dates for forecasting
    future_dates = pd.date_range(start=df_monthly.index[-1], periods=12, freq='M')[1:]
    
    # Get forecasted values and their index
    forecast = results.get_forecast(steps=12)
    forecast_values = forecast.predicted_mean
    forecast_index = pd.date_range(start=df_monthly.index[-1], periods=13, freq='M')[1:]

    # Create a DataFrame for the forecast data
    forecast_df = pd.DataFrame({'Date': forecast_index, 'Forecast': forecast_values})

    # Create product_forecasts within the view function
    product_forecasts = []
    for inventory in inventories:  # Iterate through your inventory data
        product_forecasts.append({
            'name': inventory.name,
            'data': [
                {'Date': date, 'Forecast': value} for date, value in zip(forecast_df['Date'], forecast_df['Forecast'])
            ]
        })

    context = {'product_forecasts': product_forecasts}

    # Pass the forecast data to the template
    return render(request, 'accounts/analyze_sales_data.html', context)
