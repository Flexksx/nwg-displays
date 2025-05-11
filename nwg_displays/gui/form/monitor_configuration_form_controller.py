import os
from typing import List, Dict, Any, Optional, Callable
from gi.repository import Gtk, Gdk
from nwg_displays.gui.draggable_monitor_button import DraggableMonitorButton
from nwg_displays.gui.form.adjustment_form import AdjustmentForm
from nwg_displays.gui.form.boolean_form import BooleanForm
from nwg_displays.gui.form.text_form import TextForm
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.logger import logger


class MonitorConfigurationFormController:
    def __init__(
        self,
        monitors: List[Monitor],
        config: Dict[str, Any],
    ):
        self.__monitors = monitors
        self.__config = config

    def get_monitors(self) -> List[Monitor]:
        return self.__monitors

    def get_monitor_at(self, index: int = None) -> Monitor:
        if index < 0 or index >= len(self.__monitors):
            raise IndexError("Monitor index out of range.")
        return self.__monitors[index]

    def get_monitor_by_name(self, name: str) -> Optional[Monitor]:
        for monitor in self.__monitors:
            if monitor.get_name() == name:
                return monitor
        return None
