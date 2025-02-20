# Generated by Django 5.1.4 on 2025-01-05 15:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0036_acknowledgment_receipt_ar_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acknowledgment_receipt',
            name='ar_date_received',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='acknowledgment_receipt',
            name='ar_date_receiver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shared.employee'),
        ),
    ]
