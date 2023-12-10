from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

def home(request):
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = request.POST.get('user_type')
            user.user_type = user_type
            user.save()
            login(request, user)
            return redirect('home')  # Change 'home' to your actual home page URL
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Change 'home' to your actual home page URL
    return render(request, 'accounts/login.html')
