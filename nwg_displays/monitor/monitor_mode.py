from abc import ABC, abstractmethod


class MonitorMode(ABC):
    """Class to represent a monitor mode, which includes resolution and refresh rate."""

    @abstractmethod
    def get_width(self) -> int:
        """Get the width of the monitor mode."""
        pass

    @abstractmethod
    def get_height(self) -> int:
        """Get the height of the monitor mode."""
        pass

    @abstractmethod
    def get_refresh_rate(self) -> float:
        """Get the refresh rate of the monitor mode."""
        pass
