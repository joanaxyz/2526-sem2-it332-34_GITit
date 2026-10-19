def update_best_score(completion, *, run, run_field: str) -> None:
    """Keep the best grade, breaking star ties by counted command total.

    Callers own completion eligibility and first-clear rewards. Replays may
    improve an existing grade without creating new completion progress.
    """
    if completion is None or not (
        run.stars > completion.stars
        or (
            run.stars == completion.stars
            and run.counted_action_total < completion.counted_action_total
        )
    ):
        return
    setattr(completion, run_field, run)
    completion.stars = run.stars
    completion.counted_action_total = run.counted_action_total
    completion.completed_at = run.completed_at
    completion.save(update_fields=[run_field, "stars", "counted_action_total", "completed_at"])
