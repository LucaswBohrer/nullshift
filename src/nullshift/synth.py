"""Procedural SFX synthesis (stdlib only — no numpy, no audio files).

Sounds are generated once at boot into pygame.mixer.Sound buffers.
"""
import array
import math
import random

SAMPLE_RATE = 22050

random.seed(99)


def _buffer(dur: float) -> array.array:
    return array.array("h", [0] * int(SAMPLE_RATE * dur))


def _tone(freq: float, dur: float, vol: float = 0.4, kind: str = "square",
          slide_to: float = None) -> array.array:
    buf = _buffer(dur)
    n = len(buf)
    for i in range(n):
        t = i / SAMPLE_RATE
        f = freq + (slide_to - freq) * (i / n) if slide_to else freq
        ph = 2 * math.pi * f * t
        if kind == "square":
            v = 1.0 if math.sin(ph) > 0 else -1.0
        elif kind == "saw":
            v = 2 * ((f * t) % 1.0) - 1.0
        else:  # sine
            v = math.sin(ph)
        env = 1.0 - (i / n)  # linear decay
        buf[i] = int(v * vol * env * 32767)
    return buf


def _noise(dur: float, vol: float = 0.35) -> array.array:
    buf = _buffer(dur)
    n = len(buf)
    for i in range(n):
        env = 1.0 - (i / n)
        buf[i] = int(random.uniform(-1, 1) * vol * env * 32767)
    return buf


def _mix(*bufs) -> array.array:
    n = max(len(b) for b in bufs)
    out = array.array("h", [0] * n)
    for b in bufs:
        for i in range(len(b)):
            v = out[i] + b[i] // len(bufs)
            out[i] = max(-32767, min(32767, v))
    return out


SPECS = {
    "interact": lambda: _tone(880, 0.07, 0.35),
    "console": lambda: _tone(660, 0.12, 0.35, slide_to=990),
    "door": lambda: _tone(180, 0.25, 0.4, kind="saw", slide_to=320),
    "plate": lambda: _tone(520, 0.06, 0.35),
    "reset": lambda: _tone(800, 0.4, 0.4, kind="sine", slide_to=90),
    "echo": lambda: _tone(1200, 0.3, 0.3, kind="sine", slide_to=1800),
    "death": lambda: _mix(_noise(0.3), _tone(220, 0.3, 0.3, kind="saw", slide_to=60)),
    "ui": lambda: _tone(440, 0.05, 0.3),
    "exit": lambda: _mix(_tone(660, 0.15, 0.3), _tone(990, 0.2, 0.3)),
    "room_complete": lambda: _mix(_tone(523, 0.12, 0.35), _tone(784, 0.2, 0.35)),
    "turret_charge": lambda: _tone(200, 0.35, 0.3, slide_to=700),
    "turret_shot": lambda: _tone(900, 0.12, 0.35, kind="saw", slide_to=200),
}


def build_all(pygame_module) -> dict:
    """Build pygame Sound objects. Caller must have mixer initialized."""
    sounds = {}
    for name, spec in SPECS.items():
        buf = spec()
        sounds[name] = pygame_module.mixer.Sound(buffer=buf.tobytes())
    return sounds
