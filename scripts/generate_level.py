"""
generate_level.py — Random level generator for Gridworld Quest.

Generates a random, solvable level and writes it to a JSON file.
Uses validate_level() for the solvability check so the output always
passes the same rules the game enforces.

Usage:
    python scripts/generate_level.py
    python scripts/generate_level.py --coins 6 --obstacles 14 --seed 42
    python scripts/generate_level.py --output levels/my_level.json
"""

import argparse
import json
import os
import random
import sys

# Allow running from the project root or from inside scripts/
sys.path.insert(0, os.path.dirname(__file__))
from validate_level import validate_level


def generate_level(
    grid_w: int = 10,
    grid_h: int = 10,
    num_coins: int = 5,
    num_obstacles: int = 10,
    seed: int | None = None,
    max_attempts: int = 500,
) -> dict:
    """
    Return a valid level dict, retrying until BFS confirms it is solvable.

    Player start is placed in the lower-left quadrant; goal in the upper-right.
    Coins and obstacles are placed randomly in remaining free tiles.

    Raises RuntimeError if no valid layout is found within max_attempts.
    """
    rng = random.Random(seed)

    for attempt in range(max_attempts):
        # Constrain start/goal positions to opposite corners of the grid
        start = (
            rng.randint(0, max(0, grid_w // 3 - 1)),
            rng.randint(0, max(0, grid_h // 3 - 1)),
        )
        goal = (
            rng.randint(min(grid_w - 1, 2 * grid_w // 3), grid_w - 1),
            rng.randint(min(grid_h - 1, 2 * grid_h // 3), grid_h - 1),
        )

        occupied = {start, goal}

        # Build a shuffled pool of all free cells
        all_cells = [
            (x, y)
            for x in range(grid_w)
            for y in range(grid_h)
            if (x, y) not in occupied
        ]
        rng.shuffle(all_cells)

        obstacles = all_cells[:num_obstacles]
        coins     = all_cells[num_obstacles : num_obstacles + num_coins]

        data = {
            "grid_size":    [grid_w, grid_h],
            "player_start": list(start),
            "goal":         list(goal),
            "coins":        [list(c) for c in coins],
            "obstacles":    [list(o) for o in obstacles],
        }

        ok, _ = validate_level(data)
        if ok:
            return data

    raise RuntimeError(
        f"Could not generate a valid level after {max_attempts} attempts. "
        "Try fewer obstacles."
    )



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a random solvable Gridworld Quest level."
    )
    parser.add_argument(
        "--output", default="levels/generated.json",
        help="Destination JSON file (default: levels/generated.json)",
    )
    parser.add_argument("--coins",     type=int, default=5,  help="Number of coins")
    parser.add_argument("--obstacles", type=int, default=10, help="Number of obstacles")
    parser.add_argument("--seed",      type=int, default=None, help="RNG seed for reproducibility")
    args = parser.parse_args()

    print(f"Generating level (coins={args.coins}, obstacles={args.obstacles}, seed={args.seed})…")
    data = generate_level(
        num_coins=args.coins,
        num_obstacles=args.obstacles,
        seed=args.seed,
    )

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Saved to '{args.output}'")
    print(f"  Player start : {data['player_start']}")
    print(f"  Goal         : {data['goal']}")
    print(f"  Coins        : {len(data['coins'])}")
    print(f"  Obstacles    : {len(data['obstacles'])}")
