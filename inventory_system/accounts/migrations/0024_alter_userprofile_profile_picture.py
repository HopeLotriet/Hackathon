# Generated by Django 5.0 on 2024-01-19 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_alter_userprofile_address_alter_userprofile_phone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(default='static/images/profile', upload_to='profiles/'),
        ),
    ]
