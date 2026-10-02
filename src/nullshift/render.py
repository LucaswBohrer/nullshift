"""Renderer: 640x360 internal surface, integer x2 scale, layered draw."""
import pygame

from nullshift import config, rooms, sprites, strings

T = config.TILE


class Renderer:
    def __init__(self):
        self.surf = pygame.Surface((config.INTERNAL_W, config.INTERNAL_H))
        self.font = pygame.font.SysFont("monospace", 13)
        self.big = pygame.font.SysFont("monospace", 28, bold=True)
        self._vignette = self._make_vignette()

    def _make_vignette(self):
        s = pygame.Surface((config.INTERNAL_W, config.INTERNAL_H), pygame.SRCALPHA)
        for y in range(0, config.INTERNAL_H, 3):
            pygame.draw.line(s, (0, 0, 0, 18), (0, y), (config.INTERNAL_W, y))
        pygame.draw.rect(s, (0, 0, 0, 60), (0, 0, config.INTERNAL_W, config.INTERNAL_H), 24)
        return s

    # ---- main ----
    def draw(self, game, particles, debug, flash: float):
        s = self.surf
        s.fill((8, 10, 16))
        if game.world:
            self._draw_world(s, game)
        particles.draw(s)
        s.blit(self._vignette, (0, 0))
        if game.world and game.state == "PLAYING":
            self._draw_hud(s, game)
        self._draw_state_overlay(s, game)
        debug.draw(s, game, self.font)
        debug.draw_collision(s, game)
        if flash > 0:
            f = pygame.Surface((config.INTERNAL_W, config.INTERNAL_H), pygame.SRCALPHA)
            f.fill((140, 220, 255, int(90 * flash)))
            s.blit(f, (0, 0))
        return s

    def _draw_world(self, s, game):
        w = game.world
        data = w.data
        ox = (config.INTERNAL_W - w.w * T) // 2
        oy = (config.INTERNAL_H - w.h * T) // 2

        def blit_at(surf, tx, ty, tw=1, th=1):
            s.blit(surf, (ox + tx * T, oy + ty * T))

        for ty in range(w.h):
            for tx in range(w.w):
                kind = rooms.LEGEND[rooms.tile_char(data, tx, ty)]
                blit_at(sprites.tile(kind), tx, ty)
        for dev in w.devices.values():
            if dev.kind == "pressure_plate":
                blit_at(sprites.prop("plate", dev.pressed), dev.tx, dev.ty)
            elif dev.kind == "console":
                blit_at(sprites.prop("console", dev.on), dev.tx, dev.ty)
            elif dev.kind == "door":
                if not dev.open:
                    for dx in range(dev.tw):
                        for dy in range(dev.th):
                            blit_at(sprites.prop("door"), dev.tx + dx, dev.ty + dy)
            elif dev.kind == "terminal":
                blit_at(sprites.prop("terminal"), dev.tx, dev.ty)
        # exit pad
        ex = w.exit
        s.blit(sprites.prop("exit"), (ox + ex.tx * T, oy + ex.ty * T))
        # hazards
        for hz in w.hazards:
            if hz.kind == "drone":
                s.blit(sprites.prop("drone"), (ox + hz.rect.x, oy + hz.rect.y))
            elif hz.kind == "turret":
                s.blit(sprites.prop("turret", hz.armed > 0), (ox + hz.rect.x, oy + hz.rect.y))
            elif hz.kind == "laser":
                r = hz.rect.move(ox, oy)
                if hz.active:
                    beam = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                    beam.fill((255, 50, 50, 200))
                    s.blit(beam, r.topleft)
                elif hz.warning:
                    if (pygame.time.get_ticks() // 120) % 2 == 0:
                        pygame.draw.rect(s, (255, 200, 60), r, 1)
        # echoes then player (player on top)
        for e in w.echoes:
            if e.live:
                s.blit(sprites.player_frame(e.facing, echo=True),
                       (ox + e.rect.x, oy + e.rect.y))
        p = w.player
        s.blit(sprites.player_frame(p.facing), (ox + p.rect.x, oy + p.rect.y))
        # projectiles
        for pr in w.projectiles:
            pygame.draw.circle(s, (255, 220, 80),
                               (ox + int(pr["x"]), oy + int(pr["y"])), 3)

    def _draw_hud(self, s, game):
        w = game.world
        # cycle timer bar
        frac = 1.0 - w.cycle_tick / config.CYCLE_TICKS
        bx, by, bw, bh = config.INTERNAL_W // 2 - 100, 8, 200, 8
        pygame.draw.rect(s, (30, 34, 48), (bx, by, bw, bh))
        col = (64, 224, 255) if frac > 0.15 else (255, 80, 80)
        pygame.draw.rect(s, col, (bx, by, int(bw * frac), bh))
        # echo pips
        for i in range(config.MAX_ECHOES):
            c = (64, 224, 255) if i < len(w.echoes) else (40, 46, 62)
            pygame.draw.rect(s, c, (bx + bw + 12 + i * 12, by, 8, 8))
        # objective
        obj = strings.OBJECTIVES.get(w.room_id, "")
        if obj:
            t = self.font.render(obj, True, (170, 180, 200))
            s.blit(t, (12, config.INTERNAL_H - 22))

    def _draw_state_overlay(self, s, game):
        st = game.state
        if st == "TITLE":
            self._center_lines(s, strings.TITLE_LINES, self.big, self.font)
        elif st == "PAUSED":
            self._dim(s)
            self._center_lines(s, ["PAUSED", "", "ESC resume"], self.big, self.font)
        elif st == "SECTORCARD":
            self._dim(s)
            self._center_lines(s, [game.pending_card], self.big, self.font)
        elif st == "TERMINAL":
            self._dim(s)
            self._center_lines(s, ["TERMINAL", "", game.terminal_text,
                                   "", "[E] close"], self.big, self.font)
        elif st == "GAMECOMPLETE":
            self._dim(s)
            lines = strings.SLICE_COMPLETE + ["",
                f"cycles: {game.stats['cycles']}  deaths: {game.stats['deaths']}"]
            self._center_lines(s, lines, self.big, self.font)

    def _dim(self, s):
        d = pygame.Surface((config.INTERNAL_W, config.INTERNAL_H), pygame.SRCALPHA)
        d.fill((0, 0, 0, 170))
        s.blit(d, (0, 0))

    def _center_lines(self, s, lines, big, small):
        y = config.INTERNAL_H // 2 - len(lines) * 11
        for i, line in enumerate(lines):
            f = big if i == 0 else small
            t = f.render(line, True, (220, 230, 245) if i == 0 else (170, 180, 200))
            s.blit(t, (config.INTERNAL_W // 2 - t.get_width() // 2, y))
            y += 26 if i == 0 else 20
