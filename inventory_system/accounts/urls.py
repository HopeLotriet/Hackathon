from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('catalog/', login_required(views.catalog_list), name='catalog_list'),
    path('catalog_create/', views.catalog_create, name='catalog_create'),
    path('products/', login_required(views.products), name='products'),
    path('per_product/<int:pk>/', login_required(views.per_product), name='per_product'),
    path('each_product/<int:pk>/', login_required(views.each_product), name='each_product'),
    path("product_update/<int:pk>/", login_required(views.update), name="product_update"),
    path("delete/<int:pk>/", login_required(views.delete), name="product_delete"),
    path("add/", login_required(views.add_product), name="product_add"),
    path('marketing/', login_required(views.marketing), name='marketing'),
    path("dashboard/", login_required(views.dashboard), name="dashboard"),
    path('about/', login_required(views.about), name='about'),
    path('search/', login_required(views.search), name='search'),
    path('generate_sales_report/', login_required(views.generate_sales_report), name='generate_sales_report'),
    path('analyze-sales-data/', views.analyze_sales_data, name='analyze_sales_data'),
    path('subscription/', login_required(views.subscription), name='subscription'),
    path('send_bulk_emails/',login_required(views.send_bulk_emails), name='send_bulk_emails'),
    path('create_inventory/', login_required(views.create_inventory), name='create_inventory'),
    path('inventory_list/', login_required(views.inventory_list), name='inventory_list'),
    path('rate/', login_required(views.rate), name='rate'),
    path('rate_inventory/<int:inventory_id>/', login_required(views.rate_inventory), name='rate_inventory'),
    path('submit_testimonial/<int:inventory_id>/', login_required(views.submit_testimonial), name='submit_testimonial')
]