# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-14 09:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ip', '0076_auto_20181115_0842'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='workarea',
            unique_together=set([('user', 'ip', 'type')]),
        ),
    ]