from collections import OrderedDict

import pandas as pd

from transit_odp.common.collections import Column
from transit_odp.fares.models import DataCatalogueMetaData
from transit_odp.organisation.csv import EmptyDataFrame
from transit_odp.organisation.models.organisations import OperatorCode

METADATA_COLUMNS = (
    "dataset_id",
    "xml_file_name",
    "valid_from",
    "valid_to",
    "national_operator_code",
    "string_nocs",
    "string_line_ids",
    "string_lines",
    "string_atco_areas",
    "string_tariff_basis",
    "string_product_type",
    "string_product_name",
    "string_user_type",
    "last_updated_date",
    "operator_id",
    "organisation_name",
    "is_fares_compliant",
)

FARES_DATA_COLUMN_MAP = OrderedDict(
    {
        "dataset_id": Column(
            "Dataset ID",
            "The internal BODS generated ID of the "
            "operator/publisher providing data on BODS.",
        ),
        "xml_file_name": Column(
            "XML file name",
            "The exact name of the file provided to BODS. This is usually "
            "generated by the publisher or their supplier.",
        ),
        "organisation_name": Column(
            "Organisation Name",
            "The name of the operator/publisher providing data on BODS.",
        ),
        "string_nocs": Column(
            "National Operator Code",
            "The National Operator Code(s) for the particular publisher as "
            "extracted from the NeTEx file they provided.",
        ),
        "operator_id": Column(
            "Operator ID",
            "The internal BODS generated ID of the operator/publisher "
            "providing data on BODS.",
        ),
        "is_fares_compliant": Column(
            "BODS Compliant",
            "The validation status and format of the files provided by the "
            "operator/publisher to BODS.",
        ),
        "last_updated_date": Column(
            "Last updated date",
            "The date that the data set/feed was last updated on BODS.",
        ),
        "valid_from": Column(
            "Valid from",
            "The operating period start date as extracted from the files "
            "provided by the operator/publisher to BODS.",
        ),
        "valid_to": Column(
            "Valid to",
            "The operating period end date as extracted from the files "
            "provided by the operator/publisher to BODS.",
        ),
        "string_line_ids": Column(
            "Line ids",
            "The Line id(s) as extracted from the files provided by the "
            "operator/publisher to BODS.",
        ),
        "string_lines": Column(
            "Line Name",
            "The line name(s) as extracted from the files provided by "
            "the operator/publisher to BODS.",
        ),
        "string_atco_areas": Column(
            "ATCO Area",
            "The ATCO Area (s) extracted from the ScheduledStopPoints in "
            "the files provided by the operator/publisher to BODS.",
        ),
        "string_tariff_basis": Column(
            "TariffBasis",
            "The TariffBasis element as extracted from the files provided by the "
            "operator/publisher to BODS.",
        ),
        "string_product_type": Column(
            "ProductType",
            "The ProductType element as extracted from the files provided by the "
            "operator/publisher to BODS.",
        ),
        "string_product_name": Column(
            "ProductName",
            "The Name element within PreassignedFareProduct as extracted from the "
            "files provided by the operator/publisher to BODS.",
        ),
        "string_user_type": Column(
            "UserType",
            "The origin element as extracted from the files provided by the "
            "operator/publisher to BODS.",
        ),
        "multioperator": Column(
            "Multioperator",
            "Status derived from comparing the BODS organisation of "
            "publisher and the National Operator Codes extracted "
            "from the files provided by the operator/publisher to BODS.",
        ),
    }
)

MULTIOPERATOR_STATUS_DICT = {True: "Yes", False: "No", "Unavailable": "NA"}


def _get_fares_data_catalogue_dataframe() -> pd.DataFrame:
    fares_df = pd.DataFrame.from_records(
        DataCatalogueMetaData.objects.get_active_fares_files().values(*METADATA_COLUMNS)
    )
    if fares_df.empty:
        raise EmptyDataFrame()

    nocs = fares_df["national_operator_code"].tolist()

    NOC_COLUMNS = ("organisation_id", "noc")
    nocs_data = OperatorCode.objects.values_list().order_by("id")
    nocs_df = pd.DataFrame.from_records(nocs_data.values(*NOC_COLUMNS))

    multioperator_list = add_multioperator_status(nocs, nocs_df)
    multioperator_df = pd.DataFrame(multioperator_list, columns=["multioperator"])

    if multioperator_df.empty:
        raise EmptyDataFrame()

    merged = pd.merge(
        fares_df, multioperator_df, left_index=True, right_index=True, how="outer"
    )

    rename_map = {
        old_name: column_tuple.field_name
        for old_name, column_tuple in FARES_DATA_COLUMN_MAP.items()
    }
    merged = merged[FARES_DATA_COLUMN_MAP.keys()].rename(columns=rename_map)

    merged.sort_values("Dataset ID", inplace=True)
    return merged


def get_fares_data_catalogue_csv():
    return _get_fares_data_catalogue_dataframe().to_csv(index=False)


def add_multioperator_status(nocs, nocs_df) -> list:
    """
    Calculates if the NOCs belong to the same organisation or not
    If all NOCs doesn't belong to same organisation then Multioperator is True
    """
    multioperator_list = []
    for operator_codes in nocs:
        orgs = []
        if operator_codes:
            for operator in operator_codes:
                if nocs_df.empty:
                    orgs.append(MULTIOPERATOR_STATUS_DICT["Unavailable"])
                else:
                    try:
                        org = nocs_df.loc[
                            nocs_df["noc"] == operator, "organisation_id"
                        ].iloc[0]
                        if org:
                            orgs.append(org)
                    except IndexError:
                        orgs.append(MULTIOPERATOR_STATUS_DICT["Unavailable"])
        else:
            orgs.append(MULTIOPERATOR_STATUS_DICT["Unavailable"])

        if len(set(orgs)) == 1:
            multioperator_list.append(MULTIOPERATOR_STATUS_DICT[False])
        elif len(set(orgs)) == 2 and MULTIOPERATOR_STATUS_DICT["Unavailable"] in set(
            orgs
        ):
            multioperator_list.append(MULTIOPERATOR_STATUS_DICT[False])
        elif len(set(orgs)) == 2 and MULTIOPERATOR_STATUS_DICT[
            "Unavailable"
        ] not in set(orgs):
            multioperator_list.append(MULTIOPERATOR_STATUS_DICT[True])
        elif len(set(orgs)) > 2:
            multioperator_list.append(MULTIOPERATOR_STATUS_DICT[True])

    if multioperator_list:
        return multioperator_list
