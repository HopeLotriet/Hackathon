# app_name= 'accounts'
from django.urls import path, include
from django.contrib import admin
from . import views
from .views import inventory, per_product_view, update, delete, add_product, dashboard, order_list, create_order, update_order_status, order_homepage


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('products/', views.products, name='products'),
    path('inventory/', views.inventory, name='inventory'),
    path('per_product/<int:pk>', views.per_product_view, name='per_product'),
    path('product_update/<int:pk>', views.update, name='product_update'),
    path('delete/<int:pk>', views.delete, name='product_delete'),
    path('add/', views.add_product, name='product_add'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('marketing/', views.marketing, name='marketing'),
    path('invoicing/', views.invoicing, name='invoicing'),
    path('profile/', views.profile, name='profile'),
    path('produce/', views.produce, name='produce'),
    path('productList/', views.productList, name='productList'),
    path('stock/', views.stock, name='stock'),
    path('reports/', views.reports, name='reports'),
    path('about/', views.about, name='about'),
    path('order_list', order_list, name='order_list'),
    path('create_order', create_order, name='create_order'),
    path('update_order_status/<int:order_id>/', update_order_status, name='update_order_status'),
     path('orders', order_homepage, name='order_homepage'),
]
