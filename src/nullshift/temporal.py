"""TEMPORAL state recompute (D017).

TEMPORAL = read-only during a cycle, computed once at room entry as a
pure function of (persistent flags, narrative phase, visit counters).
Never mutated by the sim, never serialized, never in recordings.

This module is the ONLY place TEMPORAL values are produced.
"""


def _condition_matches(cond: str, progression) -> bool:
    """Conditions: 'flag:NAME' (truthy) or 'phase:NAME' (equal)."""
    kind, _, name = cond.partition(":")
    if kind == "flag":
        return bool(progression.get_flag(name))
    if kind == "phase":
        return progression.phase == name
    return False


def compute(room_data: dict, progression) -> dict:
    """Return the TEMPORAL presentation for a room entry.

    {
      "lighting": "emergency" | "normal" | "low",
      "terminal_texts": {terminal_id: text},
    }
    """
    # lighting
    decl = room_data.get("lighting", "auto")
    if decl == "auto":
        lighting = "normal" if progression.get_flag("power_restored") else "emergency"
    else:
        lighting = decl
    # terminal variants: later matching variant wins (documented order)
    terminal_texts = {}
    for t in room_data.get("terminals", []):
        text = t["text"]
        for cond, variant in t.get("variants", {}).items():
            if _condition_matches(cond, progression):
                text = variant
        terminal_texts[t["id"]] = text
    return {"lighting": lighting, "terminal_texts": terminal_texts}
