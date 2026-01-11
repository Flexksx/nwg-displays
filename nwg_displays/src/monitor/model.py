from enum import StrEnum

from gi.overrides.Gdk import Gdk
from pydantic import BaseModel, ConfigDict


class MonitorBackendName(StrEnum):
    HYPRLAND = "hyprland"
    SWAY = "sway"
    UNKNOWN = "unknown"


class MonitorConfigurationMode(BaseModel):
    width: int
    height: int
    refresh_rate: float


class MonitorTransformMode(StrEnum):
    NORMAL = "normal"
    ROTATE_90 = "90"
    ROTATE_180 = "180"
    ROTATE_270 = "270"
    FLIPPED = "flipped"
    FLIPPED_ROTATE_90 = "flipped-90"
    FLIPPED_ROTATE_180 = "flipped-180"
    FLIPPED_ROTATE_270 = "flipped-270"

    def __str__(self):
        return self.name.replace("_", " ").title()


class MonitorConfiguration(BaseModel):
    name: str
    make: str
    model: str
    serial: str
    manufacturer: str
    is_active: bool
    scale: float
    x: int
    y: int
    physical_width: int
    physical_height: int
    refresh_rate: float
    transform: MonitorTransformMode
    modes: list[MonitorConfigurationMode]
    is_adaptive_sync_enabled: bool
    is_dpms_enabled: bool
    is_ten_bit_enabled: bool
    backend: MonitorBackendName
    is_mirror: bool
    is_mirror_of: str | None
    gdk_monitor: Gdk.Monitor | None

    model_config = ConfigDict(from_attributes=True)
