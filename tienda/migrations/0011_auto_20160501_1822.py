# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-01 18:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0010_address_storeuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='mobile',
            field=models.IntegerField(default=1, verbose_name='Celular'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storeuser',
            name='gov_id',
            field=models.IntegerField(null=True, verbose_name='Documento de identidad'),
        ),
        migrations.AlterField(
            model_name='address',
            name='phone',
            field=models.IntegerField(verbose_name='Tel\xe9fono'),
        ),
    ]
