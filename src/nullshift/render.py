"""Renderer: 640x360 internal surface, integer x2 scale, layered draw."""
import math

import pygame

from nullshift import config, rooms, sprites, strings

T = config.TILE


class Renderer:
    def __init__(self):
        self.surf = pygame.Surface((config.INTERNAL_W, config.INTERNAL_H))
        self.font = pygame.font.SysFont("monospace", 13)
        self.tiny = pygame.font.SysFont("monospace", 9)
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
                if dev.sets_flag:
                    blit_at(sprites.prop("console", "power_on" if dev.on else "power"),
                            dev.tx, dev.ty)
                else:
                    blit_at(sprites.prop("console", dev.on), dev.tx, dev.ty)
            elif dev.kind == "door":
                if not dev.open:
                    for dx in range(dev.tw):
                        for dy in range(dev.th):
                            blit_at(sprites.prop("door"), dev.tx + dx, dev.ty + dy)
            elif dev.kind == "terminal":
                blit_at(sprites.prop("terminal"), dev.tx, dev.ty)
        # exit pads (locked ones render red + crossed)
        for pad in w.exits:
            locked = not pad.unlocked(game.progression)
            blit_at(sprites.prop("exit", "locked" if locked else None), pad.tx, pad.ty)
        # station signage (data-driven text plates)
        for sign in data.get("signs", []):
            t = self.tiny.render(sign["text"], True, (150, 160, 190))
            sx = ox + sign["tx"] * T + T // 2 - t.get_width() // 2
            sy = oy + sign["ty"] * T + T // 2 - t.get_height() // 2
            s.blit(t, (sx, sy))
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
        # echoes then player (player on top); echoes shimmer temporally
        tick = pygame.time.get_ticks()
        for e in w.echoes:
            if e.live:
                ex, ey = ox + e.rect.x, oy + e.rect.y
                if (tick // 90) % 2 == 0:
                    s.blit(sprites.echo_ghost(), (ex + 1, ey))
                s.blit(sprites.player_frame(e.facing, echo=True), (ex, ey))
        p = w.player
        s.blit(sprites.player_frame(p.facing), (ox + p.rect.x, oy + p.rect.y))
        # projectiles
        for pr in w.projectiles:
            pygame.draw.circle(s, (255, 220, 80),
                               (ox + int(pr["x"]), oy + int(pr["y"])), 3)
        self._draw_lighting(s, game)

    def _draw_lighting(self, s, game):
        """D017 TEMPORAL presentation overlay (pure function of game.temporal)."""
        light = game.temporal.get("lighting", "emergency")
        W, H = config.INTERNAL_W, config.INTERNAL_H
        if light == "emergency":
            pulse = 14 + int(7 * math.sin(pygame.time.get_ticks() / 350.0))
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((150, 30, 30, pulse))
            s.blit(ov, (0, 0))
        elif light == "low":
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 78))
            s.blit(ov, (0, 0))

    def _draw_hud(self, s, game):
        w = game.world
        # room display name (fiction-first, not numeric)
        name = w.data.get("display_name", w.room_id)
        t = self.font.render(name, True, (190, 200, 220))
        s.blit(t, (12, 8))
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
        # reset cycle text (continuity between cycles)
        if game.reset_text:
            rt = self.font.render(game.reset_text[0], True, (120, 200, 230))
            s.blit(rt, (config.INTERNAL_W // 2 - rt.get_width() // 2, by + 14))
        # Elias subtitle (non-blocking characterization)
        if game.subtitle:
            st = self.font.render(game.subtitle[0], True, (255, 200, 130))
            s.blit(st, (config.INTERNAL_W // 2 - st.get_width() // 2,
                        config.INTERNAL_H - 42))
        # objective (room data first, legacy strings fallback)
        obj = w.data.get("objective") or strings.OBJECTIVES.get(w.room_id, "")
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
        elif st == "LIA":
            self._dim(s)
            self._lia_card(s, game.lia_text)
        elif st == "GAMECOMPLETE":
            self._dim(s)
            lines = strings.SLICE_COMPLETE + ["",
                f"cycles: {game.stats['cycles']}  deaths: {game.stats['deaths']}"]
            self._center_lines(s, lines, self.big, self.font)

    def _lia_card(self, s, text: str):
        """LIA speaks through a distinct cyan card — not a terminal."""
        W, H = config.INTERNAL_W, config.INTERNAL_H
        bw, bh = 420, 150
        bx, by = W // 2 - bw // 2, H // 2 - bh // 2
        pygame.draw.rect(s, (6, 18, 24), (bx, by, bw, bh))
        pygame.draw.rect(s, (64, 224, 255), (bx, by, bw, bh), 2)
        head = self.font.render("LIA // STATION INTELLIGENCE", True, (64, 224, 255))
        s.blit(head, (bx + 14, by + 10))
        y = by + 36
        for line in text.split("\n"):
            t = self.font.render(line, True, (190, 225, 235))
            s.blit(t, (bx + 14, y))
            y += 18
        foot = self.font.render("[E] acknowledge", True, (120, 140, 155))
        s.blit(foot, (bx + 14, by + bh - 24))

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
