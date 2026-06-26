"""
Tests for validate_level.py.

Covers: valid pass, missing field, out-of-bounds position, object overlap,
and a level where BFS cannot find a path to the goal.
"""

import sys
import os

# Resolve scripts/ relative to this file regardless of where pytest is invoked
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from validate_level import validate_level


# ── Shared fixture ─────────────────────────────────────────────────────────────

GOOD = {
    "grid_size":    [10, 10],
    "player_start": [0, 0],
    "goal":         [9, 9],
    "coins":        [[2, 2], [4, 5]],
    "obstacles":    [[1, 3], [2, 3]],
}


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_valid_level():
    """A well-formed, solvable level should pass all checks."""
    ok, errors = validate_level(GOOD)
    assert ok, f"Expected valid level, got errors: {errors}"
    assert errors == []


def test_missing_field():
    """Removing a required key should trigger a field-missing error."""
    bad = {k: v for k, v in GOOD.items() if k != "goal"}
    ok, errors = validate_level(bad)
    assert not ok
    assert any("goal" in e for e in errors)


def test_out_of_bounds_coin():
    """A coin outside the grid should be flagged."""
    bad = {**GOOD, "coins": [[15, 0], [2, 2]]}
    ok, errors = validate_level(bad)
    assert not ok
    assert any("outside" in e for e in errors)


def test_overlap_coin_and_obstacle():
    """An obstacle placed on the same tile as a coin should be rejected."""
    bad = {**GOOD, "obstacles": [[2, 2], [3, 3]]}   # [2,2] is also a coin
    ok, errors = validate_level(bad)
    assert not ok
    assert any("claimed by both" in e for e in errors)


def test_unsolvable_level():
    """
    Surrounding the player start with obstacles should cause the BFS check
    to fail since there is no path to the goal.
    """
    # [0,0] is the player. Its only neighbours are [1,0] and [0,1].
    # Block both — player is trapped.
    bad = {**GOOD, "obstacles": [[1, 0], [0, 1]]}
    ok, errors = validate_level(bad)
    assert not ok
    assert any("path" in e.lower() or "solvable" in e.lower() for e in errors)


def test_goal_overlaps_obstacle():
    """An obstacle placed on the goal tile should be rejected as an overlap."""
    bad = {**GOOD, "obstacles": GOOD["obstacles"] + [[9, 9]]}
    ok, errors = validate_level(bad)
    assert not ok


def test_player_out_of_bounds():
    """Player start position outside the grid should fail bounds check."""
    bad = {**GOOD, "player_start": [-1, 0]}
    ok, errors = validate_level(bad)
    assert not ok
    assert any("player_start" in e for e in errors)
