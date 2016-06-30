# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-30 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0030_auto_20160623_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='street_address_1_p1',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Dir parcial 1'),
        ),
        migrations.AddField(
            model_name='address',
            name='street_address_1_p2',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Dir parcial 2'),
        ),
        migrations.AddField(
            model_name='address',
            name='street_address_1_p3',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Dir parcial 3'),
        ),
        migrations.AddField(
            model_name='address',
            name='street_address_1_p4',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Dir parcial 4'),
        ),
    ]
