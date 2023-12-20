# Generated by Django 5.0 on 2023-12-20 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_merge_20231219_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='cart_records',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=100)),
                ('cost_per_item', models.DecimalField(decimal_places=2, max_digits=19)),
                ('quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='customerOrderHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(default='', max_length=100)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('product', models.CharField(default='', max_length=100)),
                ('quantity_ordered', models.PositiveIntegerField(null=True)),
                ('amount_spent', models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True)),
                ('customer_order_status', models.CharField(default='pending', max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='amount_spent',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity_ordered',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
