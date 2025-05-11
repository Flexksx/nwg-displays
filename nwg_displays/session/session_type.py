from enum import StrEnum


class SessionType(StrEnum):
    """Enum for session types."""

    HYPRLAND = "Hyprland"
    SWAY = "Sway"

    def __str__(self) -> str:
        return self.value
