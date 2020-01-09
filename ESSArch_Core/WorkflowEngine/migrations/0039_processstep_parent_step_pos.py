"""
    ESSArch is an open source archiving and digital preservation system

    ESSArch
    Copyright (C) 2005-2019 ES Solutions AB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    Contact information:
    Web - http://www.essolutions.se
    Email - essarch@essolutions.se
"""

# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-25 14:47
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WorkflowEngine', '0032_processstep_parallel'),
    ]

    operations = [
        migrations.AddField(
            model_name='processstep',
            name='parent_step_pos',
            field=models.IntegerField(default=0, verbose_name='Parent step position'),
        ),
    ]
