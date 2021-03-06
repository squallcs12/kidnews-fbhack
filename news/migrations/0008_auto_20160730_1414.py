# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-30 14:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import news.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0007_article_quick_view_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Art',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to=news.models.article_directory_path)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='answer',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='article',
            name='comic',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='article',
            name='infographic',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='article',
            name='question',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='art',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.Article'),
        ),
        migrations.AddField(
            model_name='art',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='art',
            unique_together=set([('article', 'user')]),
        ),
    ]
