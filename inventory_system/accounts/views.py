from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
# from .models import Product
from .models import Inventory
from django.shortcuts import get_object_or_404

#Update form import
from .forms import InventoryUpdateForm, AddInventoryForm
# flash messages
from django.contrib import messages
# dataframe
from django_pandas.io import read_frame
# plotly
import plotly
import plotly.express as px
# json
import json


def home(request):
    return render(request, 'accounts/home.html')


def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        PhoneNumber = request.POST['PhoneNumber']
        Password = request.POST['Password']
        ConfirmPassword = request.POST['ConfirmPassword']

        # validating user info if already existing so that user cannot create an account with the same info 
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if Password != ConfirmPassword:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')


# if all logic is correct then a user is created which takes the username, email and password
        myUser= User.objects.create_user(username, email, Password)
        myUser.first_name = fname
        myUser.last_name = lname
        myUser.phone_number = PhoneNumber


        myUser.save()

        messages.success(request, "Your account has been successfully created.")

        return redirect('/signin')


    return render(request, 'accounts/signup.html')


# signin function to authenticate user into the dashboard 

def signin(request):
    if request.method == "POST":
        email = request.POST['email']
        Password = request.POST['Password']

        user = authenticate(email=email, Password=Password)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "accounts/home.html", {'fname': fname})
        else:
            messages.error(request, "The email and/or password does not match")
            return redirect('home')

    return render(request, 'accounts/signin.html')


# Logout function to redirect to the signin page 
def signout(request):
    logout(request)
    messages.success(request, "logged out successfully")
    return redirect('/signin')


# function to send account activation to the user 

def products(request):
    context = {}
    return render(request, 'accounts/products.html', context)

def inventory(request):
    inventories = Inventory.objects.all()
    context = {
        "title" : "Inventory List",
        "inventories": inventories
    }
    return render(request, 'accounts/inventory.html', context=context)

def per_product(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        "inventory" : inventory
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
            return redirect(f"/inventory/per_product_view/{pk}/")
    else:
        updateForm = InventoryUpdateForm(instance=inventory)

    return render(request, "accounts/inventory_update.html", {'form' : updateForm})

def delete(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.success(request, "Inventory Deleted")
    return redirect("/inventory/")

def add_product(request):
    if request.method == "POST":
        updateForm = AddInventoryForm(data=request.POST)
        if updateForm.is_valid():
            new_invetory = updateForm.save(commit=False)
            new_invetory.sales = float(updateForm.data['cost_per_item']) * float(updateForm.data['quantity_sold'])
            new_invetory.save()
            messages.success(request, "Successfully Added Product")
            return redirect(f"/inventory/")
    else:
        updateForm = AddInventoryForm()

    return render(request, "accounts/inventory_add.html", {'form' : updateForm})

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

    return render(request,"accounts/reports.html", context=context)



def marketing(request):
    context = {}
    return render(request, 'accounts/marketing.html', context)

def invoicing(request):
    context = {}
    return render(request, 'accounts/invoicing.html', context)

def profile(request):
    context = {}
    return render(request, 'accounts/profile.html', context)

def produce(request):
    context = {
        
    }
    return render(request, 'accounts/produce.html', context)

def productList(request):
    products = Product.objects.all()
    return render(request, 'accounts/product_list.html', {'products': products})

def orderList(request):
    orders = Order.objects.all()
    return render(request, 'accounts/order_list.html', {'orders': orders})

def stock(request):
    context = {}
    return render(request, 'accounts/stock.html', context)

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