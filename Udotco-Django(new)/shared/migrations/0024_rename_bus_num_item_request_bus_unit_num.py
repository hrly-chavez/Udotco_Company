# Generated by Django 5.1.4 on 2024-12-09 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0023_alter_joborder_j_o_work_description_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item_request',
            old_name='bus_num',
            new_name='bus_unit_num',
        ),
    ]
