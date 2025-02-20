# Generated by Django 5.1.3 on 2024-11-29 13:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0010_purchase_order_status_supplier_purchase_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='mat_category',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='purchase_order_status',
            name='postat_status',
            field=models.CharField(choices=[('Waiting', 'Waiting'), ('Ongoing', 'Ongoing'), ('Done', 'Done')], default='Waiting', max_length=10),
        ),
        migrations.CreateModel(
            name='material_order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mat_odr_name', models.CharField(max_length=200)),
                ('mat_odr_type', models.CharField(blank=True, max_length=200, null=True)),
                ('mat_odr_quantity', models.IntegerField()),
                ('mat_odr_brand', models.CharField(blank=True, max_length=200, null=True)),
                ('mat_odr_measurement', models.CharField(blank=True, max_length=200, null=True)),
                ('mat_odr_category', models.CharField(blank=True, max_length=200, null=True)),
                ('po_num', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shared.purchase_order')),
                ('sup_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shared.supplier')),
            ],
        ),
    ]
