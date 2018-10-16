"""
    ESSArch is an open source archiving and digital preservation system

    ESSArch Core
    Copyright (C) 2005-2017 ES Solutions AB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

    Contact information:
    Web - http://www.essolutions.se
    Email - essarch@essolutions.se
"""

# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-23 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_aip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileAIP'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_classification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileClassification'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileContentType'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_data_selection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileDataSelection'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_dip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileDIP'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_import',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileImport'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_sip',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileSIP'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_submit_description',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileSubmitDescription'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_transfer_project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileTransferProject'),
        ),
        migrations.AlterField(
            model_name='submissionagreement',
            name='profile_workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.ProfileWorkflow'),
        ),
    ]