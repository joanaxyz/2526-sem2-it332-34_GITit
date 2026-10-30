from django.conf import settings

from tutoring.services.scenario_recognition import corpus_hash, load_index


def test_committed_index_matches_the_public_scenario_bank():
    # Scenario ids include the bank's file name, so renaming a bank file or editing
    # a public field leaves the index stale and the tutor stops recognising tasks.
    assert load_index(str(settings.TUTOR_SCENARIO_INDEX_PATH), corpus_hash()) is not None, (
        "Tutor scenario index is stale; run `python manage.py build_tutor_index`."
    )
