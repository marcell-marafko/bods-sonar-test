# Generated by Django 2.2.6 on 2019-11-11 16:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("transmodel", "0002_timingpattern_timingpatternstop"),
    ]

    operations = [
        migrations.CreateModel(
            name="VehicleJourney",
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
                ("start_time", models.TimeField()),
                (
                    "timing_pattern",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="transmodel.TimingPattern",
                    ),
                ),
            ],
        ),
    ]
