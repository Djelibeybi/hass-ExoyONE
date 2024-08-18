"""Helper functions."""

from __future__ import annotations

METHOD_ATTR_MAP = {
    "musicSync": "toggle_music_sync",
    "autoChange": "toggle_mode_cycle",
    "sceneGeneration": "toggle_scene_generation",
    "poweredByPowerbank": "powered_by_powerbank",
    "direction": "toggle_direction",
    "speed": "set_speed",
    "cycleSpeed": "set_cycle_speed",
    "shutdownTimer": "set_shutdown_timer",
}


def get_method_for_attribute(attr_name: str) -> str:
    """Return the method name used to update the attribute."""
    return METHOD_ATTR_MAP[attr_name]
