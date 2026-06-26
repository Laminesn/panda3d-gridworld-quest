# AI Training Task: Generate a Gridworld Quest Level

## Context

Gridworld Quest is a Python/Panda3D mini-game where a player navigates a 3D
grid, collects coins, avoids walls, and reaches a goal tile. Levels are stored
as simple JSON files, making them easy for AI agents to read, write, and modify.

Your task is to act as a game designer and create a new playable level.

---

## Task

Create a new level file for Gridworld Quest.

Save it as `levels/level_03.json` (or any unused `level_NN.json`).

---

## Requirements

1. The grid must be exactly 10×10: `"grid_size": [10, 10]`.
2. Player start must be in the lower-left area: `x ≤ 2` and `y ≤ 2`.
3. Goal must be in the upper-right area: `x ≥ 7` and `y ≥ 7`.
4. The level must include **at least 5 coins**.
5. The level must include **at least 8 obstacles**.
6. No two objects (player, goal, coin, obstacle) may occupy the same tile.
7. All coordinates must be within bounds: `0 ≤ x ≤ 9` and `0 ≤ y ≤ 9`.
8. A valid path must exist from player start to goal (obstacles may not
   completely block the route).

---

## Expected Output Format

```json
{
  "grid_size": [10, 10],
  "player_start": [x, y],
  "goal": [x, y],
  "coins": [
    [x1, y1],
    [x2, y2]
  ],
  "obstacles": [
    [x1, y1],
    [x2, y2]
  ]
}
```

---

## Validation

Run the validator to verify your level passes all checks automatically:

```bash
python scripts/validate_level.py levels/level_03.json
```

Expected output: `✓ 'levels/level_03.json' is valid.`

---

## Bonus Challenges

- Design a maze-like corridor layout that forces the player to backtrack.
- Place coins so collecting all of them requires visiting multiple branches.
- Write a short paragraph (below the JSON, in a separate `.md` file) describing
  your design rationale — what made the layout interesting or difficult?

---

## Evaluation

Your submission will be scored against `task_design/evaluation_rubric.md`.
All eight automated checks must pass before manual review begins.
