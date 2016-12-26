# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-26 07:04
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broker', '0002_auto_20161219_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='params',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=b'{}', null=True),
        ),
    ]
