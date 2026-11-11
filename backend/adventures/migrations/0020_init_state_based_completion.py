from django.db import migrations

OBSOLETE_TECHNIQUE = "init:initial-branch:main"
CASE_ID = "init-easy-current-empty"
TASK = (
    "Make the current folder a Git repository with `main` as its current branch.\n\n"
    "You may choose the branch during initialization or rename it afterward. Re-running "
    "`git init` is safe, but its initial-branch option does not rename an existing branch.\n\n"
    "**Do not stage files or create a commit.**"
)
CHECKS = [
    "Initialize the current folder as a Git repository.",
    "The current branch is main.",
    "Nothing is staged and no commit exists.",
]


def allow_state_based_init(apps, schema_editor):
    """Remove the obsolete gate without restarting active attempts or rewriting results."""
    alias = schema_editor.connection.alias
    Variant = apps.get_model("adventures", "AdventureLevelTierScenarioVariant")
    Run = apps.get_model("adventures", "AdventureLevelTierRun")
    for variant in Variant.objects.using(alias).filter(case_id=CASE_ID).iterator():
        params = dict(variant.parameter_context or {})
        params["required_techniques"] = [
            t for t in params.get("required_techniques", []) if t != OBSOLETE_TECHNIQUE
        ]
        context = dict(variant.scenario_context or {})
        context.update(task=TASK, objective_checks=CHECKS)
        Variant.objects.using(alias).filter(pk=variant.pk).update(
            parameter_context=params, scenario_context=context
        )

    pending = []
    runs = Run.objects.using(alias).filter(status="started", selected_variant__case_id=CASE_ID)
    for run in runs.only("id", "required_techniques").iterator(chunk_size=200):
        if OBSOLETE_TECHNIQUE not in (run.required_techniques or []):
            continue
        run.required_techniques = [t for t in run.required_techniques if t != OBSOLETE_TECHNIQUE]
        pending.append(run)
        if len(pending) == 200:
            Run.objects.using(alias).bulk_update(pending, ["required_techniques"])
            pending.clear()
    if pending:
        Run.objects.using(alias).bulk_update(pending, ["required_techniques"])


class Migration(migrations.Migration):
    dependencies = [
        ("adventures", "0019_adventureleveltierrun_adv_run_v2_targets"),
    ]

    operations = [migrations.RunPython(allow_state_based_init, migrations.RunPython.noop)]
