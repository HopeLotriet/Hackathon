# Generated by Django 5.0.3 on 2024-04-18 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('cost_per_item', models.DecimalField(decimal_places=2, max_digits=19)),
                ('quantity', models.IntegerField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=19)),
                ('customer', models.CharField(default='', max_length=100)),
                ('catalog', models.IntegerField(null=True)),
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
                ('payment_method', models.CharField(default='', max_length=100)),
                ('payment_status', models.CharField(default='', max_length=100)),
                ('catalog', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_no', models.CharField(default='', max_length=255)),
                ('order', models.CharField(default='', max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('billing_name', models.CharField(max_length=255)),
                ('billing_address', models.TextField(blank=True, null=True)),
                ('billing_email', models.EmailField(max_length=254)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Overdue', 'Overdue')], default='Pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('Debit/Credit card', 'Debit/Credit Card'), ('Cash Deposit', 'Cash Deposit')], default='', max_length=20)),
                ('payment_due_date', models.DateField(blank=True, null=True)),
                ('payment_proof', models.FileField(blank=True, null=True, upload_to='payment_proof/')),
                ('paid_amount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid')], default='draft', max_length=20)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='pdfs/')),
                ('supplier_info', models.JSONField(blank=True, null=True)),
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
                ('payment_method', models.CharField(default='', max_length=100)),
                ('payment_status', models.CharField(default='', max_length=100)),
                ('order_status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='pending', max_length=20)),
                ('supplier', models.CharField(default='', max_length=100)),
                ('catalog', models.IntegerField(null=True)),
                ('supplier_email', models.EmailField(max_length=254, null=True)),
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
    ]
