# Generated by Django 5.0 on 2023-12-14 07:11

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
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
                ('barcode', models.ImageField(blank=True, null=True, upload_to='barcodes/')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(default='', max_length=100)),
                ('customer', models.CharField(default='', max_length=100)),
                ('quantity_ordered', models.PositiveIntegerField()),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.CharField(choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='pending', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[('farmer', 'Farmer'), ('customer', 'Customer'), ('retail', 'Retail'), ('admin', 'Admin')], default='customer', max_length=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('billing_name', models.CharField(max_length=255)),
                ('billing_address', models.TextField()),
                ('billing_email', models.EmailField(max_length=254)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue')], default='pending', max_length=20)),
                ('payment_method', models.CharField(blank=True, max_length=50, null=True)),
                ('payment_due_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid')], default='draft', max_length=20)),
                ('pdf_document', models.FileField(blank=True, null=True, upload_to='invoice_pdfs/')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='accounts.order')),
            ],
        ),
    ]
