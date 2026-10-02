"""Developer debug layer (DEV builds only). F1/F2/F4."""
import pygame

from nullshift import config


class Debug:
    def __init__(self):
        self.overlay = False
        self.collision = False
        self.warp_request = None

    def handle_key(self, key: int, game) -> None:
        if key == pygame.K_F1:
            self.overlay = not self.overlay
        elif key == pygame.K_F2:
            self.collision = not self.collision
        elif key == pygame.K_F4:
            # warp cycles between slice rooms for testing
            cur = game.world.room_id if game.world else "1.1"
            self.warp_request = "1.2" if cur == "1.1" else "1.1"

    def draw(self, surf: pygame.Surface, game, font) -> None:
        if not self.overlay or not game.world:
            return
        w = game.world
        lines = [
            f"room {w.room_id}  tick {w.cycle_tick}/{config.CYCLE_TICKS}",
            f"echoes {len(w.echoes)}  rec {w.rec.ticks} ticks  recordings {len(w.recordings)}",
            f"player ({w.player.x:.0f},{w.player.y:.0f}) facing {w.player.facing}",
            f"last reset: {w.last_reset_reason}",
            f"cycles {game.stats['cycles']} deaths {game.stats['deaths']}",
        ]
        y = 24
        for line in lines:
            surf.blit(font.render(line, True, (120, 255, 120)), (8, y))
            y += 14

    def draw_collision(self, surf: pygame.Surface, game) -> None:
        if not self.collision or not game.world:
            return
        w = game.world
        pygame.draw.rect(surf, (255, 0, 0), w.player.rect, 1)
        for e in w.echoes:
            pygame.draw.rect(surf, (0, 255, 255), e.rect, 1)
        for d in w.devices.values():
            pygame.draw.rect(surf, (255, 255, 0), d.rect, 1)
        for hz in w.hazards:
            pygame.draw.rect(surf, (255, 0, 255), hz.rect, 1)
