# Generated by Django 3.2.20 on 2023-09-27 20:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipelines", "0021_add_schema_definition_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datasetetltaskresult",
            name="error_code",
            field=models.CharField(
                blank=True,
                choices=[
                    ("DANGEROUS_XML_ERROR", "DANGEROUS_XML_ERROR"),
                    ("DATASET_EXPIRED", "DATASET_EXPIRED"),
                    ("FILE_TOO_LARGE", "FILE_TOO_LARGE"),
                    ("NESTED_ZIP_FORBIDDEN", "NESTED_ZIP_FORBIDDEN"),
                    ("NO_DATA_FOUND", "NO_DATA_FOUND"),
                    ("POST_SCHEMA_ERROR", "POST_SCHEMA_ERROR"),
                    ("SCHEMA_ERROR", "SCHEMA_ERROR"),
                    ("SCHEMA_VERSION_MISSING", "SCHEMA_VERSION_MISSING"),
                    ("SCHEMA_VERSION_NOT_SUPPORTED", "SCHEMA_VERSION_NOT_SUPPORTED"),
                    ("SUSPICIOUS_FILE", "SUSPICIOUS_FILE"),
                    ("SYSTEM_ERROR", "SYSTEM_ERROR"),
                    ("XML_SYNTAX_ERROR", "XML_SYNTAX_ERROR"),
                    ("ZIP_TOO_LARGE", "ZIP_TOO_LARGE"),
                ],
                db_index=True,
                help_text="The error code returned for the failed task",
                max_length=50,
                verbose_name="Task Error Code",
            ),
        ),
    ]
