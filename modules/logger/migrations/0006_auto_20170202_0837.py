# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-02 05:37
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0005_auto_20170126_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='callbacklog',
            name='callback_args',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='callbacklog',
            name='callback_kwargs',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='callbackloghistory',
            name='callback_args',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='callbackloghistory',
            name='callback_kwargs',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
