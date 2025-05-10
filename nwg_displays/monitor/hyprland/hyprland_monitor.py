from nwg_displays.monitor.backend import MonitorBackend
from nwg_displays.monitor.hyprland.hyprland_monitor_mode import HyprlandMonitorMode
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_base_configuration import MonitorBaseConfiguration
from nwg_displays.monitor.monitor_mode import MonitorMode
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode


class HyprlandMonitor(Monitor):
    def __init__(self, config: MonitorBaseConfiguration, raw_data: dict = None):
        self.config = config
        self.raw_data = raw_data or {}

        self.transform = self.raw_data.get("transform", 0)
        self.ten_bit = self.raw_data.get("currentFormat", "") in [
            "XRGB2101010",
            "XBGR2101010",
        ]
        self.available_modes: list[MonitorMode] = [
            HyprlandMonitorMode.from_str(mode)
            for mode in self.raw_data.get("availableModes", [])
        ]
        super().__init__()

    def __repr__(self):
        return f"(HyprlandMonitor {self.get_name()} mode {self.get_width()}x{self.get_height()}@{self.get_refresh_rate()}, scale {self.get_scale()}, {len(self.available_modes)} modes, transform {self.get_transform()})"

    @classmethod
    def from_hyprland_response(cls, data: dict) -> "HyprlandMonitor":
        is_mirror_of = data.get("mirrorOf", None)
        is_mirror = False
        if is_mirror_of is not None:
            is_mirror = True
        transform_int = data.get("transform", 0)
        monitor_transform_mode: MonitorTransformMode = MonitorTransformMode(
            transform_int
        )

        config = MonitorBaseConfiguration(
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
            backend="hyprland",
            is_mirror_of=is_mirror_of,
            is_mirror=is_mirror,
        )
        return cls(config, data)

    def get_name(self):
        return self.config.name

    def get_is_active(self):
        return self.config.is_active

    def get_scale(self):
        return self.config.scale

    def get_x(self):
        return self.config.x

    def get_y(self):
        return self.config.y

    def get_width(self):
        return self.config.physical_width

    def get_height(self):
        return self.config.physical_height

    def get_size(self):
        return (self.config.physical_width, self.config.physical_height)

    def get_refresh_rate(self):
        return self.config.refresh_rate

    def get_is_adaptive_sync_enabled(self):
        return self.config.is_adaptive_sync_enabled

    def get_is_dpms_enabled(self):
        return self.config.is_dpms_enabled

    def get_is_ten_bit_enabled(self) -> bool:
        return self.config.is_ten_bit_enabled

    def get_backend(self) -> MonitorBackend:
        return self.config.backend

    def to_config_string(self):
        position = f"{self.get_x()},{self.get_y()}"
        scale = f"{self.get_scale()}"
        transform = f"transform, {self.get_transform()}"
        mode = f"{self.get_logical_width()}x{self.get_logical_height()}@{self.get_refresh_rate()}"
        return f"{self.get_name()} {position} {scale} {transform} {mode}"

    def is_mirror_of(self, other):
        return self.config.is_mirror_of == other.get_name() and self.config.is_mirror

    def is_mirror(self):
        return self.config.is_mirror

    def get_make(self):
        return self.config.make

    def get_model(self):
        return self.config.model

    def get_serial(self):
        return self.config.serial

    def get_modes(self):
        return self.available_modes

    def get_transform(self) -> MonitorTransformMode:
        return self.config.transform

    def get_is_mirror(self):
        return self.config.is_mirror

    def get_is_mirror_of(self):
        return self.config.is_mirror_of

    def get_scale_filter(self):
        raise NotImplementedError
