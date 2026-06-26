"""
Panda3D AI Game Task: Gridworld Quest
--------------------------------------
A Python/Panda3D mini-game for AI training task design. The player navigates
a 3D gridworld, collects coins, avoids walls, and reaches the goal tile.

Level data is loaded from JSON so levels can be authored, generated, or
evaluated programmatically — the core value proposition for AI research.

Usage:
    python main.py                         # loads levels/level_01.json
    python main.py levels/level_02.json   # loads a specific level
"""

import json
import os
import sys
import time

from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    NodePath,
    TextNode,
)

# ── Grid constants ─────────────────────────────────────────────────────────────
CELL = 1.0       # world units per grid square
MOVE_DELAY = 0.18   # seconds before key-held repeat kicks in
MOVE_REPEAT = 0.11  # seconds between repeat moves while key is held


# ── Geometry helper ────────────────────────────────────────────────────────────

def make_box(width: float = 1.0, depth: float = 1.0, height: float = 1.0) -> NodePath:
    """
    Build a solid, lit box mesh centered at the origin.

    Uses per-face normals so Panda3D's directional light gives clean flat
    shading with no external model files required.
    """
    fmt = GeomVertexFormat.getV3n3()
    vdata = GeomVertexData("box", fmt, Geom.UHStatic)
    vtx = GeomVertexWriter(vdata, "vertex")
    nrm = GeomVertexWriter(vdata, "normal")

    hw, hd, hh = width / 2, depth / 2, height / 2

    # Six faces as (corner list, outward normal).
    # Winding order is counter-clockwise when viewed from outside.
    faces = [
        ([(-hw, -hd,  hh), ( hw, -hd,  hh), ( hw,  hd,  hh), (-hw,  hd,  hh)], ( 0,  0,  1)),  # top
        ([(-hw, -hd, -hh), (-hw,  hd, -hh), ( hw,  hd, -hh), ( hw, -hd, -hh)], ( 0,  0, -1)),  # bottom
        ([(-hw, -hd, -hh), ( hw, -hd, -hh), ( hw, -hd,  hh), (-hw, -hd,  hh)], ( 0, -1,  0)),  # front
        ([(-hw,  hd, -hh), (-hw,  hd,  hh), ( hw,  hd,  hh), ( hw,  hd, -hh)], ( 0,  1,  0)),  # back
        ([( hw, -hd, -hh), ( hw,  hd, -hh), ( hw,  hd,  hh), ( hw, -hd,  hh)], ( 1,  0,  0)),  # right
        ([(-hw, -hd, -hh), (-hw, -hd,  hh), (-hw,  hd,  hh), (-hw,  hd, -hh)], (-1,  0,  0)),  # left
    ]

    prim = GeomTriangles(Geom.UHStatic)
    for i, (corners, normal) in enumerate(faces):
        base = i * 4
        for cx, cy, cz in corners:
            vtx.addData3(cx, cy, cz)
            nrm.addData3(*normal)
        # Two triangles per quad face
        prim.addVertices(base, base + 1, base + 2)
        prim.addVertices(base, base + 2, base + 3)

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    node = GeomNode("box")
    node.addGeom(geom)
    return NodePath(node)


# ── Game class ─────────────────────────────────────────────────────────────────

