from django.urls import path, include
from django.contrib import admin
from . import views
from .views import registration



urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('per_product/<int:pk>/', views.per_product, name='per_product'),
    path("product_update/<int:pk>/", views.update, name="product_update"),
    path("delete/<int:pk>/", views.delete, name="product_delete"),
    path("add/", views.add_product, name="product_add"),
    path('marketing/', views.marketing, name='marketing'),
    path('invoicing/', views.invoicing, name='invoicing'),
    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('invoice', views.invoice_detail, name='invoice_detail'),
    path('edit_invoice/<int:pk>/', views.edit_invoice, name='edit_invoice'),
    path('delete_invoice/<int:pk>/', views.delete_invoice, name='delete_invoice'),
    path('mark_as_paid/<int:pk>/', views.mark_invoice_as_paid, name='mark_invoice_as_paid'),
    path('profile/', views.profile, name='profile'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('about/', views.about, name='about'),
    path('create_order/', views.create_order, name='create_order'),
    path('order_list', views.order_list, name='order_list'),
    path('create order', views.create_order, name='create_order'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order_history', views.order_history, name='order_history'),
    path('return_order/<int:order_id>/', views.return_order, name='return_order'),
    path('stock/', views.stock, name='stock'),
    path('invoice_pdf/<int:pk>/', views.invoice_pdf, name='invoice_pdf'),
    path('view_cart', views.view_cart, name='view_cart'),
    path('delete_from_cart/<int:item_id>/', views.delete_from_cart, name="delete_from_cart"),
    path('increase_cart_quantity/<int:item_id>/', views.increase_cart_quantity, name="increase_cart_quantity"),
    path('decrease_cart_quantity/<int:item_id>/', views.decrease_cart_quantity, name="decrease_cart_quantity"),
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name="add_to_cart"),
    path('delete_cart', views.delete_cart, name='delete_cart'),
    path('order_details', views.order_details, name='order_details'),
    path('confirm_order/<int:pk>/', views.confirm_order, name='confirm_order'),
    path('search/', views.search, name='search'),
    path('confirmation_email/<int:pk>/', views.confirmation_email, name='confirmation_email'),
    path('invoice_history', views.invoice_history, name='invoice_history'),
]

