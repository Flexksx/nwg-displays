import json

from nwg_displays.hyprland.hyprctl import hyprctl
from nwg_displays.src.monitor.model import MonitorConfiguration
from nwg_displays.src.monitor.service import MonitorService


class HyprlandMonitorService(MonitorService):
    def list(self):
        monitors = json.loads(hyprctl("j/monitors all"))
        return [MonitorConfiguration.model_validate(monitor) for monitor in monitors]
