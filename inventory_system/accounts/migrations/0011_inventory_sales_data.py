# Generated by Django 5.0 on 2023-12-21 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_cart_records_total_amount_invoice_pdf_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='sales_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]