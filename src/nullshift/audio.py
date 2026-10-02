"""Audio manager: mixer init with silent fallback, SFX routing, mute."""
import pygame

from nullshift import synth

_available = False
_sounds = {}
_muted = False
_hum_channel = None


def init() -> bool:
    global _available, _sounds
    try:
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.mixer.init()
    except pygame.error:
        _available = False
        return False
    try:
        _sounds = synth.build_all(pygame)
        _available = True
    except pygame.error:
        _available = False
    return _available


def available() -> bool:
    return _available


def play(name: str) -> None:
    if _available and not _muted and name in _sounds:
        _sounds[name].play()


def toggle_mute() -> bool:
    global _muted
    _muted = not _muted
    if _muted:
        stop_hum()
    return _muted


def muted() -> bool:
    return _muted


def start_hum() -> None:
    """Start the looping electrical hum (idempotent)."""
    global _hum_channel
    if _available and not _muted and "hum" in _sounds and _hum_channel is None:
        ch = pygame.mixer.find_channel()
        if ch is not None:
            ch.play(_sounds["hum"], loops=-1)
            _hum_channel = ch


def stop_hum() -> None:
    global _hum_channel
    if _hum_channel is not None:
        _hum_channel.stop()
        _hum_channel = None
