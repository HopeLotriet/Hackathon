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

def per_product_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        "inventory" : inventory
    }
    return render(request, "inventory/per_product.html", context=context)

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

def fruits(request):
    context = {}
    return render(request, 'accounts/fruits.html', context)

def vegetables(request):
    context = {}
    return render(request, 'accounts/vegetables.html', context)

def herbs(request):
    context = {}
    return render(request, 'accounts/herbs.html', context)

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