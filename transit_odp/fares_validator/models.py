from typing import List

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField

from transit_odp.fares_validator.types import Violation
from transit_odp.organisation.models import DatasetRevision

type_of_observation = "Simple fares validation failure"


class FaresValidationResult(models.Model):
    revision = models.OneToOneField(
        DatasetRevision,
        on_delete=models.CASCADE,
        related_name="fares_validation_result",
        help_text=_("The revision being validated."),
    )
    organisation = models.ForeignKey(
        "organisation.Organisation",
        on_delete=models.CASCADE,
        help_text="Bus portal organisation.",
    )
    count = models.IntegerField(help_text=_("Number of fare violations."))
    report_file_name = models.CharField(
        max_length=256, help_text=_("The name of the report file.")
    )
    created = CreationDateTimeField(_("created"))

    @property
    def is_compliant(self):
        return self.count == 0

    @classmethod
    def create_validation_result(
        cls, revision_id: int, org_id: int, violations: List[Violation]
    ):
        """
        Creates a FaresValidationResult from a DatasetRevision and a list of Violations.

        Args:
            revision (DatasetRevision): The revision containing the violations.
            violations (List[Violation]): The violations that a revision has.
        """
        now = timezone.now()
        fares_validator_report_name = (
            f"BODS_Fares_Validation_{org_id}_{revision_id}_{now:%H_%M_%d%m%Y}.xlsx"
        )
        return cls(
            revision_id=revision_id,
            organisation_id=org_id,
            count=len(violations),
            report_file_name=fares_validator_report_name,
        )


class FaresValidation(models.Model):
    revision = models.ForeignKey(
        DatasetRevision,
        on_delete=models.CASCADE,
        related_name="fares_validations",
        help_text=_("The revision that validation occurred in."),
    )
    organisation = models.ForeignKey(
        "organisation.Organisation",
        on_delete=models.CASCADE,
        help_text="Bus portal organisation.",
    )
    file_name = models.CharField(
        max_length=256, help_text=_("The name of the file the observation occurs in.")
    )
    error_line_no = models.IntegerField(
        help_text=_("The line number of the observation.")
    )
    type_of_observation = models.CharField(
        max_length=1024, help_text=_("Type Of Observation")
    )
    category = models.CharField(
        max_length=1024, help_text=_("The category of the observation.")
    )
    error = models.CharField(
        max_length=2000, help_text=_("The detailed error of the observation.")
    )
    reference = models.CharField(
        max_length=1024,
        default="Please see BODS Fares Validator Guidance v0.2",
        help_text=_("The reference of the observation"),
    )
    important_note = models.CharField(
        max_length=2000,
        default="This is warning only but data containing this failure will eventually be rejected by BODS ",
        help_text=_("The Important Note error of the observation."),
    )

    def __str__(self):
        return "%s %s %s" % (self.file_name, self.revision, self.organisation)

    @classmethod
    def create_observations(cls, revision_id: int, org_id: int, violation: Violation):
        return cls(
            revision_id=revision_id,
            organisation_id=org_id,
            file_name=violation.filename,
            error_line_no=violation.line,
            error=violation.observation,
            type_of_observation=type_of_observation,
            category=violation.category,
        )
