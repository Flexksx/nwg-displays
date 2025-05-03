from nwg_displays.monitor.monitor_mode import MonitorMode


class HyprlandMonitorMode(MonitorMode):
    def __init__(self, width: int, height: int, refresh_rate: float):
        self.width = width
        self.height = height
        self.refresh_rate = refresh_rate

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_refresh_rate(self):
        return self.refresh_rate

    @classmethod
    def from_str(cls, mode_string: str):
        """Create a HyprlandMonitorMode instance from a mode string."""
        width, height_and_refresh_rate = mode_string.split("x")
        height, refresh_rate = height_and_refresh_rate.split("@")
        width = int(width)
        height = int(height)
        refresh_rate = float(refresh_rate.removesuffix("Hz"))
        return cls(width, height, refresh_rate)

    def __str__(self):
        """Return a string representation of the monitor mode."""
        return f"{self.width}x{self.height}@{self.refresh_rate}"

    def __repr__(self):
        """Return a string representation of the monitor mode."""
        return f"HyprlandMonitorMode(width={self.width}, height={self.height}, refresh_rate={self.refresh_rate})"
