"""Player: movement + collision. Deterministic, no acceleration model."""
import pygame

from nullshift import config
from nullshift.collision import sweep

T = config.TILE
HW = config.PLAYER_SIZE / 2.0
SPEED_PER_TICK = config.PLAYER_SPEED / config.TICK_HZ

# facing: 0=down, 1=up, 2=left, 3=right


class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.facing = 0
        self.alive = True
        self.rect = pygame.Rect(0, 0, config.PLAYER_SIZE, config.PLAYER_SIZE)
        self._sync_rect()

    def spawn(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.facing = 0
        self.alive = True
        self._sync_rect()

    def _sync_rect(self):
        self.rect.center = (int(round(self.x)), int(round(self.y)))

    def update(self, actions: dict, world) -> None:
        dx = (1 if actions.get("right") else 0) - (1 if actions.get("left") else 0)
        dy = (1 if actions.get("down") else 0) - (1 if actions.get("up") else 0)
        if dx and dy:
            dx *= 0.7071067811865476  # exact diagonal normalization
            dy *= 0.7071067811865476
        if dx or dy:
            if abs(dx) >= abs(dy):
                self.facing = 3 if dx > 0 else 2
            else:
                self.facing = 0 if dy > 0 else 1
        self.x, self.y = sweep(world, self.x, self.y,
                               dx * SPEED_PER_TICK, dy * SPEED_PER_TICK, HW, HW)
        self._sync_rect()
