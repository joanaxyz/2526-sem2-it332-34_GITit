from django.db import models


class VariantBase(models.Model):
    """Shared shape for authored problem variants (adventure waves, challenge
    trials): one authored case with an initial/target state pair, an
    evaluation spec, and scaffold policy. Concrete subclasses add only their
    parent FK."""

    slug = models.SlugField()
    label = models.CharField(max_length=80)
    initial_state = models.JSONField(default=dict)
    evaluation_spec = models.JSONField(default=dict, blank=True)
    target_state = models.JSONField(default=dict, blank=True)
    solution_commands = models.JSONField(default=list, blank=True)
    case_id = models.CharField(max_length=160, blank=True)
    semantic_key = models.CharField(max_length=240, blank=True)
    parameter_context = models.JSONField(default=dict, blank=True)
    scenario_context = models.JSONField(default=dict, blank=True)
    scaffold_policy = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        abstract = True
