# Panda3D AI Game Task: Gridworld Quest

> Built a Python/Panda3D mini-game environment for AI training task design.
> The project includes a playable 3D gridworld, JSON-based level assets,
> automatic level generation, BFS validation, and an evaluation rubric for
> assessing AI-created game levels.

---

## What it is

A small 3D game where a player moves through a gridworld, collects coins,
avoids walls, and reaches a goal tile. The real point is the layer around
it: levels are data files, a generator creates new ones programmatically,
a validator checks them automatically, and a task package frames the whole
thing as an AI training exercise.

This setup mirrors how AI research teams work with game environments —
separating content (JSON levels) from logic (the engine), so agents or
humans can author, evaluate, and iterate on game data without touching code.

---

## Stack

| Tool | Role |
|------|------|
| Python 3.12 | Language |
| Panda3D 1.10 | 3D rendering and game loop |
| JSON | Level data format |
| Pillow | Procedural texture generation |
| pytest | Automated validator tests |

---

## Project structure

```
panda3d-gridworld-quest/
  main.py                      # playable game
  requirements.txt
  levels/
    level_01.json              # beginner layout (5 coins, 7 obstacles)
    level_02.json              # medium layout  (8 coins, 18 obstacles)
  scripts/
    validate_level.py          # BFS-based level checker
    generate_level.py          # random solvable level generator
    generate_textures.py       # Pillow texture bake
  task_design/
    ai_training_prompt.md      # task specification for an AI agent
    evaluation_rubric.md       # scoring rubric for AI-generated levels
  tests/
    test_validate.py           # 7 pytest cases for the validator
  assets/
    textures/                  # generated PNGs (floor, wall, coin, goal)
  screenshots/
```

---

## Installation

```bash
git clone <repo-url>
cd panda3d-gridworld-quest
pip install -r requirements.txt
```

---

## Running the game

```bash
# Level 1 (beginner)
python main.py

# Level 2 (medium)
python main.py levels/level_02.json

# Any level file
python main.py levels/my_level.json
```

**Controls**

| Key | Action |
|-----|--------|
| W / A / S / D | Move one grid cell |
| R | Restart current level |
| Esc | Quit |

Hold a direction key to keep moving. Collect all coins you can, then reach
the green goal tile.

---

## Level format

Levels are plain JSON:

```json
{
  "grid_size": [10, 10],
  "player_start": [0, 0],
  "goal": [9, 9],
  "coins": [[2, 1], [4, 4], [6, 2]],
  "obstacles": [[1, 3], [2, 3], [3, 3]]
}
```

Coordinates are `[x, y]` where `x` goes right and `y` goes up across the grid.

---

## Scripts

### Validate a level

```bash
python scripts/validate_level.py levels/level_01.json
# ✓ 'levels/level_01.json' is valid.
```

Checks: required fields, grid bounds, no overlapping objects, and BFS
reachability from player start to goal.

### Generate a random level

```bash
python scripts/generate_level.py --coins 6 --obstacles 12 --seed 42
# ✓ Saved to 'levels/generated.json'
```

The generator retries until the BFS check passes, so output is always
solvable. Seed makes generation reproducible.

### Regenerate textures

```bash
python scripts/generate_textures.py
```

Writes four 64×64 PNGs to `assets/textures/` using Pillow.

---

## Tests

```bash
pytest tests/ -v
```

```
tests/test_validate.py::test_valid_level               PASSED
tests/test_validate.py::test_missing_field             PASSED
tests/test_validate.py::test_out_of_bounds_coin        PASSED
tests/test_validate.py::test_overlap_coin_and_obstacle PASSED
tests/test_validate.py::test_unsolvable_level          PASSED
tests/test_validate.py::test_goal_overlaps_obstacle    PASSED
tests/test_validate.py::test_player_out_of_bounds      PASSED

7 passed in 0.01s
```

---

## AI training task

`task_design/ai_training_prompt.md` defines a concrete task: given the rules
of the game, produce a valid JSON level file. It lists eight requirements
an AI agent must satisfy (grid size, object counts, position zones, no
overlaps, solvability) and points to the validator as the acceptance test.

`task_design/evaluation_rubric.md` provides the scoring rubric: eight
automated binary checks from `validate_level.py`, plus six manual review
criteria scored 0–2 each (design quality, playability, positional
constraints). A submission passes at ≥ 8/12 manual points with all
automated checks green.

This structure — task spec, automated check, manual rubric — is a small but
complete example of how AI training data pipelines evaluate generated
game content.

---

## Design notes

**Geometry** — all 3D objects are built procedurally at runtime using
`GeomVertexData` with per-face normals. No external `.egg` or `.bam`
model files are needed, which keeps the repo clean and makes the geometry
code readable.

**Movement** — grid-based. One keypress = one cell. Holding a key repeats
with a short initial delay (0.18 s) then a faster repeat rate (0.11 s),
matching the feel of classic gridworld games.

**Level as data** — separating level content from game logic is the key
architectural decision. It means levels can be authored by hand, generated
by a script, or produced by an AI agent — and the same validator checks
all of them identically.
