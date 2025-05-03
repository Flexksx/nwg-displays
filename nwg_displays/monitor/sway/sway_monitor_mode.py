from nwg_displays.monitor.monitor_mode import MonitorMode


class SwayMonitorMode(MonitorMode):
    def __init__(self, width: int, height: int, refresh: float):
        self.width = width
        self.height = height
        self.refresh = refresh

    def __repr__(self):
        return f"SwayMonitorMode({self.width}x{self.height}@{self.refresh}Hz)"

    @classmethod
    def from_dict(cls, data: dict) -> "SwayMonitorMode":
        return cls(
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            refresh=float(data.get("refresh", 0)) / 1000.0,  # Convert µHz to Hz
        )

    def to_str(self) -> str:
        return f"{self.width}x{self.height}@{self.refresh}"
