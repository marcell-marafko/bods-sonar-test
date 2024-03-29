# Generated by Django 3.2.13 on 2022-07-11 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("site_admin", "0016_deduplicate_resource_request_counter"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="resourcerequestcounter",
            constraint=models.UniqueConstraint(
                fields=("date", "requestor_id", "path_info"),
                name="requestcounter_unique_with_requestor",
            ),
        ),
        migrations.AddConstraint(
            model_name="resourcerequestcounter",
            constraint=models.UniqueConstraint(
                condition=models.Q(("requestor_id", None)),
                fields=("date", "path_info"),
                name="requestcounter_unique_without_requestor",
            ),
        ),
    ]
