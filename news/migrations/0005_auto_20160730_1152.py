# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-30 11:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_message_to_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='author',
            new_name='user',
        ),
    ]
