# Generated by Django 5.0 on 2024-01-21 15:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='accountantPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('view_records', 'Manage records'), ('add_record', 'Add record'), ('update_record', 'Update records')),
            },
        ),
        migrations.CreateModel(
            name='cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('cost_per_item', models.DecimalField(decimal_places=2, max_digits=19)),
                ('quantity', models.IntegerField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('customer', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='cart_records',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('cost_per_item', models.DecimalField(decimal_places=2, max_digits=19)),
                ('quantity', models.IntegerField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=19, null=True)),
                ('customer', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='customerOrderHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(default='', max_length=100)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.CharField(default='', max_length=100)),
                ('product', models.CharField(default='', max_length=100)),
                ('quantity_ordered', models.PositiveIntegerField(null=True)),
                ('amount_spent', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('customer_order_status', models.CharField(default='pending', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('view_cart', 'Can view cart'), ('add_to_cart', 'Can add items to cart'), ('remove_from_cart', 'Can remove items from cart'), ('update_cart', 'Can update cart'), ('clear_cart', 'Can clear cart'), ('checkout', 'Can proceed to checkout'), ('view_order_history', 'Can view order history'), ('view_product_details', 'Can view product details')),
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('cost_per_item', models.DecimalField(decimal_places=2, max_digits=19)),
                ('quantity_in_stock', models.IntegerField()),
                ('quantity_sold', models.IntegerField()),
                ('sales', models.DecimalField(decimal_places=2, max_digits=19)),
                ('stock_date', models.DateField(auto_now_add=True)),
                ('last_sales_date', models.DateField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('barcode', models.ImageField(blank=True, null=True, upload_to='barcodes/')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('sales_data', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.CharField(default='----', max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('billing_name', models.CharField(max_length=255)),
                ('billing_address', models.TextField()),
                ('billing_email', models.EmailField(max_length=254)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue')], default='pending', max_length=20)),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_due_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid')], default='draft', max_length=20)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='pdfs/')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(default='', max_length=100)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.CharField(default='', max_length=100)),
                ('product', models.CharField(default='', max_length=100)),
                ('quantity_ordered', models.PositiveIntegerField(null=True)),
                ('amount_spent', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('order_status', models.CharField(choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='OrderAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_due', models.DecimalField(decimal_places=2, max_digits=19)),
                ('customer', models.CharField(default='', max_length=100)),
                ('cart_count', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StaffPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('view_dashboard', 'Can view dashboard'), ('manage_orders', 'Can manage orders'), ('manage_products', 'Can manage products'), ('view_products', 'Manage products'), ('view_inventory', 'Manage inventory')),
            },
        ),
        migrations.CreateModel(
            name='SupplierPermissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('view_inventory', 'Manage inventory'), ('add_products', 'Add products to inventory')),
            },
        ),
        migrations.CreateModel(
            name='SalesData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('quantity_sold', models.IntegerField()),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='accounts.inventory')),
            ],
        ),
    ]
