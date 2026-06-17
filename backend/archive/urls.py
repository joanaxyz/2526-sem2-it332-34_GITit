from django.urls import path

from archive.views import (
    ArchiveChapterCreateAPIView,
    ArchiveDesignDetailAPIView,
    ArchiveDesignLayoutAPIView,
    ArchiveDesignListCreateAPIView,
    ArchiveDesignMineAPIView,
    ArchiveDesignOfficialForkAPIView,
    ArchiveDesignPublishAPIView,
    ArchiveDesignRemixAPIView,
    ArchiveDesignSetActiveAPIView,
    ArchiveDesignShareAPIView,
    MyArchiveOverviewAPIView,
    RelicPlacementCreateAPIView,
    RelicPlacementDetailAPIView,
    SharedArchiveOverviewAPIView,
)

urlpatterns = [
    path("my-archive/overview/", MyArchiveOverviewAPIView.as_view(), name="my-archive-overview"),
    path("archive-designs/mine/", ArchiveDesignMineAPIView.as_view(), name="archive-design-mine"),
    path("archive-designs/official-fork/", ArchiveDesignOfficialForkAPIView.as_view(), name="archive-design-official-fork"),
    path("archive-designs/shared/<int:design_id>/", SharedArchiveOverviewAPIView.as_view(), name="archive-design-shared"),
    path("archive-designs/", ArchiveDesignListCreateAPIView.as_view(), name="archive-design-create"),
    path("archive-designs/<int:design_id>/", ArchiveDesignDetailAPIView.as_view(), name="archive-design-detail"),
    path("archive-designs/<int:design_id>/set-active/", ArchiveDesignSetActiveAPIView.as_view(), name="archive-design-set-active"),
    path("archive-designs/<int:design_id>/publish/", ArchiveDesignPublishAPIView.as_view(), name="archive-design-publish"),
    path("archive-designs/<int:design_id>/share/", ArchiveDesignShareAPIView.as_view(), name="archive-design-share"),
    path("archive-designs/<int:design_id>/remix/", ArchiveDesignRemixAPIView.as_view(), name="archive-design-remix"),
    path("archive-designs/<int:design_id>/layout/", ArchiveDesignLayoutAPIView.as_view(), name="archive-design-layout"),
    path("archive-designs/<int:design_id>/chapters/", ArchiveChapterCreateAPIView.as_view(), name="archive-chapter-create"),
    path("archive-designs/<int:design_id>/relics/", RelicPlacementCreateAPIView.as_view(), name="relic-create"),
    path("archive-designs/<int:design_id>/relics/<int:placement_id>/", RelicPlacementDetailAPIView.as_view(), name="relic-detail"),
]
