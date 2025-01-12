# Generated by Django 5.1.4 on 2025-01-11 04:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0041_material_approved_is_acknowledged'),
    ]

    operations = [
        migrations.AddField(
            model_name='item_request',
            name='job_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shared.joborder'),
        ),
    ]