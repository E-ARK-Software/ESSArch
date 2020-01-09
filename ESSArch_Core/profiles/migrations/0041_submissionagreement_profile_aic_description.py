# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-09-27 12:42
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0040_submissionagreement_profile_aip_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='submissionagreement',
            name='profile_aic_description',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aic_description_sa', to='profiles.Profile'),
        ),
    ]
