from adventures.models import AdventureLevelTierRun


def run_tips(client, run):
    response = client.get(f"/api/adventure-tier-runs/{run.id}/")
    assert response.status_code == 200, response.data
    return [tip["key"] for tip in response.data["tips"]]


def test_tips_come_back_every_time_the_scenario_is_played(client, teaching_run):
    assert run_tips(client, teaching_run) == ["concept:repository"]

    teaching_run.status = "completed"
    teaching_run.save(update_fields=["status"])
    again = AdventureLevelTierRun.objects.create(
        player=teaching_run.player,
        tier=teaching_run.tier,
        current_scenario=teaching_run.current_scenario,
        selected_variant=teaching_run.selected_variant,
        repository_state=teaching_run.selected_variant.initial_state,
        max_counted_commands=12,
    )
    assert run_tips(client, again) == ["concept:repository"]
