# Generated by Django 3.2.16 on 2023-03-31 09:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("otc", "0005_remove_text_length_constraints"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="service_number",
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name="service",
            name="service_type_description",
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
