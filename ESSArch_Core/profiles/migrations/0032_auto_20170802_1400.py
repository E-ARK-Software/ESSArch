# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-02 14:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0031_auto_20170522_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_aip',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aip_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_archival_description',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archival_description_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_authority_information',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authority_information_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='content_type_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_data_selection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_selection_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_dip',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dip_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_event',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_import',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='import_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_preservation_metadata',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preservation_metadata_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_sip',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sip_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_submit_description',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='submit_description_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_transfer_project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfer_project_sa', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_workflow',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='workflow_sa', to='profiles.Profile'),
        ),
    ]