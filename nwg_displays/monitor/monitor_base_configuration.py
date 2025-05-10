from typing import Optional

from nwg_displays.monitor.backend import MonitorBackend
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode


class MonitorBaseConfiguration:
    def __init__(
        self,
        name: str = "",
        make: str = "",
        model: str = "",
        serial: str = "",
        manufacturer: str = "",
        is_active: bool = False,
        scale: float = 0.0,
        x: int = 0,
        y: int = 0,
        physical_width: int = 0,
        physical_height: int = 0,
        refresh_rate: Optional[float] = 60.0,
        transform: MonitorTransformMode = MonitorTransformMode.NONE,
        is_adaptive_sync_enabled: Optional[bool] = False,
        is_dpms_enabled: Optional[bool] = False,
        is_ten_bit_enabled: Optional[bool] = False,
        backend: Optional[MonitorBackend] = None,
        is_mirror: Optional[bool] = False,
        is_mirror_of: Optional[str] = None,
    ):
        self.name = name
        self.make = make
        self.model = model
        self.serial = serial
        self.manufacturer = manufacturer
        self.is_active = is_active
        self.scale = scale
        self.x = x
        self.y = y
        self.physical_width = physical_width
        self.physical_height = physical_height
        self.refresh_rate = refresh_rate
        self.transform = transform
        self.is_adaptive_sync_enabled = is_adaptive_sync_enabled
        self.is_dpms_enabled = is_dpms_enabled
        self.is_ten_bit_enabled = is_ten_bit_enabled
        self.backend = backend or MonitorBackend.UNKNOWN
        self.is_mirror = is_mirror
        self.is_mirror_of = is_mirror_of
