from django.urls import path

from adminconsole.views import (
    AdminAnalyticsAPIView,
    AdminChapterDetailAPIView,
    AdminChapterListAPIView,
    AdminContentListAPIView,
    AdminEconomyAdjustAPIView,
    AdminModerationListAPIView,
    AdminModerationUnpublishAPIView,
    AdminOverviewAPIView,
    AdminSettingsAPIView,
    AdminStoryDetailAPIView,
    AdminStoryListCreateAPIView,
    AdminTransactionListAPIView,
    AdminUserActionAPIView,
    AdminUserDetailAPIView,
    AdminUserListAPIView,
)

urlpatterns = [
    path("overview/", AdminOverviewAPIView.as_view(), name="admin-overview"),
    path("users/", AdminUserListAPIView.as_view(), name="admin-user-list"),
    path("users/<int:user_id>/", AdminUserDetailAPIView.as_view(), name="admin-user-detail"),
    path("users/<int:user_id>/actions/", AdminUserActionAPIView.as_view(), name="admin-user-action"),
    path("economy/transactions/", AdminTransactionListAPIView.as_view(), name="admin-transactions"),
    path("economy/adjust/", AdminEconomyAdjustAPIView.as_view(), name="admin-economy-adjust"),
    path("stories/", AdminStoryListCreateAPIView.as_view(), name="admin-story-list"),
    path("stories/<int:story_id>/", AdminStoryDetailAPIView.as_view(), name="admin-story-detail"),
    path("chapters/", AdminChapterListAPIView.as_view(), name="admin-chapter-list"),
    path("chapters/<int:chapter_id>/", AdminChapterDetailAPIView.as_view(), name="admin-chapter-detail"),
    path("content/", AdminContentListAPIView.as_view(), name="admin-content-list"),
    path("analytics/", AdminAnalyticsAPIView.as_view(), name="admin-analytics"),
    path("moderation/", AdminModerationListAPIView.as_view(), name="admin-moderation"),
    path("moderation/unpublish/", AdminModerationUnpublishAPIView.as_view(), name="admin-moderation-unpublish"),
    path("settings/", AdminSettingsAPIView.as_view(), name="admin-settings"),
]
