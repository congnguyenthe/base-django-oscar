# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-27 07:57
from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.postgres.fields import ArrayField

class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0016_auto_20190327_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='Product',
            name='item_list',
            field=ArrayField(),
        ),
    ]
