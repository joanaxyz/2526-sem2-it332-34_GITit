import pytest

from common.collections import as_list


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, []),
        ("", []),
        ("main", ["main"]),
        (("main", "dev"), [("main", "dev")]),
        (["main", "dev"], ["main", "dev"]),
    ],
)
def test_as_list_preserves_the_shared_scalar_coercion_contract(value, expected):
    assert as_list(value) == expected
