from curriculum.stage_config import chapter_stage_config, stage_payload


class Chapter:
    def __init__(self, number=1, battle_stage=None):
        self.number = number
        self.battle_stage = battle_stage


def test_chapter_stage_config_uses_default_parallax_for_number():
    assert chapter_stage_config(Chapter(number=1)) == {"parallax": "chapter-01-foundation-hall"}


def test_stage_payload_returns_semantic_parallax_slug_and_landing():
    payload = stage_payload(
        {
            "parallax": "chapter-01-foundation-hall",
            "landing": {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4},
        }
    )

    assert payload == {
        "parallax": {"slug": "chapter-01-foundation-hall"},
        "landing": {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4},
    }


def test_stage_payload_rejects_unsafe_parallax_slug():
    assert stage_payload({"parallax": "../battle"}) is None


def test_stage_payload_returns_none_without_visual_config():
    assert stage_payload({}) is None
