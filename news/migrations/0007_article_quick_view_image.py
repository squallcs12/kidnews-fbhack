# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-30 11:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20160730_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='quick_view_image',
            field=models.ImageField(blank=True, null=True, upload_to='news/article'),
        ),
    ]
