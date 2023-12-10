app_name= 'accounts'

from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('products', views.products, name='products'),
    path('inventory', views.inventory, name='inventory'),
    path('marketing', views.marketing, name='marketing'),
    path('invoicing', views.invoicing, name='invoicing'),
    path('profile', views.profile, name='profile'),
]
