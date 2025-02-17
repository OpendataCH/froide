# Generated by Django 2.2.4 on 2020-03-02 12:13

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("foirequest", "0041_auto_20191024_2025"),
    ]

    operations = [
        migrations.CreateModel(
            name="LetterTemplate",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("form", models.JSONField(blank=True, default=dict)),
                ("constraints", models.JSONField(blank=True, default=dict)),
                ("subject", models.TextField(blank=True)),
                ("body", models.TextField(blank=True)),
                ("active", models.BooleanField(default=False)),
                ("created", models.DateTimeField(default=django.utils.timezone.now)),
                ("modified", models.DateTimeField(default=django.utils.timezone.now)),
                ("notes", models.TextField(blank=True)),
                (
                    "tag",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="foirequest.MessageTag",
                    ),
                ),
            ],
            options={
                "verbose_name": "letter template",
                "verbose_name_plural": "letter templates",
            },
        ),
    ]