class GridworldGame(ShowBase):
    """Main game class. Loads a JSON level, builds the 3D scene, handles input."""

    def __init__(self, level_path: str = "levels/level_01.json"):
        ShowBase.__init__(self)
        self.disableMouse()

        self.level_path = level_path
        with open(level_path) as f:
            data = json.load(f)

        # Parse level data
        self.grid_w, self.grid_h = data["grid_size"]
        self.obstacles  = {tuple(p) for p in data["obstacles"]}
        self.coins      = {tuple(p) for p in data["coins"]}
        self.goal       = tuple(data["goal"])
        self.player_pos = list(data["player_start"])

        # Runtime state
        self.score      = 0
        self.start_time = time.time()
        self.game_over  = False
        self.coin_nodes: dict[tuple, NodePath] = {}
        self.key_map    = {"w": False, "a": False, "s": False, "d": False}
        self.move_timer = 0.0  # countdown until next held-key repeat move

        self._setup_lights()
        self._build_scene()
        self._setup_camera()
        self._setup_hud()
        self._setup_input()

        self.taskMgr.add(self._update, "update")

    # ── Scene setup ────────────────────────────────────────────────────────────

    def _setup_lights(self):
        """One directional 'sun' light plus a soft ambient fill."""
        sun = DirectionalLight("sun")
        sun.setColor((0.88, 0.82, 0.76, 1.0))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(35, -55, 0)
        self.render.setLight(sun_np)

        ambient = AmbientLight("ambient")
        ambient.setColor((0.32, 0.32, 0.38, 1.0))
        amb_np = self.render.attachNewNode(ambient)
        self.render.setLight(amb_np)

    def _build_scene(self):
        """Place all grid objects: floor tiles, walls, coins, goal, player."""
        # Checkerboard floor
        for gx in range(self.grid_w):
            for gy in range(self.grid_h):
                tile = make_box(CELL, CELL, 0.08)
                tile.reparentTo(self.render)
                tile.setPos(gx * CELL, gy * CELL, -0.04)
                if (gx + gy) % 2 == 0:
                    tile.setColor(0.82, 0.77, 0.68, 1)
                else:
                    tile.setColor(0.72, 0.67, 0.58, 1)

        # Walls — slightly inset so there's a visible gap between them
        for gx, gy in self.obstacles:
            wall = make_box(CELL * 0.90, CELL * 0.90, CELL * 0.85)
            wall.reparentTo(self.render)
            wall.setPos(gx * CELL, gy * CELL, CELL * 0.85 / 2)
            wall.setColor(0.38, 0.38, 0.44, 1)

        # Goal — flat green slab
        gx, gy = self.goal
        goal_node = make_box(CELL * 0.88, CELL * 0.88, 0.12)
        goal_node.reparentTo(self.render)
        goal_node.setPos(gx * CELL, gy * CELL, 0.06)
        goal_node.setColor(0.18, 0.82, 0.30, 1)

        # Coins — small gold boxes floating above the floor
        for gx, gy in self.coins:
            coin = make_box(CELL * 0.32, CELL * 0.32, CELL * 0.32)
            coin.reparentTo(self.render)
            coin.setPos(gx * CELL, gy * CELL, CELL * 0.42)
            coin.setColor(1.0, 0.85, 0.10, 1)
            self.coin_nodes[(gx, gy)] = coin

        # Player — taller blue box
        self.player = make_box(CELL * 0.58, CELL * 0.58, CELL * 0.72)
        self.player.reparentTo(self.render)
        px, py = self.player_pos
        self.player.setPos(px * CELL, py * CELL, CELL * 0.36)
        self.player.setColor(0.20, 0.45, 0.88, 1)

    def _setup_camera(self):
        """Angle the camera slightly off vertical so the grid reads clearly."""
        cx = (self.grid_w - 1) * CELL / 2
        cy = (self.grid_h - 1) * CELL / 2
        self.camera.setPos(cx, cy - self.grid_h * 0.65, self.grid_h * 1.35)
        self.camera.lookAt(cx, cy, 0)

    def _setup_hud(self):
        """Score and timer top-left; control hint bottom-center."""
        self.score_text = OnscreenText(
            text="Score: 0",
            pos=(-1.28, 0.92), scale=0.062,
            fg=(1, 1, 1, 1), align=TextNode.ALeft, mayChange=True,
        )
        self.timer_text = OnscreenText(
            text="Time: 0.0s",
            pos=(-1.28, 0.83), scale=0.055,
            fg=(0.85, 0.85, 0.85, 1), align=TextNode.ALeft, mayChange=True,
        )
        OnscreenText(
            text="WASD: move    R: restart    Esc: quit",
            pos=(0, -0.95), scale=0.048, fg=(0.7, 0.7, 0.7, 1),
        )

    def _setup_input(self):
        for key in ("w", "a", "s", "d"):
            self.accept(key,        self._key_down, [key])
            self.accept(f"{key}-up", self._key_up,  [key])
        self.accept("escape", sys.exit)
        self.accept("r", self._restart)

    # ── Input handling ─────────────────────────────────────────────────────────

    def _key_down(self, key: str):
        """Move immediately on first press, then arm the repeat timer."""
        if not self.key_map[key]:
            self._do_move(key)
            self.move_timer = MOVE_DELAY
        self.key_map[key] = True

    def _key_up(self, key: str):
        self.key_map[key] = False

    def _do_move(self, key: str):
        """Attempt a one-cell move, then check for coin/win."""
        if self.game_over:
            return
        dx, dy = {"w": (0, 1), "s": (0, -1), "a": (-1, 0), "d": (1, 0)}[key]
        nx, ny = self.player_pos[0] + dx, self.player_pos[1] + dy

        if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h):
            return  # out of bounds — stay put
        if (nx, ny) in self.obstacles:
            return  # wall collision — stay put

        self.player_pos = [nx, ny]
        self.player.setPos(nx * CELL, ny * CELL, CELL * 0.36)

        # Coin pickup
        if (nx, ny) in self.coins:
            self.coins.discard((nx, ny))
            self.coin_nodes[(nx, ny)].removeNode()
            del self.coin_nodes[(nx, ny)]
            self.score += 1
            self.score_text.setText(f"Score: {self.score}")

        # Win condition
        if (nx, ny) == self.goal:
            self._win()

    # ── Game loop ──────────────────────────────────────────────────────────────

    def _update(self, task):
        """Per-frame: update HUD timer and handle held-key repeat movement."""
        if self.game_over:
            return task.cont

        dt = globalClock.getDt()

        elapsed = time.time() - self.start_time
        self.timer_text.setText(f"Time: {elapsed:.1f}s")

        # Decrement repeat timer and fire a move when it hits zero
        self.move_timer = max(0.0, self.move_timer - dt)
        if self.move_timer <= 0:
            for key in ("w", "s", "a", "d"):
                if self.key_map[key]:
                    self._do_move(key)
                    self.move_timer = MOVE_REPEAT
                    break

        return task.cont

    # ── Win / restart ──────────────────────────────────────────────────────────

    def _win(self):
        self.game_over = True
        elapsed = time.time() - self.start_time
        total_coins = len([p for p in self.coin_nodes]) + self.score
        OnscreenText(
            text=(
                f"Level Complete!\n\n"
                f"Coins collected: {self.score} / {total_coins + self.score}\n"
                f"Time: {elapsed:.1f}s\n\n"
                f"R to play again    Esc to quit"
            ),
            pos=(0, 0.12), scale=0.09,
            fg=(1.0, 0.92, 0.10, 1),
            shadow=(0, 0, 0, 0.75), shadowOffset=(0.04, 0.04),
        )

    def _restart(self):
        """Re-launch the process — cleanest way to reset all Panda3D state."""
        os.execv(sys.executable, [sys.executable] + sys.argv)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "levels/level_01.json"
    game = GridworldGame(level)
    game.run()
