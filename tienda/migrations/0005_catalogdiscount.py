# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 15:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0004_auto_20160421_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogDiscount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre')),
                ('description', models.TextField(verbose_name='Descripci\xf3n')),
                ('discount', models.IntegerField(verbose_name='Descuento')),
                ('discount_unit', models.SmallIntegerField(choices=[(1, 'Valor fijo'), (2, 'Porcentaje')], default=1, verbose_name='Unidad de descuento')),
                ('activated_by_coupon', models.BooleanField(default=False, verbose_name='Activado con cup\xf3n')),
                ('coupon', models.CharField(blank=True, max_length=50, null=True, verbose_name='Cupon')),
                ('date_from', models.DateField(verbose_name='Fecha inicio')),
                ('date_to', models.DateField(verbose_name='Fecha fin')),
                ('enabled', models.BooleanField(default=False, verbose_name='Habilitado')),
                ('priority', models.SmallIntegerField(blank=True, default=0, verbose_name='Prioridad')),
                ('days', models.IntegerField(default=0, verbose_name='D\xedas')),
            ],
            options={
                'verbose_name': 'Descuento de cat\xe1logo',
                'verbose_name_plural': 'Descuentos de cat\xe1logo',
            },
        ),
    ]