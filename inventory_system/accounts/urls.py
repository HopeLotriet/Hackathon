# app_name= 'accounts'
from django.urls import path, include
from django.contrib import admin
from . import views
from .views import inventory, per_product, update, delete, add_product, dashboard


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('products/', views.products, name='products'),
    path('inventory/', views.inventory, name='inventory'),
    path('per_product/<int:pk>/', views.per_product, name='per_product'),
    path("product_update/<int:pk>/", views.update, name="product_update"),
    path("delete/<int:pk>/", views.delete, name="product_delete"),
    path("add/", views.add_product, name="product_add"),
    path("reports/", views.reports, name="dashboard"),
    path('marketing/', views.marketing, name='marketing'),
    path('invoicing/', views.invoicing, name='invoicing'),
    path('profile/', views.profile, name='profile'),
    path('produce/', views.produce, name='produce'),
    path('productList/', views.productList, name='productList'),
    path('stock/', views.stock, name='stock'),
    path('reports/', views.reports, name='reports'),
    path('about/', views.about, name='about'),
    path('orderList/', views.orderList, name='orderList'),

]
