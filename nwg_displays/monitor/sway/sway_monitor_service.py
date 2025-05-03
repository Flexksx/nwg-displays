import json
from typing import List

from nwg_displays.monitor.sway.sway_monitor import SwayMonitor
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_service import MonitorService

from i3ipc import Connection


class SwayMonitorService(MonitorService):
    def __init__(self):
        super().__init__()

    def list(self) -> List[Monitor]:
        conn = Connection()
        outputs = conn.get_outputs()

        return [
            SwayMonitor.from_sway_response(
                {
                    "name": o.name,
                    "make": o.ipc_data.get("make", ""),
                    "model": o.ipc_data.get("model", ""),
                    "serial": o.ipc_data.get("serial", ""),
                    "active": o.ipc_data.get("active", False),
                    "scale": float(o.ipc_data.get("scale", 1.0)),
                    "x": o.rect.x,
                    "y": o.rect.y,
                    "physical-width": o.ipc_data["current_mode"]["width"],
                    "physical-height": o.ipc_data["current_mode"]["height"],
                    "refresh": o.ipc_data["current_mode"]["refresh"] / 1000.0,
                    "transform": o.ipc_data.get("transform", 0),
                    "dpms": o.ipc_data.get("dpms", True),
                    "adaptive_sync_status": o.ipc_data.get(
                        "adaptive_sync_status", "disabled"
                    ),
                    "modes": o.ipc_data.get("modes", []),
                }
            )
            for o in outputs
            if not o.name.startswith("__")
        ]
