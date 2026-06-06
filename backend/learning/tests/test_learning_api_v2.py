from django.core.management import call_command

from learning.models import FoundationTopic, LearningModule
from learning.selectors import published_foundations, published_modules


def test_foundations_are_first_class_not_a_numbered_module(db):
    call_command("seed_curriculum_v2")

    assert FoundationTopic.objects.filter(slug="git-mental-model").exists()
    assert not LearningModule.objects.filter(slug="orientation").exists()
    assert not LearningModule.objects.filter(number=0).exists()
    assert len(list(published_foundations())) == FoundationTopic.objects.filter(is_published=True).count()


def test_modules_have_command_and_workflow_counts(db):
    call_command("seed_curriculum_v2")

    modules = list(published_modules())

    assert modules
    assert modules[0].command_topic_count > 0
    assert any(module.workflow_scenario_count > 0 for module in modules)
