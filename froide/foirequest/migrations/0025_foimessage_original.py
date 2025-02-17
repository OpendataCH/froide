# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-10 08:27
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("foirequest", "0024_auto_20180710_1025"),
    ]

    operations = [
        migrations.AddField(
            model_name="foimessage",
            name="original",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="message_copies",
                to="foirequest.FoiMessage",
            ),
        ),
    ]
