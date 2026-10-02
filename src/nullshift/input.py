"""Input polling. Continuous actions from key state, edge actions from KEYDOWN.

Testability: sim.tick() takes the action dict directly — no pygame needed.
"""
import pygame

from nullshift import config

_hold = {}
_edge = {}


def _init_maps():
    for action, names in config.KEYMAP.items():
        _hold[action] = [getattr(pygame, n) for n in names]
    for action, names in config.EDGE_KEYS.items():
        _edge[action] = [getattr(pygame, n) for n in names]


_init_maps()


def poll(just_pressed: set) -> dict:
    keys = pygame.key.get_pressed()
    actions = {a: any(keys[k] for k in codes) for a, codes in _hold.items()}
    for a, codes in _edge.items():
        actions[a] = any(k in just_pressed for k in codes)
    return actions


def empty_actions() -> dict:
    actions = {a: False for a in list(_hold) + list(_edge)}
    return actions
