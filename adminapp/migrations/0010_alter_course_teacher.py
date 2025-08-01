# Generated by Django 5.2 on 2025-06-26 07:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0009_classgroup'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(blank=True, limit_choices_to={'activation': 1, 'is_staff': 1}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
