"""Resource path resolution: dev tree vs PyInstaller bundle (sys._MEIPASS)."""
import os
import sys


def project_root() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore[attr-defined]
    # src/nullshift/paths.py -> repo root (three levels up)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resource_path(*parts: str) -> str:
    return os.path.join(project_root(), *parts)


def rooms_dir() -> str:
    return resource_path("data", "rooms")


def art_dir() -> str:
    return resource_path("assets", "art")
