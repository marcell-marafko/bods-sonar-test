import pandas as pd
from celery.utils.log import get_task_logger
from django.contrib.gis.geos import LineString

from transit_odp.naptan.models import Locality
from datetime import datetime

from .dataframes import create_naptan_locality_df

logger = get_task_logger(__name__)


def convert_to_time_field(time_delta_value):
    base_datetime = pd.to_datetime("2000-01-01")
    if pd.isna(time_delta_value):
        return "00:00:00"

    time_delta_value = base_datetime + time_delta_value
    return time_delta_value.strftime("%H:%M:%S")


def create_stop_sequence(df: pd.DataFrame):
    df = df.reset_index().sort_values("order")
    columns = df.columns
    stops_atcos = (
        df[
            [
                "from_stop_atco",
                "departure_time",
                "is_timing_status",
                "journey_pattern_id",
            ]
        ]
        .iloc[[0]]
        .rename(columns={"from_stop_atco": "stop_atco"})
    )
    stops_atcos["is_timing_status"] = True
    stops_atcos["departure_time"] = pd.to_timedelta(stops_atcos["departure_time"])
    use_vehicle_journey_runtime = False
    if "run_time_vj" in columns:
        use_vehicle_journey_runtime = True
        columns = [
            "to_stop_atco",
            "is_timing_status",
            "run_time",
            "wait_time",
            "run_time_vj",
            "journey_pattern_id",
        ]
    else:
        columns = [
            "to_stop_atco",
            "is_timing_status",
            "run_time",
            "wait_time",
            "journey_pattern_id",
        ]

    last_stop = df[columns].rename(columns={"to_stop_atco": "stop_atco"})
    columns.remove("to_stop_atco")
    columns.remove("is_timing_status")
    columns.remove("journey_pattern_id")
    if use_vehicle_journey_runtime:
        last_stop["departure_time"] = last_stop["run_time_vj"].combine_first(
            last_stop["run_time"]
        ).fillna(pd.Timedelta(0)) + last_stop["wait_time"].fillna(pd.Timedelta(0))
    else:
        last_stop["departure_time"] = last_stop["run_time"].fillna(
            pd.Timedelta(0)
        ) + last_stop["wait_time"].fillna(pd.Timedelta(0))

    last_stop.drop(columns=columns, axis=1, inplace=True)
    stops_atcos = pd.concat([stops_atcos, last_stop], ignore_index=True)
    stops_atcos["departure_time"] = stops_atcos["departure_time"].cumsum()
    stops_atcos["departure_time"] = stops_atcos["departure_time"].apply(
        convert_to_time_field
    )

    stops_atcos.index.name = "order"
    return stops_atcos


def transform_service_pattern_stops(
    service_pattern_to_service_links: pd.DataFrame, stop_points
):
    service_pattern_stops = (
        (
            service_pattern_to_service_links.reset_index()
            .groupby(["file_id", "service_pattern_id"])
            .apply(create_stop_sequence)
        )
        .reset_index()
        .set_index(["file_id"], append=True, verify_integrity=True)
    )
    # Merge with stops to have sequence of naptan_id, geometry, etc.
    stop_cols = ["naptan_id", "geometry", "locality_id", "admin_area_id", "common_name"]
    service_pattern_stops = service_pattern_stops.merge(
        stop_points[stop_cols],
        how="left",
        left_on="stop_atco",
        right_index=True,
    )
    service_pattern_stops = service_pattern_stops.where(
        service_pattern_stops.notnull(), None
    )

    return service_pattern_stops


def agg_service_pattern_sequences(df: pd.DataFrame):
    geometry = None
    points = df["geometry"].values
    if len(list(point for point in points if point)) > 1:
        geometry = LineString(
            [[point.x, point.y] for point in points if point and pd.notna(point)]
        )

    return pd.Series(
        {
            "geometry": geometry,
            "localities": df["locality_id"].to_list(),
            "admin_area_codes": df["admin_area_id"].to_list(),
        }
    )


