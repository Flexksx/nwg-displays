from nwg_displays.monitor.backend import MonitorBackend
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_base_configuration import MonitorBaseConfiguration
from nwg_displays.monitor.monitor_mode import MonitorMode


class SwayMonitor(Monitor):
    def __init__(self, config: MonitorBaseConfiguration, raw_data: dict = None):
        super().__init__()
        self.config = config
        self.raw_data = raw_data or {}

    @classmethod
    def from_sway_response(cls, data: dict) -> "SwayMonitor":
        config = MonitorBaseConfiguration(
            name=data["name"],
            make=data.get("make", ""),
            model=data.get("model", ""),
            serial=data.get("serial", ""),
            is_active=data.get("active", False),
            scale=data.get("scale", 1.0),
            x=data.get("x", 0),
            y=data.get("y", 0),
            physical_width=data["physical-width"],
            physical_height=data["physical-height"],
            refresh_rate=round(data["refresh"], 2),
            transform=data.get("transform", 0),
            is_dpms_enabled=data.get("dpms", True),
            is_adaptive_sync_enabled=(
                data.get("adaptive_sync_status", "") == "enabled"
            ),
            is_ten_bit_enabled=False,  # Sway doesn’t expose ten-bit
            backend="sway",
            is_mirror_of=None,  # Sway doesn’t expose mirror info
            is_mirror=False,
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

    def get_width(self):
        return self.config.physical_width

    def get_height(self):
        return self.config.physical_height

    def get_size(self):
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

    def get_backend(self):
        return MonitorBackend.SWAY

    def to_config_string(self):
        return (
            f"{self.get_name()} "
            f"{self.get_x()},{self.get_y()} "
            f"scale,{self.get_scale()} "
            f"transform,{self.config.transform} "
            f"{int(self.get_logical_width())}x{int(self.get_logical_height())}@{self.get_refresh_rate()}"
        )

    def is_mirror_of(self, other):
        return False

    def is_mirror(self):
        return False

    def get_modes(self):
        return []
