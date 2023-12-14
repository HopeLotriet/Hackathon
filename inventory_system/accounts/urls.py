# app_name= 'accounts'
from django.urls import path, include
from django.contrib import admin
from . import views
from .views import per_product, update, delete, add_product, dashboard, order_list, create_order, update_order_status, order_history, return_order
from .views import invoicing, create_invoice, invoice_detail, edit_invoice, delete_invoice, mark_invoice_as_paid


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('products/', views.products, name='products'),
    path('per_product/<int:pk>/', views.per_product, name='per_product'),
    path("product_update/<int:pk>/", views.update, name="product_update"),
    path("delete/<int:pk>/", views.delete, name="product_delete"),
    path("add/", views.add_product, name="product_add"),
    path("reports/", views.reports, name="dashboard"),
    path('marketing/', views.marketing, name='marketing'),
    path('invoicing/', views.invoicing, name='invoicing'),
    path('create_invoice/', create_invoice, name='create_invoice'),
    path('invoice/<int:pk>/', invoice_detail, name='invoice_detail'),
    path('edit_invoice/<int:pk>/', edit_invoice, name='edit_invoice'),
    path('delete_invoice/<int:pk>/', delete_invoice, name='delete_invoice'),
    path('mark_as_paid/<int:pk>/', mark_invoice_as_paid, name='mark_invoice_as_paid'),
    path('profile/', views.profile, name='profile'),
    path('stock/', views.stock, name='stock'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('about/', views.about, name='about'),
    path('create_order/', views.create_order, name='create_order'),
    path('order_list', order_list, name='order_list'),
    path('create order', create_order, name='create_order'),
    path('update_order_status/<int:order_id>/', update_order_status, name='update_order_status'),
    path('order_history', order_history, name='order_history'),
    path('return_order/<int:order_id>/', return_order, name='return_order'),
]