def transform_stop_sequence(service_pattern_stops, service_patterns):
    sequence = (
        service_pattern_stops.reset_index()
        .groupby(["file_id", "service_pattern_id"])
        .apply(agg_service_pattern_sequences)
    )
    service_patterns = service_patterns.join(sequence)
    service_patterns = service_patterns.where(service_patterns.notnull(), None)

    return service_patterns


def get_most_common_districts(stops: pd.DataFrame):
    """Returns top 5 most common district names for stops"""
    stops["district_name"] = stops["district_name"].replace(
        {"": "unknown", "None": "unknown", None: "unknown"}
    )
    count = stops["district_name"].value_counts()
    # Replace empty district name with "unknown"
    # count = count.rename({"": "unknown", "None": "unknown", None: "unknown"})
    # count = count.rename({"None": "unknown"})
    # Put unknown at the end of the list in case its singular. ie
    # this ["unknown"]. To protect against the unlikely event
    # that we have two lines with every district having an empty name
    return list(count.head().index) + ["unknown"]


def get_most_common_localities(stops: pd.DataFrame):
    """Returns top 5 most common localities names for stops"""
    stops["locality_name"] = stops["locality_name"].replace(
        {"": "unknown", "None": "unknown", None: "unknown"}
    )
    # Put unknown at the end of the list in case its singular. ie
    # this ["unknown"]. To protect against the unlikely event
    # that we have two lines with every district having an empty name
    count = stops["locality_name"].value_counts()
    count = count.sort_index(ascending=False).sort_values(
        ascending=False, kind="mergesort"
    )
    return list(count.head().index) + ["unknown"]


def sync_localities_and_adminareas(stop_points):
    locality_set = set(
        [
            locality if locality != "" else None
            for locality in stop_points["locality_id"].to_list()
        ]
    )

    if len(locality_set) != 0:
        qs = Locality.objects.filter(gazetteer_id__in=locality_set)

        fetched = create_naptan_locality_df(
            data=(
                {
                    "locality_name": obj.name,
                    "locality_id": obj.gazetteer_id,
                    "admin_area_id": obj.admin_area_id,
                }
                for obj in qs
            )
        )

        stop_points = stop_points.merge(
            fetched, how="left", left_on="locality_id", right_index=True
        )

    return stop_points


def create_route_links(timing_links, stop_points):
    """Reduce timing_links into route_links."""
    columns = timing_links.columns
    if "run_time" in columns:
        columns = [
            "from_stop_ref",
            "to_stop_ref",
            "is_timing_status",
            "run_time",
            "wait_time",
        ]
    else:
        columns = ["from_stop_ref", "to_stop_ref"]

    route_links = (
        timing_links.reset_index()
        .drop_duplicates(["file_id", "route_link_ref"])
        .set_index(["file_id", "route_link_ref"])
        .loc[:, columns]
        .rename(
            columns={"from_stop_ref": "from_stop_atco", "to_stop_ref": "to_stop_atco"}
        )
    )

    # Note route_links are not unique (from_stop_ref, to_stop_ref) pairs,
    # get list of unique pairs
    return route_links


def create_routes(journey_patterns, jp_to_jps, jp_sections, timing_links):
    jp_sections["route_section_hash"] = timing_links.groupby(
        ["file_id", "jp_section_id"]
    )["route_link_ref"].apply(create_hash)

    # Calculate the 'route_hash' of the journey_pattern - this identifies
    # the Route of the JourneyPattern
    journey_patterns["route_hash"] = (
        jp_to_jps.reset_index()
        .merge(jp_sections, left_on=["file_id", "jp_section_ref"], right_index=True)
        .groupby(["file_id", "journey_pattern_id"])
        .apply(lambda df: create_hash(df.sort_values("order")["route_section_hash"]))
    )

    # Create Routes from journey_patterns with unique route_hash
    routes = (
        journey_patterns.reset_index()[["file_id", "route_hash"]]
        .drop_duplicates(["file_id", "route_hash"])
        .set_index(["file_id", "route_hash"])
    )

    if routes.empty:
        return pd.DataFrame()

    return routes


