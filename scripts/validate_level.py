"""
validate_level.py — Level validator for Gridworld Quest.

Runs four checks in order:
  1. Required fields are present.
  2. Every position is inside the grid bounds.
  3. No two objects share the same tile.
  4. A valid path exists from player_start to goal (BFS).

Can be used as a module (validate_level(data)) or run directly:
    python scripts/validate_level.py levels/level_01.json
"""

import json
import sys
from collections import deque


def validate_level(data: dict) -> tuple[bool, list[str]]:
    """
    Validate a level dict loaded from JSON.

    Returns (is_valid, errors) where errors is a list of human-readable
    problem descriptions. An empty list means the level is clean.
    """
    errors: list[str] = []

    # ── 1. Required fields ────────────────────────────────────────────────────
    required = ("grid_size", "player_start", "goal", "coins", "obstacles")
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    if errors:
        return False, errors  # can't continue without the basics

    gw, gh      = data["grid_size"]
    start       = tuple(data["player_start"])
    goal        = tuple(data["goal"])
    coins       = [tuple(c) for c in data["coins"]]
    obstacles   = [tuple(o) for o in data["obstacles"]]

    # ── 2. Bounds check ───────────────────────────────────────────────────────
    named_positions = (
        [("player_start", start), ("goal", goal)]
        + [("coin", c) for c in coins]
        + [("obstacle", o) for o in obstacles]
    )
    for label, (x, y) in named_positions:
        if not (0 <= x < gw and 0 <= y < gh):
            errors.append(
                f"{label} position {(x, y)} is outside the {gw}x{gh} grid"
            )

    # ── 3. Overlap check ──────────────────────────────────────────────────────
    occupied: dict[tuple, str] = {}
    for label, pos in named_positions:
        if pos in occupied:
            errors.append(
                f"Tile {pos} is claimed by both '{occupied[pos]}' and '{label}'"
            )
        else:
            occupied[pos] = label

    # ── 4. BFS reachability ───────────────────────────────────────────────────
    if not errors:  # skip if earlier checks already failed
        obs_set = set(obstacles)
        visited = {start}
        queue   = deque([start])
        found   = False

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == goal:
                found = True
                break
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = cx + dx, cy + dy
                npos = (nx, ny)
                if (
                    0 <= nx < gw
                    and 0 <= ny < gh
                    and npos not in obs_set
                    and npos not in visited
                ):
                    visited.add(npos)
                    queue.append(npos)

        if not found:
            errors.append(
                "No path from player_start to goal — level is not solvable"
            )

    return len(errors) == 0, errors


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "levels/level_01.json"

    with open(path) as f:
        data = json.load(f)

    ok, errors = validate_level(data)

    if ok:
        print(f"✓ '{path}' is valid.")
    else:
        print(f"✗ '{path}' has {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
