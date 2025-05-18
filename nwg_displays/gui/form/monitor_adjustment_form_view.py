from typing import Dict
import os
from typing import Callable, Dict, List, Optional, Any
from gi.repository import Gtk, GObject
from nwg_displays.gui.form.adjustment_form import AdjustmentForm
from nwg_displays.gui.form.boolean_form import BooleanForm
from nwg_displays.gui.form.text_form import TextForm
from nwg_displays.logger import get_class_logger
from nwg_displays.monitor.monitor import Monitor


class MonitorAdjustmentFormView(GObject.Object):
    """
    Monitor adjustment form view that handles monitor position, size, scale, and refresh widgets
    and emits signals when monitor properties change.
    """

    __gsignals__ = {
        "monitor-position-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # Return type
            (object, int, int),  # Parameter types (monitor, x, y)
        ),
        "monitor-size-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # Return type
            (object, int, int),  # Parameter types (monitor, width, height)
        ),
        "monitor-scale-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # Return type
            (object, float),  # Parameter types (monitor, scale)
        ),
        "monitor-refresh-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # Return type
            (object, float),  # Parameter types (monitor, refresh_rate)
        ),
        "monitor-property-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # Return type
            (
                object,
                str,
                object,
            ),  # Parameter types (monitor, property_name, new_value)
        ),
    }

    def __init__(self, builder: Gtk.Builder, vocabulary: Dict[str, str]):
        super().__init__()
        self.__logger = get_class_logger(self.__class__)
        self._builder = builder
        self._vocabulary = vocabulary
        self._updating = False
        self._monitor: Optional[Monitor] = None
        self._monitor_handler: Optional[int] = None
        self._setup_adjustment_widgets()

    def _setup_adjustment_widgets(self):
        """Set up all the adjustment widgets"""

        # Position adjustments
        self.x = self._create_adjustment(
            "x",
            0,
            60000,
            self._on_x_changed,
            digits=0,
            tooltip=self._vocabulary.get("x-tooltip", "Monitor X position"),
        )
        self.y = self._create_adjustment(
            "y",
            0,
            40000,
            self._on_y_changed,
            digits=0,
            tooltip=self._vocabulary.get("y-tooltip", "Monitor Y position"),
        )

        # Size adjustments
        self.width = self._create_adjustment(
            "width",
            0,
            7680,
            self._on_width_changed,
            digits=0,
            tooltip=self._vocabulary.get("width-tooltip", "Monitor width"),
        )
        self.height = self._create_adjustment(
            "height",
            0,
            4320,
            self._on_height_changed,
            digits=0,
            tooltip=self._vocabulary.get("height-tooltip", "Monitor height"),
        )

        # Scale adjustment
        self.scale = self._create_adjustment(
            "scale",
            0.1,
            10.0,
            self._on_scale_changed,
            digits=2,
            step=0.1,
            tooltip=self._vocabulary.get("scale-tooltip", "Monitor scale factor"),
        )

        # Refresh rate adjustment
        self.refresh = self._create_adjustment(
            "refresh",
            1,
            1200,
            self._on_refresh_changed,
            digits=2,
            tooltip=self._vocabulary.get("refresh-tooltip", "Monitor refresh rate"),
        )

    def _create_adjustment(
        self,
        name: str,
        low: float,
        up: float,
        callback: Callable,
        *,
        step: float = 1,
        page: float = 10,
        digits: int = 2,
        tooltip: str = None,
    ):
        """Create an adjustment form widget"""
        adj = AdjustmentForm(
            builder=self._builder,
            glade_name=name,
            on_event_callback=("value-changed", callback),
            lower_bound=low,
            upper_bound=up,
            step_increment=step,
            page_increment=page,
            page_size=1,
            climb_rate=step,
            digits=digits,
        )
        if tooltip:
            adj.get_form().set_tooltip_text(tooltip)
        return adj

    def set_monitor(self, monitor: Monitor):
        """Set the monitor to control"""
        # Disconnect from previous monitor
        if self._monitor_handler and self._monitor:
            self._monitor.disconnect(self._monitor_handler)

        self._monitor = monitor

        # Connect to monitor property changes
        if monitor:
            self._monitor_handler = monitor.connect(
                "property-changed", self._on_monitor_change
            )

        self.refresh_all()

    def _on_monitor_change(self, monitor: Monitor, field: str, value):
        """Handle external monitor changes and update widgets accordingly"""
        if self._updating:
            return
        self._updating = True
        try:
            if field == "x":
                self.x.set_value(monitor.get_x())
            elif field == "y":
                self.y.set_value(monitor.get_y())
            elif field == "width":
                self.width.set_value(monitor.get_width())
            elif field == "height":
                self.height.set_value(monitor.get_height())
            elif field == "scale":
                self.scale.set_value(monitor.get_scale())
            elif field == "refresh_rate":
                self.refresh.set_value(monitor.get_refresh_rate())
        finally:
            self._updating = False

    def _on_x_changed(self, adjustment: Gtk.Adjustment):
        """Handle X position changes"""
        if self._updating or not self._monitor:
            return
        self._updating = True
        try:
            new_value = int(round(adjustment.get_value()))
            self._monitor.set_x(new_value)
            self.__logger.debug(f"Monitor X changed to {new_value}")

            # Emit signals
            self.emit(
                "monitor-position-changed",
                self._monitor,
                new_value,
                self._monitor.get_y(),
            )
            self.emit("monitor-property-changed", self._monitor, "x", new_value)
        finally:
            self._updating = False

    def _on_y_changed(self, adjustment: Gtk.Adjustment):
        """Handle Y position changes"""
        if self._updating or not self._monitor:
            return
        self._updating = True
        try:
            new_value = int(round(adjustment.get_value()))
            self._monitor.set_y(new_value)
            self.__logger.debug(f"Monitor Y changed to {new_value}")

            # Emit signals
            self.emit(
                "monitor-position-changed",
                self._monitor,
                self._monitor.get_x(),
                new_value,
            )
            self.emit("monitor-property-changed", self._monitor, "y", new_value)
        finally:
            self._updating = False

    def _on_width_changed(self, adjustment: Gtk.Adjustment):
        """Handle width changes"""
        if self._updating or not self._monitor:
            return
        self._updating = True
        try:
            new_value = int(round(adjustment.get_value()))
            self._monitor.set_width(new_value)
            self.__logger.debug(f"Monitor width changed to {new_value}")

            # Emit signals
            self.emit(
                "monitor-size-changed",
                self._monitor,
                new_value,
                self._monitor.get_height(),
            )
            self.emit("monitor-property-changed", self._monitor, "width", new_value)
        finally:
            self._updating = False

    def _on_height_changed(self, adjustment: Gtk.Adjustment):
        """Handle height changes"""
        if self._updating or not self._monitor:
            return
        self._updating = True
        try:
            new_value = int(round(adjustment.get_value()))
            self._monitor.set_height(new_value)
            self.__logger.debug(f"Monitor height changed to {new_value}")

            # Emit signals
            self.emit(
                "monitor-size-changed",
                self._monitor,
                self._monitor.get_width(),
                new_value,
            )
            self.emit("monitor-property-changed", self._monitor, "height", new_value)
        finally:
            self._updating = False

    def _on_scale_changed(self, adjustment: Gtk.Adjustment):
        """Handle scale changes"""
        if self._updating or not self._monitor:
            return
        self._updating = True
        try:
            new_value = adjustment.get_value()
            self._monitor.set_scale(new_value)
            self.__logger.debug(f"Monitor scale changed to {new_value}")

            # Emit signals
            self.emit("monitor-scale-changed", self._monitor, new_value)
            self.emit("monitor-property-changed", self._monitor, "scale", new_value)
        finally:
            self._updating = False

    def _on_refresh_changed(self, adjustment: Gtk.Adjustment):
        """Handle refresh rate changes"""
        if self._updating or not self._monitor:
            return
        self._updating = True
        try:
            new_value = adjustment.get_value()
            self._monitor.set_refresh_rate(new_value)
            self.__logger.debug(f"Monitor refresh rate changed to {new_value}")

            # Emit signals
            self.emit("monitor-refresh-changed", self._monitor, new_value)
            self.emit(
                "monitor-property-changed", self._monitor, "refresh_rate", new_value
            )
        finally:
            self._updating = False

    def refresh_all(self):
        """Refresh all widgets from current monitor values"""
        if not self._monitor:
            return

        self._updating = True
        try:
            self.x.set_value(self._monitor.get_x())
            self.y.set_value(self._monitor.get_y())
            self.width.set_value(self._monitor.get_width())
            self.height.set_value(self._monitor.get_height())
            self.scale.set_value(self._monitor.get_scale())
            self.refresh.set_value(self._monitor.get_refresh_rate())
        finally:
            self._updating = False

    def get_monitor(self) -> Optional[Monitor]:
        """Get the current monitor"""
        return self._monitor

    def __del__(self):
        """Clean up signal connections"""
        if self._monitor_handler and self._monitor:
            self._monitor.disconnect(self._monitor_handler)
