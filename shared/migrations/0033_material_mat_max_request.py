# Generated by Django 5.1.4 on 2025-01-04 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0032_alter_material_order_mat_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='mat_max_request',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]