import pytest
from pydantic import ValidationError

from app.schemas import PropCreate


def make_prop_data(**overrides) -> dict:
    prop_data = {
        "game_id": 1,
        "player_name": "Josh Allen",
        "stat_category": "Passing Yards",
        "line": 275.5,
    }
    prop_data.update(overrides)
    return prop_data


@pytest.mark.parametrize("line", [0.5, 3.5, 72.5, 299.5, "64.5"])
def test_prop_create_accepts_half_point_lines(line):
    prop = PropCreate(**make_prop_data(line=line))

    assert prop.line == float(line)


@pytest.mark.parametrize("line", [300, 299.0, 299.25, 299.4, 0, -3.5])
def test_prop_create_rejects_lines_not_ending_in_half(line):
    with pytest.raises(ValidationError) as exc_info:
        PropCreate(**make_prop_data(line=line))

    message = exc_info.value.errors()[0]["msg"]
    assert "Line must be a positive number ending in .5 (e.g. 299.5)" in message
    assert f"got {line:g}" in message


@pytest.mark.parametrize("line", [float("inf"), float("nan")])
def test_prop_create_rejects_non_finite_lines(line):
    with pytest.raises(ValidationError):
        PropCreate(**make_prop_data(line=line))


def test_prop_create_strips_player_name():
    prop = PropCreate(**make_prop_data(player_name="  Josh Allen  "))

    assert prop.player_name == "Josh Allen"


@pytest.mark.parametrize("player_name", ["", "   ", "x" * 101])
def test_prop_create_rejects_bad_player_names(player_name):
    with pytest.raises(ValidationError) as exc_info:
        PropCreate(**make_prop_data(player_name=player_name))

    assert "Player name must be between 1 and 100 characters" in str(exc_info.value)


@pytest.mark.parametrize("category", ["All", "Sacks"])
def test_prop_create_rejects_unknown_categories(category):
    with pytest.raises(ValidationError):
        PropCreate(**make_prop_data(stat_category=category))


@pytest.mark.parametrize(
    "missing_field", ["game_id", "player_name", "stat_category", "line"]
)
def test_prop_create_requires_all_fields(missing_field):
    prop_data = make_prop_data()
    del prop_data[missing_field]

    with pytest.raises(ValidationError):
        PropCreate(**prop_data)
