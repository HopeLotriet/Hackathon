from django.urls import path, include
from django.contrib import admin
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('products/', login_required(views.products), name='products'),
    path('per_product/<int:pk>/', login_required(views.per_product), name='per_product'),
    path("product_update/<int:pk>/", login_required(views.update), name="product_update"),
    path("delete/<int:pk>/", login_required(views.delete), name="product_delete"),
    path("add/", login_required(views.add_product), name="product_add"),
    path('marketing/', login_required(views.marketing), name='marketing'),
    path('profile/', login_required(views.profile), name='profile'),
    path('invoicing/', login_required(views.invoicing), name='invoicing'),
    path('create_invoice/', login_required(views.create_invoice), name='create_invoice'),
    path('invoice', login_required(views.invoice_detail), name='invoice_detail'),
    path('edit_invoice/<int:pk>/', login_required(views.edit_invoice), name='edit_invoice'),
    path('delete_invoice/<int:pk>/', login_required(views.delete_invoice), name='delete_invoice'),
    path('mark_as_paid/<int:pk>/', login_required(views.mark_invoice_as_paid), name='mark_invoice_as_paid'),
    path("dashboard/", login_required(views.dashboard), name="dashboard"),
    path('about/', login_required(views.about), name='about'),
    path('create_order/', login_required(views.create_order), name='create_order'),
    path('order_list', login_required(views.order_list), name='order_list'),
    path('create order', login_required(views.create_order), name='create_order'),
    path('update_order_status/<int:order_id>/', login_required(views.update_order_status), name='update_order_status'),
    path('order_history', login_required(views.order_history), name='order_history'),
    path('return_order/<int:order_id>/', login_required(views.return_order), name='return_order'),
    path('stock/', login_required(views.stock), name='stock'),
    path('invoice_pdf/<int:pk>/', login_required(views.invoice_pdf), name='invoice_pdf'),
    path('view_cart', login_required(views.view_cart), name='view_cart'),
    path('delete_from_cart/<int:item_id>/', login_required(views.delete_from_cart), name="delete_from_cart"),
    path('increase_cart_quantity/<int:item_id>/', login_required(views.increase_cart_quantity), name="increase_cart_quantity"),
    path('decrease_cart_quantity/<int:item_id>/', login_required(views.decrease_cart_quantity), name="decrease_cart_quantity"),
    path('add_to_cart/<int:item_id>/', login_required(views.add_to_cart), name="add_to_cart"),
    path('delete_cart', login_required(views.delete_cart), name='delete_cart'),
    path('order_details', login_required(views.order_details), name='order_details'),
    path('confirm_order/<int:pk>/', login_required(views.confirm_order), name='confirm_order'),
    path('search/', login_required(views.search), name='search'),
    path('confirmation_email/<int:pk>/', login_required(views.confirmation_email), name='confirmation_email'),
    path('invoice_history', login_required(views.invoice_history), name='invoice_history'),
    path('generate_sales_report/', login_required(views.generate_sales_report), name='generate_sales_report'),
    path('analyze-sales-data/', views.analyze_sales_data, name='analyze_sales_data'),
    #path('sales_data/', views.sales_data, name='sales_data'),
    path('subscription/', login_required(views.subscription), name='subscription'), 
]