def create_hash(s: pd.Series):
    """Hash together values in pd.Series"""
    return hash(tuple(s))


def create_route_to_route_links(
    journey_patterns, jp_to_jps, timing_links, vehicle_journeys_with_timing_refs
):
    """
    Merge timing_links with jp_to_jps to get timing links for each journey
    pattern, Note 'order' column appears in both jp_to_jps and timing_links,
    so suffixes are used to distinguish them.
    """
    # TODO - this could be optimised, there is no need to generate timing link
    # sequence for every journey pattern
    #  to get the route_link sequences. We can drop the journey_patterns
    # we don't need

    # get journey_patterns with unique routes
    route_patterns = journey_patterns.reset_index().drop_duplicates(
        ["file_id", "route_hash"]
    )[["file_id", "route_hash", "journey_pattern_id"]]

    route_to_route_links = route_patterns.merge(
        jp_to_jps.reset_index(), how="left", on=["file_id", "journey_pattern_id"]
    ).merge(
        timing_links.reset_index(),
        left_on=["file_id", "jp_section_ref"],
        right_on=["file_id", "jp_section_id"],
        suffixes=["_section", "_link"],
    )

    if not vehicle_journeys_with_timing_refs.empty:
        route_to_route_links = route_to_route_links.merge(
            vehicle_journeys_with_timing_refs.reset_index(),
            left_on=["file_id", "journey_pattern_id", "jp_timing_link_id"],
            right_on=["file_id", "journey_pattern_id", "timing_link_ref"],
            how="left",
            suffixes=["_rl", "_vj"],
        )
        route_to_route_links = route_to_route_links.groupby(
            ["file_id", "route_hash"]
        ).apply(
            lambda g: g.sort_values(["order_section", "order_link"]).reset_index()[
                ["route_link_ref", "run_time_vj"]
            ]
        )
    else:
        # Build the new sequence. To get the final ordering of route_link_ref,
        # we sort each group by the two
        # orderings and use 'reset_index' to create a new sequential index in this order
        route_to_route_links = route_to_route_links.groupby(
            ["file_id", "route_hash"]
        ).apply(
            lambda g: g.sort_values(["order_section", "order_link"]).reset_index()[
                ["route_link_ref"]
            ]
        )
    route_to_route_links.index.names = ["file_id", "route_hash", "order"]

    return route_to_route_links


def transform_service_links(route_links):
    service_links = (
        route_links.reset_index()[["from_stop_atco", "to_stop_atco"]]
        .drop_duplicates(["from_stop_atco", "to_stop_atco"])
        .reset_index()
        .set_index(["from_stop_atco", "to_stop_atco"])
    )
    return service_links


def transform_line_names(line_name_list):
    if line_name_list:
        line_names = ",".join(key for key in line_name_list)
        return line_names


def get_vehicle_journey_without_timing_refs(vehicle_journeys):
    df_subset = vehicle_journeys[
        vehicle_journeys.columns.difference(["timing_link_ref", "run_time"])
    ].drop_duplicates()
    df_subset = df_subset.drop(["service_code"], axis=1)
    return df_subset


def get_vehicle_journey_with_timing_refs(vehicle_journeys):
    df_subset = vehicle_journeys.loc[
        :, ["journey_pattern_ref", "service_code", "timing_link_ref", "run_time"]
    ]
    df_subset = df_subset.rename(
        columns={"journey_pattern_ref": "journey_pattern_id"}
    ).drop(["service_code"], axis=1)
    return df_subset[df_subset["timing_link_ref"].notna()].drop_duplicates()


def merge_vehicle_journeys_with_jp(vehicle_journeys, journey_patterns):
    df_merged = pd.merge(
        vehicle_journeys,
        journey_patterns,
        left_on=["file_id", "journey_pattern_ref"],
        right_index=True,
        how="left",
        suffixes=("_vj", "_jp"),
    )
    return df_merged


