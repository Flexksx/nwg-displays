from typing import List
from nwg_displays.monitor.backend import MonitorBackend
from nwg_displays.monitor.hyprland.hyprland_monitor_mode import HyprlandMonitorMode
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_base_configuration import MonitorConfiguration
from nwg_displays.monitor.monitor_mode import MonitorMode
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode
from gi.repository import Gdk


class HyprlandMonitor(Monitor):
    def __init__(self, config: MonitorConfiguration, raw_data: dict = None):
        super().__init__(config=config)
        self.raw_data = raw_data or {}

        self.transform = self.raw_data.get("transform", 0)
        self.ten_bit = self.raw_data.get("currentFormat", "") in [
            "XRGB2101010",
            "XBGR2101010",
        ]
        self.available_modes: List[MonitorMode] = [
            HyprlandMonitorMode.from_str(mode)
            for mode in self.raw_data.get("availableModes", [])
        ]

    def __repr__(self):
        return f"(HyprlandMonitor {self.get_name()}, (x:{self.get_x()} y:{self.get_y()}), mode {self.get_width()}x{self.get_height()}@{self.get_refresh_rate()}, scale {self.get_scale()}, {len(self.available_modes)} modes, transform {self.get_transform()})"

    @classmethod
    def from_hyprland_response(cls, data: dict) -> "HyprlandMonitor":
        is_mirror_of = data.get("mirrorOf", None)
        is_mirror = False
        if is_mirror_of is not None:
            is_mirror = True
        hyprland_transform_map = {
            0: MonitorTransformMode.NORMAL,
            1: MonitorTransformMode.ROTATE_90,
            2: MonitorTransformMode.ROTATE_180,
            3: MonitorTransformMode.ROTATE_270,
            4: MonitorTransformMode.FLIPPED,
            5: MonitorTransformMode.FLIPPED_ROTATE_90,
            6: MonitorTransformMode.FLIPPED_ROTATE_180,
            7: MonitorTransformMode.FLIPPED_ROTATE_270,
        }
        monitor_transform_mode: MonitorTransformMode = (
            hyprland_transform_map[data.get("transform", None)]
            or MonitorTransformMode.NORMAL
        )
        availableModes = data.get("availableModes", [])
        if availableModes is not None and len(availableModes) > 0:
            modes = [HyprlandMonitorMode.from_str(mode) for mode in availableModes]

        config = MonitorConfiguration(
            name=data["name"],
            make=data["make"],
            model=data["model"],
            serial=data["serial"],
            is_active=not data["disabled"],
            scale=data["scale"],
            x=data["x"],
            y=data["y"],
            physical_width=data["width"],
            physical_height=data["height"],
            refresh_rate=round(data.get("refreshRate", 0.0), 2),
            transform=monitor_transform_mode,
            is_dpms_enabled=data.get("dpmsStatus", True),
            is_adaptive_sync_enabled=data.get("vrr", False),
            is_ten_bit_enabled=data.get("currentFormat")
            in ["XRGB2101010", "XBGR2101010"],
            modes=modes,
            backend="hyprland",
            is_mirror_of=is_mirror_of,
            is_mirror=is_mirror,
        )
        return cls(config, data)

    def to_config_string(self):
        position = f"{self.get_x()}x{self.get_y()}"
        scale = f"{self.get_scale()}"
        transform_map = {
            MonitorTransformMode.NORMAL: 0,
            MonitorTransformMode.ROTATE_90: 1,
            MonitorTransformMode.ROTATE_180: 2,
            MonitorTransformMode.ROTATE_270: 3,
            MonitorTransformMode.FLIPPED: 4,
            MonitorTransformMode.FLIPPED_ROTATE_90: 5,
            MonitorTransformMode.FLIPPED_ROTATE_180: 6,
            MonitorTransformMode.FLIPPED_ROTATE_270: 7,
        }
        transform = f"transform, {transform_map[self.get_transform()]}"
        mode = f"{self.get_width()}x{self.get_height()}@{self.get_refresh_rate()}"
        return f"monitor = {self.get_name()}, {mode}, {position}, {scale}, {transform}"
