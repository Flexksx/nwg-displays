from typing import Dict, Optional
from gi.repository import Gtk, GObject
from nwg_displays.logger import get_class_logger
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_mode import MonitorMode
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode


class MonitorDisplayFormView(GObject.Object):
    """
    Monitor display form view that handles transform and modes and emits signals
    when display settings change.
    """

    # Define custom signals
    __gsignals__ = {
        "transform-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # Return type
            (object, object),  # Parameter types (monitor, transform_mode)
        ),
        "mode-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # Return type
            (object, object),  # Parameter types (monitor, selected_mode)
        ),
        "display-property-changed": (
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
        self._setup_display_widgets()

    def _setup_display_widgets(self):
        """Set up the transform and modes widgets"""
        # Transform combobox
        self.transform: Gtk.ComboBox = self._builder.get_object("transform")
        self.transform.connect("changed", self._on_transform_changed)
        transform_tooltip = self._vocabulary.get(
            "transform-tooltip", "Monitor orientation/rotation"
        )
        self.transform.set_tooltip_text(transform_tooltip)

        # Modes combobox
        self.modes: Gtk.ComboBox = self._builder.get_object("modes")
        self.modes.connect("changed", self._on_mode_changed)
        modes_tooltip = self._vocabulary.get("modes-tooltip", "Monitor display mode")
        self.modes.set_tooltip_text(modes_tooltip)

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
            if field == "transform":
                self.transform.set_active_id(str(monitor.get_transform()))
            elif field in {"width", "height", "refresh_rate", "modes"}:
                self._refresh_modes()
        finally:
            self._updating = False

    def _on_transform_changed(self, combobox: Gtk.ComboBox):
        """Handle transform selection changes"""
        if self._updating or not self._monitor:
            return

        self._updating = True
        try:
            transform_id = combobox.get_active_id()
            if transform_id:
                transform = MonitorTransformMode(transform_id)
                self._monitor.set_transform(transform)

                self.__logger.debug(
                    f"Transform changed: {self._monitor.get_name()} -> {transform}"
                )

                # Emit signals
                self.emit("transform-changed", self._monitor, transform)
                self.emit(
                    "display-property-changed", self._monitor, "transform", transform
                )
        finally:
            self._updating = False

    def _on_mode_changed(self, combobox: Gtk.ComboBox):
        """Handle mode selection changes"""
        if self._updating or not self._monitor:
            return

        self._updating = True
        try:
            idx = combobox.get_active()
            modes = self._monitor.get_modes()

            if 0 <= idx < len(modes):
                selected_mode = modes[idx]

                # Update monitor properties
                self._monitor.set_width(selected_mode.get_width())
                self._monitor.set_height(selected_mode.get_height())
                self._monitor.set_refresh_rate(selected_mode.get_refresh_rate())

                self.__logger.debug(
                    f"Mode changed: {self._monitor.get_name()} -> "
                    f"{selected_mode.get_width()}x{selected_mode.get_height()}@{selected_mode.get_refresh_rate()}Hz"
                )

                # Emit signals
                self.emit("mode-changed", self._monitor, selected_mode)
                self.emit(
                    "display-property-changed", self._monitor, "mode", selected_mode
                )
        finally:
            self._updating = False

    def refresh_all(self):
        """Refresh both transform and modes from current monitor values"""
        if not self._monitor:
            return

        self._updating = True
        try:
            self._refresh_transform()
            self._refresh_modes()
        finally:
            self._updating = False

    def _refresh_transform(self):
        """Refresh the transform combobox from current monitor values"""
        if not self._monitor:
            return

        current_transform = self._monitor.get_transform()
        self.transform.set_active_id(str(current_transform))

    def _refresh_modes(self):
        """Refresh the modes combobox from current monitor values"""
        self.__logger.debug(f"_refresh_modes called, monitor={self._monitor}")

        if not self._monitor:
            self.__logger.debug("No monitor, clearing modes")
            self.modes.remove_all()
            return

        # Clear existing modes
        self.modes.remove_all()

        # Populate with available modes
        modes = self._monitor.get_modes()
        active_index = -1

        self.__logger.debug(
            f"Populating {len(modes)} modes for {self._monitor.get_name()}"
        )

        for i, mode in enumerate(modes):
            mode_text = (
                f"{mode.get_width()}x{mode.get_height()}@{mode.get_refresh_rate()}Hz"
            )
            self.modes.append_text(mode_text)

            if (
                mode.get_width() == self._monitor.get_width()
                and mode.get_height() == self._monitor.get_height()
                and abs(mode.get_refresh_rate() - self._monitor.get_refresh_rate())
                < 0.01
            ):
                active_index = i
                self.__logger.debug(f"Found matching mode at index {i}")

        # Set the active mode
        if active_index >= 0:
            self.__logger.debug(f"Setting active mode to index {active_index}")
            self.modes.set_active(active_index)
        elif modes:
            # If no exact match found but modes exist, don't select anything
            # This indicates a custom mode
            self.__logger.debug(
                "No exact match found, setting to custom mode (no selection)"
            )
            self.modes.set_active(-1)
            self.__logger.debug(
                f"Custom mode detected for {self._monitor.get_name()}: "
                f"{self._monitor.get_width()}x{self._monitor.get_height()}@{self._monitor.get_refresh_rate()}Hz"
            )
        else:
            self.__logger.debug(
                "No modes available. Refresh the modes combobox from current monitor values"
            )
        if not self._monitor:
            self.modes.remove_all()
            return

        # Clear existing modes
        self.modes.remove_all()

        # Populate with available modes
        modes = self._monitor.get_modes()
        active_id = ""

        for i, mode in enumerate(modes):
            mode_text = (
                f"{mode.get_width()}x{mode.get_height()}@{mode.get_refresh_rate()}Hz"
            )
            self.modes.append(str(i), mode_text)

            # Check if this mode matches current monitor settings
            if (
                mode.get_width() == self._monitor.get_width()
                and mode.get_height() == self._monitor.get_height()
                and abs(mode.get_refresh_rate() - self._monitor.get_refresh_rate())
                < 0.01
            ):
                active_id = str(i)

        # Set the active mode
        if active_id:
            self.modes.set_active_id(active_id)
        elif modes:
            # If no exact match found but modes exist, don't select anything
            # This indicates a custom mode
            self.modes.set_active(-1)
            self.__logger.debug(
                f"Custom mode detected for {self._monitor.get_name()}: "
                f"{self._monitor.get_width()}x{self._monitor.get_height()}@{self._monitor.get_refresh_rate()}Hz"
            )

    def get_selected_transform(self) -> Optional[MonitorTransformMode]:
        """Get the currently selected transform"""
        if not self._monitor:
            return None
        return self._monitor.get_transform()

    def get_selected_mode(self) -> Optional[MonitorMode]:
        """Get the currently selected mode"""
        if not self._monitor:
            return None

        idx = self.modes.get_active()
        modes = self._monitor.get_modes()

        if 0 <= idx < len(modes):
            return modes[idx]
        return None

    def is_custom_mode_active(self) -> bool:
        """Check if the current monitor settings represent a custom mode"""
        if not self._monitor:
            return False

        modes = self._monitor.get_modes()
        current_width = self._monitor.get_width()
        current_height = self._monitor.get_height()
        current_refresh = self._monitor.get_refresh_rate()

        for mode in modes:
            if (
                mode.get_width() == current_width
                and mode.get_height() == current_height
                and abs(mode.get_refresh_rate() - current_refresh) < 0.01
            ):
                return False

        return True  # No matching mode found, so it's custom

    def set_transform(self, transform: MonitorTransformMode):
        """Programmatically set the transform"""
        self._updating = True
        try:
            self.transform.set_active_id(str(transform))
        finally:
            self._updating = False

    def set_mode_by_properties(self, width: int, height: int, refresh_rate: float):
        """Set the active mode based on width, height, and refresh rate"""
        if not self._monitor:
            return

        modes = self._monitor.get_modes()
        for i, mode in enumerate(modes):
            if (
                mode.get_width() == width
                and mode.get_height() == height
                and abs(mode.get_refresh_rate() - refresh_rate) < 0.01
            ):
                self._updating = True
                try:
                    self.modes.set_active(i)
                finally:
                    self._updating = False
                return

        # No exact match found - set to no selection (custom mode)
        self._updating = True
        try:
            self.modes.set_active(-1)
        finally:
            self._updating = False

    def get_monitor(self) -> Optional[Monitor]:
        """Get the current monitor"""
        return self._monitor

    def __del__(self):
        """Clean up signal connections"""
        if self._monitor_handler and self._monitor:
            self._monitor.disconnect(self._monitor_handler)
