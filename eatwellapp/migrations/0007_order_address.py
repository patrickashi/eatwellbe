# Generated by Django 5.1.4 on 2025-01-14 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eatwellapp', '0006_remove_supermarketorder_supermarket_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
    ]
