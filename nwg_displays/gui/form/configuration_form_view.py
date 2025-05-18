from typing import Dict
import os
from typing import Callable, Dict, List, Optional, Any
from gi.repository import Gtk, GObject
from nwg_displays.config.nwg_displays_config import (
    DEFAULT_VIEW_SCALE,
    ConfigurationService,
)
from nwg_displays.gui.draggable_monitor_button import DraggableMonitorButton
from nwg_displays.gui.form.adjustment_form import AdjustmentForm
from nwg_displays.gui.form.boolean_form import BooleanForm
from nwg_displays.gui.form.text_form import TextForm
from nwg_displays.logger import get_class_logger
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_mode import MonitorMode
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode
from nwg_displays.session.session_service import SessionService

session_service = SessionService()
configuration_service = ConfigurationService.get()


class ConfigurationFormView(GObject.Object):
    """
    Configuration form view that handles config-related widgets and emits signals
    when configuration changes occur.
    """

    __gsignals__ = {
        "view-scale-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (float,),
        ),
        "use-desc-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (bool,),
        ),
        "config-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (str, object),
        ),
    }

    def __init__(self, builder: Gtk.Builder, config, vocabulary: Dict[str, str]):
        super().__init__()
        self.__logger = get_class_logger(self.__class__)
        self._builder = builder
        self._config = config
        self._vocabulary = vocabulary
        self._updating = False
        self._setup_config_widgets()

    def _setup_config_widgets(self):
        init_view_scale = self._config.view_scale or DEFAULT_VIEW_SCALE
        self.__logger.debug(f"View scale from config={init_view_scale}")

        # Set up view scale widget
        self.view_scale_spin = self._builder.get_object("view-scale")
        self.view_scale_adjustment = Gtk.Adjustment(
            value=init_view_scale,
            lower=0.05,
            upper=1.0,
            step_increment=0.05,
            page_increment=0.1,
            page_size=0,
        )
        self.view_scale_adjustment.connect(
            "value-changed",
            self._on_view_scale_change,
        )
        self.view_scale_spin.set_adjustment(self.view_scale_adjustment)
        self.view_scale_spin.set_digits(2)
        self.view_scale_spin.set_tooltip_text(
            self._vocabulary.get(
                "view-scale-tooltip",
                "Scale factor for the view. 1.0 = 100%.",
            )
        )

        # Set up use description widget
        self.use_desc = BooleanForm(
            builder=self._builder,
            glade_name="use-desc",
            on_event_callback=("toggled", self._on_use_desc_change),
            tooltip=self._vocabulary.get(
                "use-desc-tooltip",
                "Show EDID description instead of connector name.",
            ),
        )

        # Connect to config changes if supported
        if hasattr(self._config, "connect"):
            self._config_handler = self._config.connect(
                "property-changed", self._on_config_change
            )

    def _on_config_change(self, _config, field: str, value):
        """Handle external config changes and update widgets accordingly"""
        if self._updating:
            return
        self._updating = True
        try:
            if field == "view_scale":
                self.view_scale_adjustment.set_value(value or DEFAULT_VIEW_SCALE)
            elif field == "use_desc":
                self.use_desc.set_active(value)
        finally:
            self._updating = False

    def _on_view_scale_change(self, adjustment: Gtk.Adjustment):
        """Handle view scale widget changes"""
        if self._updating:
            return
        self._updating = True
        try:
            new_value = adjustment.get_value()
            self._config.view_scale = new_value
            self.__logger.debug(f"View scale changed to {new_value}")

            # Emit custom signal for parent to handle
            self.emit("view-scale-changed", new_value)
            self.emit("config-changed", "view_scale", new_value)
        finally:
            self._updating = False

    def _on_use_desc_change(self, widget: Gtk.CheckButton):
        """Handle use description widget changes"""
        if self._updating:
            return
        self._updating = True
        try:
            new_value = widget.get_active()
            self._config.use_desc = new_value
            self.__logger.debug(f"Use description changed to {new_value}")

            # Emit custom signal for parent to handle
            self.emit("use-desc-changed", new_value)
            self.emit("config-changed", "use_desc", new_value)
        finally:
            self._updating = False

    def refresh_all(self):
        """Refresh all widgets from current config values"""
        self._updating = True
        try:
            self.view_scale_adjustment.set_value(
                self._config.view_scale or DEFAULT_VIEW_SCALE
            )
            self.use_desc.set_active(self._config.use_desc)
        finally:
            self._updating = False

    def get_view_scale(self) -> float:
        """Get current view scale value"""
        return self.view_scale_adjustment.get_value()

    def get_use_desc(self) -> bool:
        """Get current use description value"""
        return self.use_desc.get_active()

    def __del__(self):
        """Clean up signal connections"""
        if hasattr(self, "_config_handler") and hasattr(self._config, "disconnect"):
            self._config.disconnect(self._config_handler)
