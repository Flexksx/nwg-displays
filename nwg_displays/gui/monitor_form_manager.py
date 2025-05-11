from typing import Dict, Any, Optional, Callable
import logging

from gi.repository import Gtk, Gdk
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode
from nwg_displays.gui.draggable_monitor_button import DraggableMonitorButton


class MonitorFormManager:
    """
    Manages the form for editing display settings.

    This class encapsulates all form-related logic, handling the initialization,
    updates, and event callbacks for the display settings form.
    """

    def __init__(
        self,
        builder: Gtk.Builder,
        config: Dict[str, Any],
        vocabulary: Dict[str, str],
        config_dir: str,
        is_sway_session: bool,
    ):
        """
        Initialize the form manager.

        Args:
            builder: Gtk builder with form widgets
            config: Configuration dictionary
            vocabulary: Vocabulary dictionary for translations
            config_dir: Path to the configuration directory
            is_sway_session: True if running in Sway, False for Hyprland
        """
        self.builder = builder
        self.config = config
        self.vocabulary = vocabulary
        self.config_dir = config_dir
        self.is_sway_session = is_sway_session

        # The currently selected monitor button
        self.selected_button = None

        # Flag to prevent mode changed event from triggering when rebuilding the combo box
        self.on_mode_changed_silent = False

        # Initialize form widgets
        self._init_form_fields()
        self._setup_form_widgets()

    def _init_form_fields(self):
        """Initialize form field references"""
        self.form_name = self.builder.get_object("name")
        self.form_description = self.builder.get_object("description")
        self.form_dpms = self.builder.get_object("dpms")
        self.form_adaptive_sync = self.builder.get_object("adaptive-sync")
        self.form_custom_mode = self.builder.get_object("custom-mode")
        self.form_view_scale = self.builder.get_object("view-scale")
        self.form_use_desc = self.builder.get_object("use-desc")
        self.form_x = self.builder.get_object("x")
        self.form_y = self.builder.get_object("y")
        self.form_width = self.builder.get_object("width")
        self.form_height = self.builder.get_object("height")
        self.form_scale = self.builder.get_object("scale")
        self.form_scale_filter = self.builder.get_object("scale-filter")
        self.form_refresh = self.builder.get_object("refresh")
        self.form_modes = self.builder.get_object("modes")
        self.form_transform = self.builder.get_object("transform")
        self.form_wrapper_box = self.builder.get_object("wrapper-box")
        self.form_workspaces = self.builder.get_object("workspaces")
        self.form_close = self.builder.get_object("close")
        self.form_apply = self.builder.get_object("apply")
        self.form_version = self.builder.get_object("version")
        self.form_mirror = (
            self.builder.get_object("mirror")
            if self.builder.get_object("mirror")
            else None
        )
        self.form_ten_bit = (
            self.builder.get_object("ten-bit")
            if self.builder.get_object("ten-bit")
            else None
        )

    def _setup_form_widgets(self):
        """Set up form widgets with labels, tooltips, and event handlers"""
        # Set up labels
        self.builder.get_object("lbl-modes").set_label(
            "{}:".format(self.vocabulary.get("modes", "Modes"))
        )
        self.builder.get_object("lbl-position-x").set_label(
            "{}:".format(self.vocabulary.get("position-x", "Position X"))
        )
        self.builder.get_object("lbl-refresh").set_label(
            "{}:".format(self.vocabulary.get("refresh", "Refresh"))
        )
        self.builder.get_object("lbl-scale").set_label(
            "{}:".format(self.vocabulary.get("scale", "Scale"))
        )
        self.builder.get_object("lbl-scale-filter").set_label(
            "{}:".format(self.vocabulary.get("scale-filter", "Scale Filter"))
        )
        self.builder.get_object("lbl-size").set_label(
            "{}:".format(self.vocabulary.get("size", "Size"))
        )
        self.builder.get_object("lbl-transform").set_label(
            "{}:".format(self.vocabulary.get("transform", "Transform"))
        )
        self.builder.get_object("lbl-zoom").set_label(
            "{}:".format(self.vocabulary.get("zoom", "Zoom"))
        )

        # Set up tooltips and event handlers
        self.form_dpms.set_tooltip_text(
            self.vocabulary.get("dpms-tooltip", "DPMS Configuration")
        )
        self.form_dpms.connect("toggled", self.on_dpms_toggled)

        if self.is_sway_session:
            self.form_adaptive_sync.set_label(
                self.vocabulary.get("adaptive-sync", "Adaptive sync")
            )
            self.form_adaptive_sync.set_tooltip_text(
                self.vocabulary.get(
                    "adaptive-sync-tooltip",
                    "Enables or disables adaptive synchronization \n(often referred to as Variable Refresh Rate, \nor by the vendor-specific names FreeSync/G-Sync).",
                )
            )
            self.form_adaptive_sync.connect("toggled", self.on_adaptive_sync_toggled)
        else:
            self.form_adaptive_sync.set_sensitive(False)

        if self.is_sway_session:
            self.form_custom_mode.set_label(
                self.vocabulary.get("custom-mode", "Custom mode")
            )
            self.form_custom_mode.set_tooltip_text(
                self.vocabulary.get(
                    "custom-mode-tooltip",
                    "Adds '--custom' argument to set a mode \nnot listed in the list of available modes.\nUse this ONLY if you know what you're doing.",
                )
            )
            self.form_custom_mode.connect("toggled", self.on_custom_mode_toggle)
        else:
            self.form_custom_mode.set_sensitive(False)

        self.form_view_scale.set_tooltip_text(
            self.vocabulary.get("view-scale-tooltip", "Scale view")
        )
        adj = Gtk.Adjustment(
            lower=0.1, upper=0.6, step_increment=0.05, page_increment=0.1, page_size=0.1
        )
        self.form_view_scale.configure(adj, 1, 2)
        self.form_view_scale.connect("changed", self.on_view_scale_changed)

        adj = Gtk.Adjustment(
            lower=0, upper=60000, step_increment=1, page_increment=10, page_size=1
        )
        self.form_x.configure(adj, 1, 0)
        self.form_x.connect("value-changed", self.on_pos_x_changed)

        adj = Gtk.Adjustment(
            lower=0, upper=40000, step_increment=1, page_increment=10, page_size=1
        )
        self.form_y.configure(adj, 1, 0)
        self.form_y.connect("value-changed", self.on_pos_y_changed)

        adj = Gtk.Adjustment(
            lower=0, upper=7680, step_increment=1, page_increment=10, page_size=1
        )
        self.form_width.configure(adj, 1, 0)
        self.form_width.connect("value-changed", self.on_width_changed)

        adj = Gtk.Adjustment(
            lower=0, upper=4320, step_increment=1, page_increment=10, page_size=1
        )
        self.form_height.configure(adj, 1, 0)
        self.form_height.connect("value-changed", self.on_height_changed)

        adj = Gtk.Adjustment(
            lower=0.1, upper=10, step_increment=0.1, page_increment=10, page_size=1
        )
        self.form_scale.configure(adj, 0.1, 6)
        self.form_scale.connect("value-changed", self.on_scale_changed)

        if self.is_sway_session:
            self.form_scale_filter.set_tooltip_text(
                self.vocabulary.get("scale-filter-tooltip", "Scale filter method")
            )
            self.form_scale_filter.connect("changed", self.on_scale_filter_changed)
        else:
            self.form_scale_filter.set_sensitive(False)

        adj = Gtk.Adjustment(
            lower=1, upper=1200, step_increment=1, page_increment=10, page_size=1
        )
        self.form_refresh.configure(adj, 1, 3)
        self.form_refresh.connect("changed", self.on_refresh_changed)

        self.form_modes.set_tooltip_text(
            self.vocabulary.get("modes-tooltip", "Available display modes")
        )
        self.form_modes.connect("changed", self.on_mode_changed)

        self.form_use_desc.set_label(
            "{}".format(self.vocabulary.get("use-desc", "Use Descriptions"))
        )
        self.form_use_desc.set_tooltip_text(
            "{}".format(
                self.vocabulary.get(
                    "use-desc-tooltip", "Use display descriptions instead of names"
                )
            )
        )
        self.form_use_desc.connect("toggled", self.on_use_desc_toggled)

        self.form_transform.set_tooltip_text(
            self.vocabulary.get(
                "transform-tooltip",
                "Transformations are used to rotate, flip or mirror the display.",
            )
        )
        self.form_transform.connect("changed", self.on_transform_changed)

        self.form_workspaces.set_label(
            "{}:".format(self.vocabulary.get("workspaces", "Workspaces"))
        )
        self.form_workspaces.set_tooltip_text(
            "{}".format(
                self.vocabulary.get("workspaces-tooltip", "Workspaces assignment")
            )
        )

        self.form_close.set_label(self.vocabulary.get("close", "Close"))
        self.form_apply.set_label(self.vocabulary.get("apply", "Apply"))

        if self.form_ten_bit:
            self.form_ten_bit.connect("toggled", self.on_ten_bit_toggled)

        if self.form_mirror:
            self.form_mirror.connect("changed", self.on_mirror_selected)

    def update_form_from_monitor(self, monitor_button: DraggableMonitorButton) -> None:
        """
        Update form values to reflect the selected monitor button.

        Args:
            monitor_button: The monitor button to display in the form
        """
        self.selected_button = monitor_button
        monitor = monitor_button.get_monitor()

        # Update form fields with monitor properties
        self.form_name.set_text(monitor.get_name())
        description = monitor.get_model()
        if len(description) > 48:
            self.form_description.set_text(f"{description[:47]}(…)")
        else:
            self.form_description.set_text(description)

        self.form_dpms.set_active(monitor.get_is_dpms_enabled())
        self.form_adaptive_sync.set_active(monitor.get_is_adaptive_sync_enabled())
        self.form_custom_mode.set_active(
            False
        )  # Placeholder, implement custom mode tracking
        self.form_view_scale.set_value(self.config.get("view-scale", 0.15))
        self.form_use_desc.set_active(self.config.get("use-desc", False))
        self.form_x.set_value(monitor.get_x())
        self.form_y.set_value(monitor.get_y())
        self.form_width.set_value(monitor.get_width())
        self.form_height.set_value(monitor.get_height())
        self.form_scale.set_value(monitor.get_scale())
        # Scale filter implementation depends on your monitor class
        self.form_refresh.set_value(monitor.get_refresh_rate())

        # Set up ten-bit and mirror options if available
        if self.form_ten_bit:
            self.form_ten_bit.set_active(monitor.get_is_ten_bit_enabled())

        if self.form_mirror:
            self._update_mirror_options(monitor)

        # Update modes combo
        self._update_modes_combo(monitor)

        # Set transform
        self.form_transform.set_active_id(str(monitor.get_transform()))

    def _update_mirror_options(self, monitor: Monitor) -> None:
        """Update mirror options in the form"""
        self.form_mirror.remove_all()
        self.form_mirror.append("", self.vocabulary.get("none", "None"))

        # Implement this method based on your application's logic for mirror options
        # Example:
        # for other_monitor in available_monitors:
        #     if other_monitor.get_name() != monitor.get_name():
        #         self.form_mirror.append(other_monitor.get_name(), other_monitor.get_name())

        # Set active mirror option
        self.form_mirror.set_active_id(str(monitor.get_is_mirror()))
        self.form_mirror.show_all()

    def _update_modes_combo(self, monitor: Monitor) -> None:
        """Update the modes combo box with available modes for the monitor"""
        # Prevent mode changed event while rebuilding
        self.on_mode_changed_silent = True

        self.form_modes.remove_all()
        active_mode = ""

        for mode in monitor.get_modes():
            mode_text = "{}x{}@{}Hz".format(
                mode.get_width(), mode.get_height(), mode.get_refresh_rate()
            )
            self.form_modes.append(mode_text, mode_text)

            # Set the active mode
            if (
                mode.get_width() == monitor.get_width()
                and mode.get_height() == monitor.get_height()
                and mode.get_refresh_rate() == monitor.get_refresh_rate()
            ):
                active_mode = mode_text

        if active_mode:
            self.form_modes.set_active_id(active_mode)

        self.on_mode_changed_silent = False

    # Event handlers for form widgets

    def on_view_scale_changed(self, widget: Gtk.Widget) -> None:
        """Handle view scale change"""
        self.config["view-scale"] = round(self.form_view_scale.get_value(), 2)
        # Rest of implementation depends on external state and functions

    def on_transform_changed(self, widget: Gtk.Widget) -> None:
        """Handle transform change"""
        if self.selected_button:
            transform = self.form_transform.get_active_id()
            # Implementation depends on your monitor button class

    def on_ten_bit_toggled(self, widget: Gtk.Widget) -> None:
        """Handle 10-bit mode toggle"""
        if self.selected_button:
            is_enabled = widget.get_active()
            self.selected_button.get_monitor().set_is_ten_bit_enabled(is_enabled)

    def on_dpms_toggled(self, widget: Gtk.Widget) -> None:
        """Handle DPMS toggle"""
        if self.selected_button:
            is_enabled = widget.get_active()
            self.selected_button.get_monitor().set_is_dpms_enabled(is_enabled)

    def on_use_desc_toggled(self, widget: Gtk.Widget) -> None:
        """Handle use description toggle"""
        self.config["use-desc"] = widget.get_active()
        # Save configuration

    def on_adaptive_sync_toggled(self, widget: Gtk.Widget) -> None:
        """Handle adaptive sync toggle"""
        if self.selected_button:
            is_enabled = widget.get_active()
            self.selected_button.get_monitor().set_is_adaptive_sync_enabled(is_enabled)

    def on_custom_mode_toggle(self, widget: Gtk.Widget) -> None:
        """Handle custom mode toggle"""
        if self.selected_button:
            # Implementation depends on your application's custom mode handling
            pass

    def on_pos_x_changed(self, widget: Gtk.Widget) -> None:
        """Handle X position change"""
        if self.selected_button:
            value = round(widget.get_value())
            self.selected_button.set_x(value)
            # Update visual position

    def on_pos_y_changed(self, widget: Gtk.Widget) -> None:
        """Handle Y position change"""
        if self.selected_button:
            value = round(widget.get_value())
            self.selected_button.set_y(value)
            # Update visual position

    def on_width_changed(self, widget: Gtk.Widget) -> None:
        """Handle width change"""
        if self.selected_button:
            value = round(widget.get_value())
            self.selected_button.get_monitor().set_width(value)
            self.selected_button.rescale_transform()

    def on_height_changed(self, widget: Gtk.Widget) -> None:
        """Handle height change"""
        if self.selected_button:
            value = round(widget.get_value())
            self.selected_button.get_monitor().set_height(value)
            self.selected_button.rescale_transform()

    def on_scale_changed(self, widget: Gtk.Widget) -> None:
        """Handle scale change"""
        if self.selected_button:
            value = widget.get_value()
            self.selected_button.get_monitor().set_scale(value)
            self.selected_button.rescale_transform()

    def on_scale_filter_changed(self, widget: Gtk.Widget) -> None:
        """Handle scale filter change"""
        if self.selected_button:
            value = widget.get_active_id()
            # Implementation depends on monitor scale filter support

    def on_refresh_changed(self, widget: Gtk.Widget) -> None:
        """Handle refresh rate change"""
        if self.selected_button:
            value = widget.get_value()
            self.selected_button.get_monitor().set_refresh_rate(value)
            self.update_form_from_monitor(self.selected_button)

    def on_mode_changed(self, widget: Gtk.Widget) -> None:
        """Handle mode selection change"""
        if self.selected_button and not self.on_mode_changed_silent:
            active_index = widget.get_active()
            if active_index >= 0:
                mode = self.selected_button.get_monitor().get_modes()[active_index]
                self.selected_button.get_monitor().set_width(mode.get_width())
                self.selected_button.get_monitor().set_height(mode.get_height())
                self.selected_button.get_monitor().set_refresh_rate(
                    mode.get_refresh_rate()
                )
                self.selected_button.rescale_transform()
                self.update_form_from_monitor(self.selected_button)

    def on_mirror_selected(self, widget: Gtk.Widget) -> None:
        """Handle mirror selection change"""
        if self.selected_button and widget.get_active_id() is not None:
            mirror_target = widget.get_active_id()
            # Implementation depends on your monitor mirror support

    def set_selected_button(self, button: DraggableMonitorButton) -> None:
        """Set the currently selected button"""
        self.selected_button = button
        self.update_form_from_monitor(button)