def merge_journey_pattern_with_vj_for_departure_time(
    vehicle_journeys, journey_patterns
):
    index = journey_patterns.index
    df_merged = pd.merge(
        journey_patterns.reset_index(),
        vehicle_journeys[["file_id", "journey_pattern_ref", "departure_time"]],
        left_on=["file_id", "journey_pattern_id"],
        right_on=["file_id", "journey_pattern_ref"],
        how="left",
        suffixes=("_vj", "_jp"),
    )
    df_merged = df_merged.drop(columns=["journey_pattern_ref"], axis=1)
    df_merged.set_index(index.names, inplace=True)
    return df_merged


def merge_serviced_organisations_with_operating_profile(
    serviced_organisations, operating_profiles
):
    serviced_organisations.reset_index(inplace=True)

    df_merged = pd.merge(
        serviced_organisations, operating_profiles, on="serviced_org_ref", how="inner"
    )
    df_merged = df_merged[
        ["file_id", "serviced_org_ref", "name", "operational", "start_date", "end_date"]
    ]
    df_merged.drop_duplicates(inplace=True)
    df_merged["operational"] = df_merged["operational"].astype(bool)
    df_merged.set_index("file_id", inplace=True)

    return df_merged


def transform_service_patterns(journey_patterns):
    # Create list of service patterns from journey patterns
    service_patterns = journey_patterns.reset_index().drop_duplicates(
        ["service_code", "route_hash"]
    )

    # Route hash at the time of this comment was null for
    # flexible services
    service_patterns.dropna(subset=["route_hash"], inplace=True)
    # Create an id column for service_patterns. Note using the route_hash
    # won't result in the prettiest id
    service_patterns["service_pattern_id"] = service_patterns["service_code"].str.cat(
        service_patterns["route_hash"].astype(str), sep="-"
    )

    service_patterns.set_index(["file_id", "service_pattern_id"], inplace=True)

    return service_patterns


def transform_service_pattern_to_service_links(
    service_patterns, route_to_route_links, route_links
):
    logger.info("Starting transform_service_pattern_to_service_links")
    service_pattern_to_service_links = (
        service_patterns.reset_index()
        .merge(
            route_to_route_links.reset_index(),
            how="left",
            on=["file_id", "route_hash"],
        )
        .merge(
            route_links,
            how="left",
            left_on=["file_id", "route_link_ref"],
            right_index=True,
        )
    )

    link_columns = service_pattern_to_service_links.columns
    if "departure_time" not in link_columns:
        service_pattern_to_service_links = service_pattern_to_service_links.set_index(
            ["file_id", "service_pattern_id", "order"]
        )
        service_pattern_to_service_links["departure_time"] = None
        service_pattern_to_service_links["is_timing_status"] = False
        service_pattern_to_service_links["run_time"] = pd.NaT
        service_pattern_to_service_links["wait_time"] = pd.NaT
        return service_pattern_to_service_links, []

    drop_columns = [
        "departure_time",
        "is_timing_status",
        "run_time",
        "wait_time",
        "journey_pattern_id",
    ]

    if "run_time_vj" in link_columns:
        link_columns = [
            "file_id",
            "service_pattern_id",
            "order",
            "from_stop_atco",
            "to_stop_atco",
            "departure_time",
            "is_timing_status",
            "run_time",
            "wait_time",
            "run_time_vj",
            "journey_pattern_id",
        ]
        drop_columns.append("run_time_vj")
    else:
        link_columns = [
            "file_id",
            "service_pattern_id",
            "order",
            "from_stop_atco",
            "to_stop_atco",
            "departure_time",
            "is_timing_status",
            "run_time",
            "wait_time",
            "journey_pattern_id",
        ]

    # filter and rename columns
    service_pattern_to_service_links = service_pattern_to_service_links[
        link_columns
    ].set_index(["file_id", "service_pattern_id", "order"])

    # no longer need route_hash
    service_patterns.drop("route_hash", axis=1, inplace=True)
    logger.info("Finished transform_service_pattern_to_service_links")
    return service_pattern_to_service_links, drop_columns
