import pandas as pd

from transit_odp.organisation.csv import EmptyDataFrame
from transit_odp.fares.models import DataCatalogueMetaData


def _get_fares_data_catalogue_dataframe() -> pd.DataFrame:
    fares_df = pd.DataFrame.from_records(
        DataCatalogueMetaData.objects.get_active_fares_files().values()
    )

    if fares_df.empty:
        raise EmptyDataFrame()

    fares_df.sort_values("fares_metadata_id", inplace=True)
    return fares_df


def get_fares_data_catalogue_csv():
    return _get_fares_data_catalogue_dataframe().to_csv(index=False)
