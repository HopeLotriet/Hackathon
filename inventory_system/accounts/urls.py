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
    path("dashboard/", login_required(views.dashboard), name="dashboard"),
    path('about/', login_required(views.about), name='about'),
    path('stock/', login_required(views.stock), name='stock'),
    path('search/', login_required(views.search), name='search'),
    path('generate_sales_report/', login_required(views.generate_sales_report), name='generate_sales_report'),
    path('analyze-sales-data/', views.analyze_sales_data, name='analyze_sales_data'),
    path('subscription/', login_required(views.subscription), name='subscription'),
    path('send_bulk_emails/',login_required(views.send_bulk_emails), name='send_bulk_emails'),
]

