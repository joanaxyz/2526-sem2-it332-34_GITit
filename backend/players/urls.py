from django.urls import path

from players.views import CompanionLoadoutAPIView, PlayerPreferencesAPIView

urlpatterns = [
    path("preferences/", PlayerPreferencesAPIView.as_view(), name="player-preferences"),
    path("loadout/companion/", CompanionLoadoutAPIView.as_view(), name="player-companion-loadout"),
]
