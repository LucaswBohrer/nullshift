"""Visual-only particles. Never affect simulation state."""
import random

import pygame

random.seed(1234)  # deterministic look; visual only


class Particles:
    def __init__(self):
        self.items = []

    def spawn_reset(self, x, y):
        for _ in range(26):
            self.items.append({
                "x": x, "y": y,
                "vx": random.uniform(-90, 90), "vy": random.uniform(-90, 90),
                "life": 0.5, "max": 0.5, "col": (64, 224, 255), "size": 2,
            })

    def spawn_sparks(self, x, y):
        for _ in range(12):
            self.items.append({
                "x": x, "y": y,
                "vx": random.uniform(-120, 120), "vy": random.uniform(-120, 120),
                "life": 0.35, "max": 0.35, "col": (255, 190, 80), "size": 2,
            })

    def spawn_shimmer(self, x, y):
        for _ in range(10):
            self.items.append({
                "x": x + random.uniform(-8, 8), "y": y + random.uniform(-8, 8),
                "vx": 0, "vy": -30,
                "life": 0.6, "max": 0.6, "col": (64, 224, 255), "size": 1,
            })

    def update(self, dt: float):
        for p in self.items:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.items = [p for p in self.items if p["life"] > 0]

    def draw(self, surf: pygame.Surface):
        for p in self.items:
            a = max(0, int(255 * p["life"] / p["max"]))
            col = (*p["col"], a)
            s = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            s.fill(col)
            surf.blit(s, (p["x"] - p["size"], p["y"] - p["size"]))
