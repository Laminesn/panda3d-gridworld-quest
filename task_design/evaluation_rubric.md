# Evaluation Rubric: AI-Generated Gridworld Quest Level

Use this rubric to score a level file submitted in response to
`ai_training_prompt.md`. Automated checks must all pass before manual
review begins.

---

## Automated Checks

Run with: `python scripts/validate_level.py levels/your_level.json`

| # | Criterion | Pass Condition |
|---|-----------|----------------|
| 1 | JSON parses without errors | `json.load()` succeeds |
| 2 | `grid_size` present | Field exists and equals `[10, 10]` |
| 3 | `player_start` present and in-bounds | Field exists; `0 ≤ x,y ≤ 9` |
| 4 | `goal` present and in-bounds | Field exists; `0 ≤ x,y ≤ 9` |
| 5 | All coins in-bounds | Every coin position satisfies `0 ≤ x,y ≤ 9` |
| 6 | All obstacles in-bounds | Every obstacle position satisfies `0 ≤ x,y ≤ 9` |
| 7 | No overlapping objects | Every tile holds at most one object |
| 8 | Level is solvable | BFS finds a path from `player_start` to `goal` |

All eight checks are **binary pass/fail**. A single failure blocks the submission.

---

## Manual Review Criteria

Assessed by a human reviewer after automated checks pass.

| # | Criterion | 0 | 1 | 2 |
|---|-----------|---|---|---|
| 9 | Coin count ≥ 5 | Fewer than 5 | Exactly 5 | 6 or more |
| 10 | Obstacle count ≥ 8 | Fewer than 8 | Exactly 8 | 9 or more |
| 11 | Player in lower-left (`x ≤ 2`, `y ≤ 2`) | No | — | Yes |
| 12 | Goal in upper-right (`x ≥ 7`, `y ≥ 7`) | No | — | Yes |
| 13 | Level runs in Panda3D without errors | Crash on load | Minor visual issue | Clean run |
| 14 | Design quality | Random noise | Some routing choices | Intentional, interesting layout |

**Manual score range**: 0–12 points.

---

## Scoring Summary

| Component | Weight |
|-----------|--------|
| Automated checks (all 8) | Must pass — no partial credit |
| Manual criteria (14 total, 0–2 each) | Max 12 points |

**Passing threshold**: All automated checks green **and** manual score ≥ 8 / 12.

---

## Notes for Reviewers

- Run `python main.py levels/your_level.json` to test in-engine.
- For criterion 14, a layout scores 2 if obstacles form corridors or
  decision points, not just random scatter.
- If the path check passes but the level is obviously trivial (no obstacles
  near the critical path), deduct 1 from criterion 14.
