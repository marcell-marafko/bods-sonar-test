from django.urls import include, path
from transit_odp.browse.views.disruptions_views import (
    DisruptionOrganisationDetailView,
    DisruptionsDataView,
    DownloadDisruptionsDataArchiveView,
    DownloadDisruptionsView,
    DisruptionDetailView,
)

urlpatterns = [
    path(
        "download/",
        include(
            [
                path(
                    "",
                    view=DownloadDisruptionsView.as_view(),
                    name="download-disruptions",
                ),
                path(
                    "bulk_archive",
                    view=DownloadDisruptionsDataArchiveView.as_view(),
                    name="downloads-disruptions-bulk",
                ),
            ]
        ),
    ),
    path(
        "organisations/",
        include(
            [
                path(
                    "",
                    view=DisruptionsDataView.as_view(),
                    name="disruptions-data",
                ),
                path(
                    "<uuid:pk>/",
                    include(
                        [
                            path(
                                "",
                                view=DisruptionOrganisationDetailView.as_view(),
                                name="org-detail",
                            ),
                        ]
                    ),
                ),
                path(
                    "<uuid:pk1>/disruption-detail/",
                    view=DisruptionDetailView.as_view(),
                    name="disruption-detail",
                ),
            ]
        ),
    ),
]
