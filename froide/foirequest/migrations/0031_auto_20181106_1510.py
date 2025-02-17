# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-06 14:10
from __future__ import unicode_literals

import base64
from io import BytesIO

from django.db import migrations

from froide.helper.email_parsing import parse_email


def deferred_fill_sender(apps, schema_editor):
    DeferredMessage = apps.get_model("foirequest", "DeferredMessage")
    for deferred in DeferredMessage.objects.all():
        print(deferred.pk)
        email = parse_email(BytesIO(base64.b64decode(deferred.mail)))
        deferred.sender = email.from_[1]
        deferred.save()


class Migration(migrations.Migration):

    dependencies = [
        ("foirequest", "0030_auto_20181106_1510"),
    ]

    operations = [
        migrations.RunPython(deferred_fill_sender),
    ]
