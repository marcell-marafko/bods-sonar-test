# Generated by Django 3.2.13 on 2022-10-31 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("avl", "0021_auto_20221021_1602"),
    ]

    operations = [
        migrations.AlterField(
            model_name="postpublishingcheckreport",
            name="vehicle_activities_analysed",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="Vehicles analysed"
            ),
        ),
        migrations.AlterField(
            model_name="postpublishingcheckreport",
            name="vehicle_activities_completely_matching",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                null=True,
                verbose_name="Vehicles completely matching (ex. BlockRef)",
            ),
        ),
    ]
