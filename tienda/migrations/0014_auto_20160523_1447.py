# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-23 14:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0013_auto_20160523_1244'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productorder',
            old_name='discount',
            new_name='discount_price',
        ),
    ]
