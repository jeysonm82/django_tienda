# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-23 17:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0016_auto_20160523_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[(b'test', b'TEST')], max_length=30, verbose_name='M\xe9todo de pago')),
                ('payment_ref', models.CharField(max_length=50, verbose_name='Referencia de pago')),
                ('status', models.CharField(choices=[('payment-pending', 'Pendiente de pago'), ('fully-paid', 'Pagada')], max_length=30, verbose_name='Estado')),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_ref',
        ),
        migrations.AddField(
            model_name='order',
            name='obs',
            field=models.TextField(blank=True, null=True, verbose_name='Observaciones'),
        ),
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tienda.Order'),
        ),
    ]
