# Generated by Django 3.1.8 on 2021-06-03 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import filingcabinet.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('document', '0025_auto_20210505_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='content_hash',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='published_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='document_document', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='documentcollection',
            name='settings',
            field=models.JSONField(blank=True, default=dict, validators=[filingcabinet.validators.validate_settings_schema]),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(condition=models.Q(content_hash__isnull=False), fields=['content_hash'], name='document_document_chash_idx'),
        ),
    ]
