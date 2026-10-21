"""Public HTTP adapter exports for the staff admin console."""

from .curriculum import (
    AdminChapterDetailAPIView,
    AdminChapterListAPIView,
    AdminStoryDetailAPIView,
    AdminStoryListCreateAPIView,
)
from .dashboard import AdminAnalyticsAPIView, AdminOverviewAPIView
from .economy import AdminEconomyAdjustAPIView, AdminTransactionListAPIView
from .settings import AdminSettingsAPIView
from .users import (
    AdminUserActionAPIView,
    AdminUserDetailAPIView,
    AdminUserKpisAPIView,
    AdminUserListAPIView,
)

__all__ = [
    "AdminAnalyticsAPIView",
    "AdminChapterDetailAPIView",
    "AdminChapterListAPIView",
    "AdminEconomyAdjustAPIView",
    "AdminOverviewAPIView",
    "AdminSettingsAPIView",
    "AdminStoryDetailAPIView",
    "AdminStoryListCreateAPIView",
    "AdminTransactionListAPIView",
    "AdminUserActionAPIView",
    "AdminUserDetailAPIView",
    "AdminUserKpisAPIView",
    "AdminUserListAPIView",
]
