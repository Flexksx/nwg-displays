import os
from typing import Callable, Dict, List, Optional, Any

from gi.repository import Gtk

from nwg_displays.config.nwg_displays_config import ConfigurationService
from nwg_displays.gui.draggable_monitor_button import DraggableMonitorButton
from nwg_displays.gui.form.boolean_form import BooleanForm
from nwg_displays.gui.form.configuration_form_view import ConfigurationFormView
from nwg_displays.gui.form.monitor_adjustment_form_view import MonitorAdjustmentFormView
from nwg_displays.gui.form.text_form import TextForm
from nwg_displays.logger import get_class_logger
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_mode import MonitorMode
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode
from nwg_displays.session.session_service import SessionService

session_service = SessionService()
configuration_service = ConfigurationService.get()  # Singleton access


class MonitorConfigurationFormView:
    """
    GTK side-panel that edits one :class:`Monitor`.

    The view listens to the model's ``property-changed`` signal and updates its
    widgets automatically.  Conversely, every widget callback writes back to the
    model, so *any* change (dragging, other scripts, hot-plug) propagates to all
    views.
    """

    def __init__(
        self,
        builder: Gtk.Builder,
        monitor_buttons: List[DraggableMonitorButton],
        vocabulary: Dict[str, str],
        fixed_container: Gtk.Fixed,
        on_monitor_changed_callback: Optional[Callable[[Monitor], None]] = None,
    ):
        self.__logger = get_class_logger(self.__class__)
        self._builder = builder
        self._buttons = monitor_buttons
        self._config = configuration_service.get_config()
        self.__logger.debug(f"MonitorConfigurationFormView config={self._config}")
        self._vocab = vocabulary
        self._fixed = fixed_container
        self._notify_parent = on_monitor_changed_callback

        self._monitor: Optional[Monitor] = None
        self._monitor_handler: Optional[int] = None
        self._updating = False
        self._setup_widgets()

        # Create configuration form view with signal connections
        self._configuration_form_view = ConfigurationFormView(
            builder=self._builder, config=self._config, vocabulary=self._vocab
        )
        self._configuration_form_view.connect(
            "view-scale-changed", self._on_view_scale_changed
        )

        # Create monitor adjustment form view with signal connections
        self._monitor_adjustment_form_view = MonitorAdjustmentFormView(
            builder=self._builder,
            vocabulary=self._vocab,
        )
        self._monitor_adjustment_form_view.connect(
            "monitor-position-changed", self._on_monitor_position_changed
        )
        self._monitor_adjustment_form_view.connect(
            "monitor-size-changed", self._on_monitor_size_changed
        )
        self._monitor_adjustment_form_view.connect(
            "monitor-scale-changed", self._on_monitor_scale_changed
        )
        self._monitor_adjustment_form_view.connect(
            "monitor-refresh-changed", self._on_monitor_refresh_changed
        )
        self._monitor_adjustment_form_view.connect(
            "monitor-property-changed", self._on_monitor_property_changed
        )

        if monitor_buttons:
            self.set_selected_monitor(monitor_buttons[0].get_monitor())

    def _setup_widgets(self) -> None:
        v, b = self._vocab, self._builder

        # Text form widgets
        self.name = TextForm(
            builder=b,
            glade_name="name",
            tooltip=v.get("name-tooltip", "Monitor name"),
        )
        self.desc = TextForm(
            builder=b,
            glade_name="description",
            tooltip=v.get("description-tooltip", "Monitor description"),
        )

        # Boolean form widgets
        self.dpms = BooleanForm(
            builder=b,
            glade_name="dpms",
            on_event_callback=("toggled", self._on_dpms_changed),
            tooltip=v.get("dpms-tooltip", "DPMS (turn display off when idle)"),
        )
        self.sync = BooleanForm(
            builder=b,
            glade_name="adaptive-sync",
            on_event_callback=("toggled", self._on_adaptive_sync_changed),
            tooltip=v.get(
                "adaptive-sync-tooltip",
                "Variable Refresh Rate / FreeSync / G-Sync.",
            ),
        )
        self.custom = BooleanForm(
            builder=b,
            glade_name="custom-mode",
            on_event_callback=("toggled", self._on_custom_toggled),
            tooltip=v.get(
                "custom-mode-tooltip",
                "Add '--custom' to sway's *mode* command.",
            ),
        )

        # Other combo box widgets
        self.scale_filter: Gtk.ComboBox = b.get_object("scale-filter")
        self.scale_filter.connect("changed", self._on_scale_filter)

        self.transform: Gtk.ComboBox = b.get_object("transform")
        self.transform.connect("changed", self._on_transform)

        self.modes: Gtk.ComboBox = b.get_object("modes")
        self.modes.connect("changed", self._on_mode)

        # Hyprland-specific widgets
        self.ten_bit: Optional[Gtk.CheckButton] = None
        self.mirror: Optional[Gtk.ComboBox] = None
        if session_service.is_hyprland_session():
            grid: Gtk.Grid = b.get_object("grid")

            self.ten_bit = Gtk.CheckButton.new_with_label(
                v.get("10-bit-support", "10 bit support"),
            )
            self.ten_bit.set_tooltip_text(
                v.get("10-bit-support-tooltip", "Enable 10-bit colour depth."),
            )
            self.ten_bit.connect("toggled", self._on_ten_bit)
            grid.attach(self.ten_bit, 5, 4, 1, 1)

            lbl = Gtk.Label.new("Mirror:")
            lbl.set_property("halign", Gtk.Align.END)
            grid.attach(lbl, 6, 4, 1, 1)

            self.mirror = Gtk.ComboBoxText()
            self.mirror.connect("changed", self._on_mirror)
            grid.attach(self.mirror, 7, 4, 1, 1)

    def set_selected_monitor(self, m: Monitor) -> None:
        # Set monitor on the adjustment form (this handles disconnecting from previous monitor)
        self._monitor_adjustment_form_view.set_monitor(m)

        # Handle monitor property changes for non-adjustment properties
        if self._monitor_handler and self._monitor:
            self._monitor.disconnect(self._monitor_handler)

        self._monitor = m
        self._monitor_handler = m.connect("property-changed", self._on_model_change)
        self._refresh_all()

    def _on_model_change(self, _m: Monitor, field: str, _value) -> None:
        """Handle monitor property changes for non-adjustment properties"""
        if self._updating:
            return
        self._updating = True
        try:
            if field == "dpms":
                self.dpms.set_active(self._monitor.get_is_dpms_enabled())
            elif field == "adaptive_sync":
                self.sync.set_active(self._monitor.get_is_adaptive_sync_enabled())
            elif field in {"transform", "modes"}:
                self._refresh_transform_and_modes()
            elif self.ten_bit and field == "ten_bit":
                self.ten_bit.set_active(self._monitor.get_is_ten_bit_enabled())
            elif self.mirror and field == "mirror":
                self._populate_mirror_combo()
        finally:
            self._updating = False

    # Signal handlers for configuration changes
    def _on_view_scale_changed(self, config_form: ConfigurationFormView, value: float):
        """Handle view scale changes from configuration form"""
        for button in self._buttons:
            button.rescale_transform()
            self._fixed.move(
                button,
                button.get_monitor().get_x() * value,
                button.get_monitor().get_y() * value,
            )

    # Signal handlers for monitor adjustment changes
    def _on_monitor_position_changed(
        self, adjustment_form, monitor: Monitor, x: int, y: int
    ):
        """Handle monitor position changes from adjustment form"""
        self.__logger.debug(
            f"Monitor position changed: {monitor.get_name()} -> ({x}, {y})"
        )
        if self._notify_parent:
            self._notify_parent(monitor)

    def _on_monitor_size_changed(
        self, adjustment_form, monitor: Monitor, width: int, height: int
    ):
        """Handle monitor size changes from adjustment form"""
        self.__logger.debug(
            f"Monitor size changed: {monitor.get_name()} -> {width}x{height}"
        )
        if self._notify_parent:
            self._notify_parent(monitor)

    def _on_monitor_scale_changed(
        self, adjustment_form, monitor: Monitor, scale: float
    ):
        """Handle monitor scale changes from adjustment form"""
        self.__logger.debug(
            f"Monitor scale changed: {monitor.get_name()} -> scale {scale}"
        )
        if self._notify_parent:
            self._notify_parent(monitor)

    def _on_monitor_refresh_changed(
        self, adjustment_form, monitor: Monitor, refresh_rate: float
    ):
        """Handle monitor refresh rate changes from adjustment form"""
        self.__logger.debug(
            f"Monitor refresh rate changed: {monitor.get_name()} -> {refresh_rate}Hz"
        )
        if self._notify_parent:
            self._notify_parent(monitor)

    def _on_monitor_property_changed(
        self, adjustment_form, monitor: Monitor, property_name: str, new_value
    ):
        """Handle general monitor property changes from adjustment form"""
        self.__logger.debug(
            f"Monitor property changed: {monitor.get_name()}.{property_name} = {new_value}"
        )

    # Widget event handlers
    def _on_dpms_changed(self, btn: Gtk.ToggleButton):
        """Handle DPMS checkbox changes"""
        if self._monitor is None or self._updating:
            return
        self._monitor.set_is_dpms_enabled(btn.get_active())
        if self._notify_parent:
            self._notify_parent(self._monitor)

    def _on_adaptive_sync_changed(self, btn: Gtk.ToggleButton):
        """Handle adaptive sync checkbox changes"""
        if self._monitor is None or self._updating:
            return
        self._monitor.set_is_adaptive_sync_enabled(btn.get_active())
        if self._notify_parent:
            self._notify_parent(self._monitor)

    def _on_custom_toggled(self, btn: Gtk.ToggleButton):
        """Handle custom mode checkbox changes"""
        if self._monitor is None:
            return
        modes = set(self._config.custom_mode)
        if btn.get_active():
            modes.add(self._monitor.get_name())
        else:
            modes.discard(self._monitor.get_name())
        self._config.custom_mode = list(modes)
        if self._notify_parent:
            self._notify_parent(self._monitor)

    def _on_transform(self, box: Gtk.ComboBox):
        """Handle transform combobox changes"""
        if self._updating or self._monitor is None:
            return
        tid = box.get_active_id()
        if tid:
            transform = MonitorTransformMode(tid)
            self._monitor.set_transform(transform)
            if self._notify_parent:
                self._notify_parent(self._monitor)

    def _on_scale_filter(self, box: Gtk.ComboBox):
        """Handle scale filter combobox changes"""
        if self._updating or self._monitor is None:
            return
        sid = box.get_active_id()
        if sid and hasattr(self._monitor, "set_scale_filter"):
            self._monitor.set_scale_filter(sid)
            if self._notify_parent:
                self._notify_parent(self._monitor)

    def _on_mode(self, box: Gtk.ComboBox):
        """Handle mode combobox changes"""
        if self._updating or self._monitor is None:
            return
        idx = box.get_active()
        modes = self._monitor.get_modes()
        if 0 <= idx < len(modes):
            mode: MonitorMode = modes[idx]
            self._monitor.set_width(mode.get_width())
            self._monitor.set_height(mode.get_height())
            self._monitor.set_refresh_rate(mode.get_refresh_rate())
            if self._notify_parent:
                self._notify_parent(self._monitor)

    def _on_ten_bit(self, btn: Gtk.ToggleButton):
        """Handle 10-bit checkbox changes (Hyprland only)"""
        if self._updating or self._monitor is None:
            return
        self._monitor.set_is_ten_bit_enabled(btn.get_active())
        if self._notify_parent:
            self._notify_parent(self._monitor)

    def _on_mirror(self, box: Gtk.ComboBox):
        """Handle mirror combobox changes (Hyprland only)"""
        if self._updating or not self.mirror or self._monitor is None:
            return
        self._monitor.set_mirror(box.get_active_id())
        if self._notify_parent:
            self._notify_parent(self._monitor)

    def _refresh_all(self) -> None:
        """Refresh all widgets from current monitor and config values"""
        if not self._monitor:
            return
        self._updating = True
        try:
            # Basic info
            self.name.set_value(self._monitor.get_name())
            self.desc.set_value(self._monitor.get_model()[:48])

            # Boolean properties
            self.dpms.set_value(self._monitor.get_is_dpms_enabled())
            self.sync.set_value(self._monitor.get_is_adaptive_sync_enabled())

            # Position, size, scale, refresh (handled by adjustment form)
            self._monitor_adjustment_form_view.refresh_all()

            # Transform and modes
            self._refresh_transform_and_modes()

            # Hyprland-specific properties
            if self.ten_bit:
                self.ten_bit.set_active(self._monitor.get_is_ten_bit_enabled())
            if self.mirror:
                self._populate_mirror_combo()
        finally:
            self._updating = False

    def _refresh_transform_and_modes(self) -> None:
        """Refresh transform and modes comboboxes"""
        self.transform.set_active_id(str(self._monitor.get_transform()))

        # Use the _updating flag instead of signal blocking
        self.modes.remove_all()
        active_id = ""
        for i, mode in enumerate(self._monitor.get_modes()):
            txt = f"{mode.get_width()}x{mode.get_height()}@{mode.get_refresh_rate()}Hz"
            self.modes.append(str(i), txt)
            if (
                mode.get_width() == self._monitor.get_width()
                and mode.get_height() == self._monitor.get_height()
                and mode.get_refresh_rate() == self._monitor.get_refresh_rate()
            ):
                active_id = str(i)
        if active_id:
            self.modes.set_active_id(active_id)

    def _populate_mirror_combo(self) -> None:
        """Populate the mirror combobox (Hyprland only)"""
        if not self.mirror:
            return
        self.mirror.handler_block_by_func(self._on_mirror)
        try:
            self.mirror.remove_all()
            self.mirror.append("", self._vocab.get("none", "None"))
            for btn in self._buttons:
                if btn.get_monitor() is not self._monitor:
                    name = btn.get_monitor().get_name()
                    self.mirror.append(name, name)
            current = self._monitor.get_is_mirror_of() or ""
            self.mirror.set_active_id(current)
        finally:
            self.mirror.handler_unblock_by_func(self._on_mirror)

    def get_selected_monitor(self) -> Optional[Monitor]:
        """Get the currently selected monitor"""
        return self._monitor

    def __del__(self):
        """Clean up signal handlers when the object is destroyed"""
        if self._monitor_handler and self._monitor:
            self._monitor.disconnect(self._monitor_handler)
