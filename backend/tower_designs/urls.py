from django.urls import path

from towers.views import (
    ArtifactPlacementCreateAPIView,
    ArtifactPlacementDetailAPIView,
    MyTowerOverviewAPIView,
    TowerBindingCreateAPIView,
    TowerBindingDetailAPIView,
    TowerDesignDetailAPIView,
    TowerDesignLayoutAPIView,
    TowerDesignListCreateAPIView,
    TowerDesignMineAPIView,
    TowerDesignPublishAPIView,
    TowerDesignRemixAPIView,
    TowerDesignSetActiveAPIView,
    TowerPieceDetailAPIView,
    TowerPieceListCreateAPIView,
)

urlpatterns = [
    path("my-tower/overview/", MyTowerOverviewAPIView.as_view(), name="my-tower-overview"),
    path("tower-designs/mine/", TowerDesignMineAPIView.as_view(), name="tower-design-mine"),
    path("tower-designs/", TowerDesignListCreateAPIView.as_view(), name="tower-design-create"),
    path("tower-designs/<int:design_id>/", TowerDesignDetailAPIView.as_view(), name="tower-design-detail"),
    path("tower-designs/<int:design_id>/set-active/", TowerDesignSetActiveAPIView.as_view(), name="tower-design-set-active"),
    path("tower-designs/<int:design_id>/publish/", TowerDesignPublishAPIView.as_view(), name="tower-design-publish"),
    path("tower-designs/<int:design_id>/remix/", TowerDesignRemixAPIView.as_view(), name="tower-design-remix"),
    path("tower-designs/<int:design_id>/layout/", TowerDesignLayoutAPIView.as_view(), name="tower-design-layout"),
    path("tower-designs/<int:design_id>/pieces/", TowerPieceListCreateAPIView.as_view(), name="tower-piece-create"),
    path("tower-designs/<int:design_id>/pieces/<int:piece_id>/", TowerPieceDetailAPIView.as_view(), name="tower-piece-detail"),
    path("tower-designs/<int:design_id>/bindings/", TowerBindingCreateAPIView.as_view(), name="tower-binding-create"),
    path("tower-designs/<int:design_id>/bindings/<int:binding_id>/", TowerBindingDetailAPIView.as_view(), name="tower-binding-detail"),
    path("tower-designs/<int:design_id>/artifacts/", ArtifactPlacementCreateAPIView.as_view(), name="tower-artifact-create"),
    path("tower-designs/<int:design_id>/artifacts/<int:placement_id>/", ArtifactPlacementDetailAPIView.as_view(), name="tower-artifact-detail"),
]
