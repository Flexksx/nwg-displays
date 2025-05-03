from nwg_displays.monitor.backend import MonitorBackend
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_base_configuration import MonitorBaseConfiguration


class SwayMonitor(Monitor):
    def __init__(self, config: MonitorBaseConfiguration, raw_data: dict = None):
        self.config = config
        self.raw_data = raw_data or {}

        self.transform = self.raw_data.get("transform", 0)
        self.ten_bit = False  # Sway doesn't expose 10-bit format detection
        super().__init__()

    def __repr__(self):
        return f"(SwayMonitor {self.get_name()} mode {self.get_physical_width()}x{self.get_physical_height()}@{self.get_refresh_rate()}, scale {self.get_scale()})"

    @classmethod
    def from_sway_response(cls, data: dict) -> "SwayMonitor":
        config = MonitorBaseConfiguration(
            name=data["name"],
            make=data["make"],
            model=data["model"],
            serial=data["serial"],
            is_active=data.get("active", True),
            scale=data.get("scale", 1.0),
            x=data.get("x", 0),
            y=data.get("y", 0),
            physical_width=data["physical-width"],
            physical_height=data["physical-height"],
            refresh_rate=data.get("refresh", 0.0),
            transform=data.get("transform", 0),
            is_dpms_enabled=data.get("dpms", True),
            is_adaptive_sync_enabled=data.get("adaptive_sync_status", "") == "enabled",
            is_ten_bit_enabled=False,  # Can't determine on sway
            backend="sway",
        )
        return cls(config, data)

    def get_name(self):
        return self.config.name

    def get_make(self):
        return self.config.make

    def get_model(self):
        return self.config.model

    def get_serial(self):
        return self.config.serial

    def get_is_active(self):
        return self.config.is_active

    def get_scale(self):
        return self.config.scale

    def get_x(self):
        return self.config.x

    def get_y(self):
        return self.config.y

    def get_physical_width(self):
        return self.config.physical_width

    def get_physical_height(self):
        return self.config.physical_height

    def get_physical_size(self):
        return (self.config.physical_width, self.config.physical_height)

    def get_logical_width(self):
        return self.config.physical_width / self.config.scale

    def get_logical_height(self):
        return self.config.physical_height / self.config.scale

    def get_logical_size(self):
        return (self.get_logical_width(), self.get_logical_height())

    def get_refresh_rate(self):
        return self.config.refresh_rate

    def get_is_adaptive_sync_enabled(self):
        return self.config.is_adaptive_sync_enabled

    def get_is_dpms_enabled(self):
        return self.config.is_dpms_enabled

    def get_is_ten_bit_enabled(self):
        return self.config.is_ten_bit_enabled

    def get_backend(self) -> MonitorBackend:
        return self.config.backend

    def to_config_string(self):
        position = f"{self.get_x()},{self.get_y()}"
        scale = f"{self.get_scale()}"
        transform = f"transform,{self.get_transform()}"
        mode = f"{self.get_logical_width()}x{self.get_logical_height()}@{self.get_refresh_rate()}"
        return f"{self.get_name()} {position} {scale} {transform} {mode}"

    def is_mirror_of(self, other):
        return False  # Not implemented or detectable on sway

    def is_mirror(self):
        return False  # Not implemented or detectable on sway

    def get_transform(self):
        return self.config.transform
