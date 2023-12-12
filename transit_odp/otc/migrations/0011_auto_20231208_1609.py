# Generated by Django 3.2.20 on 2023-12-08 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("otc", "0010_inactiveservice"),
    ]

    operations = [
        migrations.CreateModel(
            name="UILta",
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
                ("name", models.TextField(unique=True)),
            ],
            options={
                "verbose_name_plural": "UI LTA",
                "db_table": "ui_lta",
            },
        ),
        migrations.RemoveField(
            model_name="localauthority",
            name="ui_lta_name",
        ),
        migrations.AddField(
            model_name="localauthority",
            name="ui_lta",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="localauthority_ui_lta_records",
                to="otc.uilta",
            ),
        ),
    ]