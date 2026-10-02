"""Tunable constants. Gameplay-relevant numbers live here, not in logic."""

TICK_HZ = 60
CYCLE_TICKS = 2400          # 40 s cycle (slice validation parameter, D006)
TILE = 16
INTERNAL_W, INTERNAL_H = 640, 360
WINDOW_W, WINDOW_H = 1280, 720
SCALE = 2

PLAYER_SPEED = 110.0        # px/s
PLAYER_SIZE = 12            # hitbox, px
INTERACT_RADIUS = 28        # px, generous by design

MIN_RECORD_TICKS = 60       # runs shorter than this are not recorded
MAX_ECHOES = 3              # FIFO cap (D005)

TITLE = "NULL//SHIFT"

# keymap: pygame key constant names -> action
KEYMAP = {
    "up": ["K_UP", "K_w"],
    "down": ["K_DOWN", "K_s"],
    "left": ["K_LEFT", "K_a"],
    "right": ["K_RIGHT", "K_d"],
}
# edge-triggered (KEYDOWN)
EDGE_KEYS = {
    "interact": ["K_e"],
    "reset": ["K_r"],
    "pause": ["K_ESCAPE"],
    "mute": ["K_m"],
    "confirm": ["K_RETURN", "K_KP_ENTER", "K_SPACE"],
    "debug_overlay": ["K_F1"],
    "debug_collision": ["K_F2"],
    "debug_warp": ["K_F4"],
}
