from gi.repository import Gdk, GObject

from nwg_displays.logger import get_class_logger
from nwg_displays.monitor.backend import MonitorBackend
from nwg_displays.monitor.monitor_base_configuration import MonitorConfiguration
from nwg_displays.monitor.monitor_mode import MonitorMode
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode


class Monitor(GObject.GObject):
    __gsignals__ = {
        "property-changed": (GObject.SIGNAL_RUN_FIRST, None, (str, object)),
    }

    def __init__(
        self,
        config: MonitorConfiguration,
    ):
        super().__init__()
        self.__config = config
        self.__selected_mode = self.__config.modes[0] if self.__config.modes else None
        self.__logger = get_class_logger(self.__class__)

    def to_config_string(self) -> str:
        """Convert the monitor config to a string format."""
        raise NotImplementedError("Subclasses of `Monitor` must implement this method.")

    def _emit_change(self, field: str, value):
        """Internal: broadcast that a field changed."""
        self.__logger.debug(
            f"Emitting change of field {field} to {value} for {self.get_name()}"
        )
        self.emit("property-changed", field, value)

    def get_name(self) -> str:
        return self.__config.name

    def get_make(self) -> str:
        return self.__config.make

    def get_model(self) -> str:
        return self.__config.model

    def get_serial(self) -> str:
        return self.__config.serial

    def get_is_active(self) -> bool:
        return self.__config.is_active

    def get_scale(self) -> float:
        return self.__config.scale

    def get_x(self) -> int:
        return self.__config.x

    def get_y(self) -> int:
        return self.__config.y

    def get_width(self) -> int:
        return self.__config.physical_width

    def get_height(self) -> int:
        return self.__config.physical_height

    def get_size(self) -> tuple[int, int]:
        return (self.get_width(), self.get_height())

    def get_refresh_rate(self) -> float:
        return self.__config.refresh_rate

    def get_is_adaptive_sync_enabled(self) -> bool:
        return self.__config.is_adaptive_sync_enabled

    def get_is_dpms_enabled(self) -> bool:
        return self.__config.is_dpms_enabled

    def get_is_ten_bit_enabled(self) -> bool:
        return self.__config.is_ten_bit_enabled

    def get_backend(self) -> MonitorBackend:
        return self.__config.backend

    def get_modes(self) -> list[MonitorMode]:
        return self.__config.modes

    def get_transform(self) -> MonitorTransformMode:
        return self.__config.transform

    def get_is_mirror(self) -> bool:
        return self.__config.is_mirror

    def get_is_mirror_of(self) -> str | None:
        return self.__config.is_mirror_of

    def get_gdk_monitor(self) -> Gdk.Monitor | None:
        return self.__config.gdk_monitor

    def get_scale_filter(self) -> str:
        return getattr(self.__config, "scale_filter", "nearest")

    def get_selected_mode(self) -> MonitorMode | None:
        return self.__selected_mode

    def set_x(self, value: int):
        if value != self.__config.x:
            self.__config.x = value
            self._emit_change("x", value)

    def set_y(self, value: int):
        if value != self.__config.y:
            self.__config.y = value
            self._emit_change("y", value)

    def set_width(self, value: int):
        if value != self.__config.physical_width:
            self.__config.physical_width = value
            self._emit_change("width", value)

    def set_height(self, value: int):
        if value != self.__config.physical_height:
            self.__config.physical_height = value
            self._emit_change("height", value)

    def set_scale(self, value: float):
        self.__logger.info(f"Set scale to {value} for {self.__config.name}")
        if value != self.__config.scale:
            self.__config.scale = value
            self._emit_change("scale", value)

    def set_refresh_rate(self, value: float):
        self.__logger.info(f"Set refresh rate to {value} for {self.__config.name}")
        if value != self.__config.refresh_rate:
            self.__config.refresh_rate = value
            self._emit_change("refresh_rate", value)

    def set_is_adaptive_sync_enabled(self, value: bool):
        self.__logger.info(f"Set adaptive sync to {value} for {self.__config.name}")
        if value != self.__config.is_adaptive_sync_enabled:
            self.__config.is_adaptive_sync_enabled = value
            self._emit_change("adaptive_sync", value)

    def set_is_dpms_enabled(self, value: bool):
        self.__logger.info(f"Set DPMS to {value} for {self.__config.name}")
        if value != self.__config.is_dpms_enabled:
            self.__config.is_dpms_enabled = value
            self._emit_change("dpms", value)

    def set_is_ten_bit_enabled(self, value: bool):
        self.__logger.info(f"Set 10-bit to {value} for {self.__config.name}")
        if value != self.__config.is_ten_bit_enabled:
            self.__config.is_ten_bit_enabled = value
            self._emit_change("ten_bit", value)

    def set_transform(self, value: MonitorTransformMode):
        self.__logger.info(
            f"[{self.get_name()}] Set transform to {value} for {self.__config.name}"
        )
        if value != self.__config.transform:
            self.__config.transform = value
            self._emit_change("transform", value)

    def set_gdk_monitor(self, monitor: Gdk.Monitor):
        if monitor != self.__config.gdk_monitor:
            self.__config.gdk_monitor = monitor
            self._emit_change("gdk_monitor", monitor)

    def set_mirror(self, target_name: str | None):
        """Hyprland-specific helper: make this display a mirror of *target* or clear."""
        self.__config.is_mirror_of = target_name
        self.__config.is_mirror = target_name is not None
        self._emit_change("mirror", target_name)
