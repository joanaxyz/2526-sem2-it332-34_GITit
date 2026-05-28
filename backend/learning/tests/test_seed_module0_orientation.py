import pytest
from django.core.management import call_command

from learning.models import LearningUnit, Lesson


@pytest.mark.django_db
def test_seed_module0_orientation_creates_eight_lessons():
    call_command("seed_module0_orientation")
    unit = LearningUnit.objects.get(slug="orientation")
    lessons = Lesson.objects.filter(unit=unit, is_published=True).order_by("sort_order")
    assert lessons.count() == 8
    slugs = list(lessons.values_list("slug", flat=True))
    assert slugs[0] == "what-is-git-and-why-it-matters"
    assert slugs[-1] == "how-git-it-works"
    for lesson in lessons:
        assert lesson.interaction_steps
        assert lesson.interaction_steps[0].get("id")
        assert not lesson.title.lower().startswith("lesson 0.")

    extras = Lesson.objects.filter(unit=unit).exclude(slug__in=[
        "what-is-git-and-why-it-matters",
        "installing-git-and-environment",
        "command-line-basics",
        "git-diagram-four-areas",
        "commits-and-history",
        "reading-a-dag",
        "git-command-anatomy",
        "how-git-it-works",
    ])
    assert extras.filter(is_published=True).count() == 0
