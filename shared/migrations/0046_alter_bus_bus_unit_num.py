# Generated by Django 5.1.4 on 2025-01-11 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0045_alter_material_order_mat_odr_brand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='bus_unit_num',
            field=models.CharField(primary_key=True, serialize=False),
        ),
    ]
