import json
from typing import List
from nwg_displays.hyprland.hyprctl import hyprctl
from nwg_displays.monitor.hyprland.hyprland_monitor import HyprlandMonitor
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_service import MonitorService


class HyprlandMonitorService(MonitorService):
    def __init__(self):
        super().__init__()

    def list(self) -> List[Monitor]:
        monitors = json.loads(hyprctl("j/monitors all"))
        return [HyprlandMonitor.from_hyprland_response(monitor) for monitor in monitors]
