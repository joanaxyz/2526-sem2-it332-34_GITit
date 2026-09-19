from django.urls import path

from drills.views import LevelDrillAPIView, LevelDrillResultAPIView, LevelDrillRunAPIView

urlpatterns = [
    path(
        "adventure-levels/<int:level_id>/drill/",
        LevelDrillAPIView.as_view(),
        name="level-drill",
    ),
    path(
        "adventure-levels/<int:level_id>/drill/run/",
        LevelDrillRunAPIView.as_view(),
        name="level-drill-run",
    ),
    path(
        "adventure-levels/<int:level_id>/drill/results/",
        LevelDrillResultAPIView.as_view(),
        name="level-drill-result",
    ),
]
