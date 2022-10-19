# Generated by Django 3.2.15 on 2022-09-27 18:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("organisation", "0054_initialise_organisation_stats"),
    ]

    operations = [
        migrations.CreateModel(
            name="FaresValidation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("dataset_id", models.IntegerField()),
                ("file_name", models.CharField(max_length=200)),
                ("error_line_no", models.IntegerField()),
                ("type_of_observation", models.CharField(max_length=2000)),
                ("category", models.CharField(max_length=2000)),
                ("error", models.CharField(max_length=2000)),
                (
                    "reference",
                    models.CharField(
                        default="Please see BODS Fares Validator Guidance v0.2",
                        max_length=2000,
                    ),
                ),
                (
                    "important_note",
                    models.CharField(
                        default="Data containing this warning will be rejected by BODS after January 2023. Please contact your ticket machine supplier",
                        max_length=2000,
                    ),
                ),
                (
                    "organisation",
                    models.ForeignKey(
                        help_text="Bus portal organisation.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="organisation.organisation",
                    ),
                ),
            ],
        ),
    ]