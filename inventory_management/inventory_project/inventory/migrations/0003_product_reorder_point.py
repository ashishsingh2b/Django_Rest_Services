# Generated by Django 4.2.19 on 2025-02-20 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_remove_product_average_daily_usage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='reorder_point',
            field=models.IntegerField(default=10),
        ),
    ]
