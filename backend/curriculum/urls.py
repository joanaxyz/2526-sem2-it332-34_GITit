from django.urls import path

from curriculum.views import (
    ChapterBookAPIView,
    ChapterContentAPIView,
    ChapterContentOverviewAPIView,
    ChapterListAPIView,
    CommandFormPreviewAPIView,
    LearnedSkillsAPIView,
    StoryListAPIView,
)

urlpatterns = [
    path("stories/", StoryListAPIView.as_view(), name="stories"),
    path("chapters/", ChapterListAPIView.as_view(), name="chapters"),
    path("chapters/<int:chapter_id>/content/", ChapterContentAPIView.as_view(), name="chapter-content"),
    path("chapters/<int:chapter_id>/overview/", ChapterContentOverviewAPIView.as_view(), name="chapter-overview"),
    path("chapters/<int:chapter_id>/book/", ChapterBookAPIView.as_view(), name="chapter-book"),
    path("skills/learned/", LearnedSkillsAPIView.as_view(), name="skills-learned"),
    path("command-forms/<int:form_id>/preview/", CommandFormPreviewAPIView.as_view(), name="command-form-preview"),
]
