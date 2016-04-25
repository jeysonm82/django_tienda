# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-25 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0008_catalogdiscountrule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='catalogdiscount',
            name='discount_unit',
            field=models.SmallIntegerField(choices=[(1, 'Valor fijo'), (2, 'Porcentaje')], default=2, verbose_name='Unidad de descuento'),
        ),
        migrations.AlterField(
            model_name='catalogdiscountrule',
            name='rtype',
            field=models.IntegerField(choices=[(1, 'Categoria'), (2, 'Producto')], default=1, verbose_name='Tipo'),
        ),
    ]
