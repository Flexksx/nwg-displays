from enum import StrEnum


class MonitorBackend(StrEnum):
    HYPRLAND = "hyprland"
    SWAY = "sway"
    UNKNOWN = "unknown"
