# Generated by Django 5.1.4 on 2025-01-01 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0025_material_requested_item_req_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item_request',
            name='irstat_id',
        ),
        migrations.RemoveField(
            model_name='joborder',
            name='jostat_id',
        ),
        migrations.AddField(
            model_name='item_request',
            name='item_req_status',
            field=models.CharField(choices=[('Waiting', 'Waiting'), ('Ongoing', 'Ongoing'), ('Done', 'Done')], default='Waiting', max_length=10),
        ),
        migrations.AddField(
            model_name='joborder',
            name='j_o_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Pending', max_length=20),
        ),
        migrations.DeleteModel(
            name='Item_Req_Status',
        ),
        migrations.DeleteModel(
            name='Job_Order_Status',
        ),
    ]
