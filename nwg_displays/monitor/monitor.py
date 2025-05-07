from abc import ABC, abstractmethod
from typing import List, Tuple

from nwg_displays.monitor.monitor_mode import MonitorMode


class Monitor(ABC):
    """Base abstract class for monitor objects that provides an interface for getting monitor information and configurations."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the monitor."""
        pass

    @abstractmethod
    def get_make(self) -> str:
        """Get the make of the monitor."""
        pass

    @abstractmethod
    def get_model(self) -> str:
        """Get the model of the monitor."""
        pass

    @abstractmethod
    def get_serial(self) -> str:
        """Get the serial number of the monitor."""
        pass

    @abstractmethod
    def get_is_active(self) -> bool:
        """Get whether the monitor is active."""
        pass

    @abstractmethod
    def get_scale(self) -> float:
        """Get the scale of the monitor."""
        pass

    @abstractmethod
    def get_x(self) -> int:
        """Get the horizontal coordinate of the monitor."""
        pass

    @abstractmethod
    def get_y(self) -> int:
        """Get the vertical coordinate of the monitor."""
        pass

    @abstractmethod
    def get_physical_width(self) -> int:
        """Get the width of the monitor."""
        pass

    @abstractmethod
    def get_physical_height(self) -> int:
        """Get the height of the monitor."""
        pass

    @abstractmethod
    def get_physical_size(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def get_logical_width(self) -> int:
        """Get the logical width of the monitor"""
        pass

    @abstractmethod
    def get_logical_height(self) -> int:
        """Get the logical height of the monitor"""
        pass

    @abstractmethod
    def get_logical_size(self) -> Tuple[int, int]:
        """Get the logical size of the monitor"""
        pass

    @abstractmethod
    def get_refresh_rate(self) -> float:
        """Get the refresh rate of the monitor."""
        pass

    @abstractmethod
    def get_is_adaptive_sync_enabled(self) -> bool:
        """Get whether the monitor has enabled adaptive sync."""
        pass

    @abstractmethod
    def get_is_dpms_enabled(self) -> bool:
        """Get whether the monitor has DPMS enabled."""
        pass

    @abstractmethod
    def get_is_ten_bit_enabled(self) -> bool:
        """Get whether ten bit is enabled"""
        pass

    @abstractmethod
    def get_backend(self) -> str:
        """Get backend the monitor is connected with"""
        pass

    @abstractmethod
    def to_config_string(self) -> str:
        """Get the configuration string for the monitor."""
        pass

    @abstractmethod
    def is_mirror_of(self, other: "Monitor") -> None:
        """Mirror the monitor with another monitor."""
        pass

    @abstractmethod
    def is_mirror(self) -> bool:
        """Check if the monitor is a mirror."""
        pass

    @abstractmethod
    def get_modes(self) -> List[MonitorMode]:
        """Get the modes of the monitor."""
        pass
