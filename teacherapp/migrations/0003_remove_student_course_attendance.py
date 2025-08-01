# Generated by Django 5.2 on 2025-06-26 09:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0012_drop_year_class_unique'),
        ('teacherapp', '0002_add_class_group_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='course',
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('status', models.CharField(choices=[('Present', 'Present'), ('Absent', 'Absent')], max_length=7)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teacherapp.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.subject')),
            ],
            options={
                'unique_together': {('date', 'student', 'subject')},
            },
        ),
    ]
