# Generated by Django 5.1.3 on 2024-11-30 14:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0012_rename_purchase_order_purchaseorder_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job_Order_Status',
            fields=[
                ('jostat_id', models.AutoField(primary_key=True, serialize=False)),
                ('jostat_status', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='material_order',
            name='sup_id',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='sup_id',
        ),
        migrations.CreateModel(
            name='Job_Order',
            fields=[
                ('JO_number', models.AutoField(primary_key=True, serialize=False)),
                ('JO_date_requested', models.DateField()),
                ('JO_description', models.CharField(blank=True, max_length=200, null=True)),
                ('JO_mat_used', models.CharField(max_length=200)),
                ('JO_date_completed', models.DateField()),
                ('JO_approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approved_job_orders', to='shared.employee')),
                ('JO_checked_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checked_job_orders', to='shared.employee')),
                ('bus_unit_num', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shared.bus')),
                ('mat_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shared.material')),
                ('jostat_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shared.job_order_status')),
            ],
        ),
    ]
