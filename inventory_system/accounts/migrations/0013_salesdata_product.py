# Generated by Django 5.0 on 2023-12-21 14:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_salesdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesdata',
            name='product',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='accounts.inventory'),
        ),
    ]
