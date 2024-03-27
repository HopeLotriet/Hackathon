# Generated by Django 5.0.3 on 2024-03-26 19:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('orders', '0002_order_catalog_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='catalog_id',
        ),
        migrations.AddField(
            model_name='order',
            name='catalog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='accounts.catalog'),
        ),
        migrations.AddField(
            model_name='order',
            name='supplier_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
