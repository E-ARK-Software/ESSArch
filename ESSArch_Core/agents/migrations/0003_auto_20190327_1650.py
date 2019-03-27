# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-27 15:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0002_agentrelationtype_mirrored_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentrelationtype',
            name='mirrored_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='agents.AgentRelationType', verbose_name='mirrored type'),
        ),
    ]
