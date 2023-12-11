# app_name= 'accounts'

from django.urls import path, include
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('products/', views.products, name='products'),
    path('inventory/', views.inventory, name='inventory'),
    path('marketing/', views.marketing, name='marketing'),
    path('invoicing/', views.invoicing, name='invoicing'),
    path('profile/', views.profile, name='profile'),
    path('produce/', views.produce, name='produce'),
    path('fruits/', views.fruits, name='fruits'),
    path('vegetables/', views.vegetables, name='vegetables'),
    path('herbs/', views.herbs, name='herbs'),
    path('productList/', views.productList, name='productList'),
    path('stock/', views.stock, name='stock'),
    path('reports/', views.reports, name='reports'),
    path('about/', views.about, name='about'),
    path('orderList/', views.orderList, name='orderList'),
]
