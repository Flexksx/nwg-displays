import os
from typing import Callable, Dict, List, Optional, Any

from gi.repository import Gtk

from nwg_displays.gui.draggable_monitor_button import DraggableMonitorButton
from nwg_displays.gui.form.adjustment_form import AdjustmentForm
from nwg_displays.gui.form.boolean_form import BooleanForm
from nwg_displays.gui.form.text_form import TextForm
from nwg_displays.logger import logger
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_mode import MonitorMode
from nwg_displays.session.session_service import SessionService

session_service = SessionService()
DEFAULT_VIEW_SCALE = 0.15


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
        config: Dict[str, Any],
        vocabulary: Dict[str, str],
        fixed_container: Gtk.Fixed,
        on_monitor_changed_callback: Optional[Callable[[Monitor], None]] = None,
    ):
        self._builder = builder
        self._buttons = monitor_buttons
        self._config = config
        self._vocab = vocabulary
        self._fixed = fixed_container
        self._notify_parent = on_monitor_changed_callback

        self._monitor: Optional[Monitor] = None
        self._monitor_handler: Optional[int] = None
        self._updating = False

        self._setup_widgets()

        if monitor_buttons:
            self.set_selected_monitor(monitor_buttons[0].get_monitor())

    def _setup_widgets(self) -> None:
        v, b = self._vocab, self._builder

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
        self.dpms = BooleanForm(
            builder=b,
            glade_name="dpms",
            on_event_callback=("toggled", self._bool("dpms")),
            tooltip=v.get("dpms-tooltip", "DPMS (turn display off when idle)"),
        )
        self.sync = BooleanForm(
            builder=b,
            glade_name="adaptive-sync",
            on_event_callback=("toggled", self._bool("adaptive")),
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
        self.use_desc = BooleanForm(
            builder=b,
            glade_name="use-desc",
            on_event_callback=("toggled", self._on_use_desc),
            tooltip=v.get(
                "use-desc-tooltip",
                "Show EDID description instead of connector name.",
            ),
        )

        self.x = self._adj("x", 0, 60000, self._num("x"), digits=0)
        self.y = self._adj("y", 0, 40000, self._num("y"), digits=0)
        self.w = self._adj("width", 0, 7680, self._num("width"), digits=0)
        self.h = self._adj("height", 0, 4320, self._num("height"), digits=0)
        self.scale = self._adj("scale", 0.1, 10.0, self._float("scale"), digits=2)
        self.refresh = self._adj("refresh", 1, 1200, self._float("refresh"), digits=2)
        self.view_scale = self._adj(
            "view-scale", 0.1, 0.6, self._on_view_scale, step=0.05, digits=2
        )
        init_view_scale = self._config.get("view-scale", DEFAULT_VIEW_SCALE)
        if init_view_scale == 0:
            init_view_scale = DEFAULT_VIEW_SCALE
        self.view_scale.set_value(init_view_scale)
        logger.debug(
            f"MonitorConfigurationFormView: view_scale={self.view_scale.get_value()}"
        )

        self.scale_filter: Gtk.ComboBox = b.get_object("scale-filter")
        self.scale_filter.connect("changed", self._on_scale_filter)

        self.transform: Gtk.ComboBox = b.get_object("transform")
        self.transform.connect("changed", self._on_transform)

        self.modes: Gtk.ComboBox = b.get_object("modes")
        self.modes.connect("changed", self._on_mode)

        self.ten_bit: Optional[Gtk.CheckButton] = None
        self.mirror: Optional[Gtk.ComboBox] = None
        if session_service.is_hyprland_session():
            grid: Gtk.Grid = b.get_object("grid")

            self.ten_bit = Gtk.CheckButton.new_with_label(
                v.get("10-bit-support", "10 bit colour"),
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

    def _adj(
        self,
        name: str,
        low: int | float,
        up: int | float,
        on_change_cb,
        *,
        step: int | float = 1,
        page: int | float = 10,
        digits: int = 2,
    ):
        return AdjustmentForm(
            builder=self._builder,
            glade_name=name,
            on_event_callback=("value-changed", on_change_cb),
            lower_bound=low,
            upper_bound=up,
            step_increment=step,
            page_increment=page,
            page_size=1,
            climb_rate=step,
            digits=digits,
        )

    def set_selected_monitor(self, m: Monitor) -> None:
        if self._monitor_handler:
            self._monitor.disconnect(self._monitor_handler)

        self._monitor = m
        self._monitor_handler = m.connect("property-changed", self._on_model_change)
        self._refresh_all()

    def _on_model_change(self, _m: Monitor, field: str, _value) -> None:
        if self._updating:
            return
        self._updating = True
        try:
            if field == "x":
                self.x.set_value(self._monitor.get_x())
            elif field == "y":
                self.y.set_value(self._monitor.get_y())
            elif field == "width":
                self.w.set_value(self._monitor.get_width())
            elif field == "height":
                self.h.set_value(self._monitor.get_height())
            elif field == "scale":
                self.scale.set_value(self._monitor.get_scale())
            elif field == "refresh_rate":
                self.refresh.set_value(self._monitor.get_refresh_rate())
            elif field == "dpms":
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

    def _num(self, field: str):
        def cb(adj: Gtk.Adjustment):
            if self._monitor is None or self._updating:
                return
            getattr(self._monitor, f"set_{field}")(int(round(adj.get_value())))
            self._notify_parent()

        return cb

    def _float(self, field: str):
        def cb(adj: Gtk.Adjustment):
            if self._monitor is None or self._updating:
                return
            getattr(self._monitor, f"set_{field}")(adj.get_value())
            self._notify_parent()

        return cb

    def _bool(self, which: str):
        def cb(btn: Gtk.ToggleButton):
            if self._monitor is None or self._updating:
                return
            if which == "dpms":
                self._monitor.set_is_dpms_enabled(btn.get_active())
            else:
                self._monitor.set_is_adaptive_sync_enabled(btn.get_active())
            self._notify_parent()

        return cb

    def _on_custom_toggled(self, btn: Gtk.ToggleButton):
        modes = set(self._config.get("custom-mode", []))
        if btn.get_active():
            modes.add(self._monitor.get_name())
        else:
            modes.discard(self._monitor.get_name())
        self._config["custom-mode"] = tuple(modes)
        self._notify_parent()

    def _on_use_desc(self, btn: Gtk.ToggleButton):
        self._config["use-desc"] = btn.get_active()

    def _on_view_scale(self, adj: Gtk.Adjustment):
        self._config["view-scale"] = round(adj.get_value(), 2)
        for b in self._buttons:
            b.rescale_transform()
            self._fixed.move(
                b,
                b.get_monitor().get_x() * self._config["view-scale"],
                b.get_monitor().get_y() * self._config["view-scale"],
            )

    def _on_transform(self, box: Gtk.ComboBox):
        if self._updating:
            return
        tid = box.get_active_id()
        if tid:
            self._monitor.set_transform(int(tid))
            self._notify_parent()

    def _on_scale_filter(self, box: Gtk.ComboBox):
        if self._updating:
            return
        sid = box.get_active_id()
        if sid and hasattr(self._monitor, "set_scale_filter"):
            self._monitor.set_scale_filter(sid)
            self._notify_parent()

    def _on_mode(self, box: Gtk.ComboBox):
        if self._updating:
            return
        idx = box.get_active()
        modes = self._monitor.get_modes()
        if 0 <= idx < len(modes):
            mode: MonitorMode = modes[idx]
            self._monitor.set_width(mode.get_width())
            self._monitor.set_height(mode.get_height())
            self._monitor.set_refresh_rate(mode.get_refresh_rate())
            self._notify_parent()

    def _on_ten_bit(self, btn: Gtk.ToggleButton):
        if self._updating:
            return
        self._monitor.set_is_ten_bit_enabled(btn.get_active())
        self._notify_parent()

    def _on_mirror(self, box: Gtk.ComboBox):
        if self._updating or not self.mirror:
            return
        self._monitor.set_mirror(box.get_active_id())
        self._notify_parent()

    def _refresh_all(self) -> None:
        if not self._monitor:
            return
        self._updating = True
        try:
            self.name.set_value(self._monitor.get_name())
            self.desc.set_value(self._monitor.get_model()[:48])
            self.x.set_value(self._monitor.get_x())
            self.y.set_value(self._monitor.get_y())
            self.w.set_value(self._monitor.get_width())
            self.h.set_value(self._monitor.get_height())
            self.scale.set_value(self._monitor.get_scale())
            self.refresh.set_value(self._monitor.get_refresh_rate())
            self.dpms.set_value(self._monitor.get_is_dpms_enabled())
            self.sync.set_value(self._monitor.get_is_adaptive_sync_enabled())
            self._refresh_transform_and_modes()

            if self.ten_bit:
                self.ten_bit.set_active(self._monitor.get_is_ten_bit_enabled())
            if self.mirror:
                self._populate_mirror_combo()
        finally:
            self._updating = False

    def _refresh_transform_and_modes(self) -> None:
        self.transform.set_active_id(str(self._monitor.get_transform()))

        self.modes.handler_block_by_func(self._on_mode)
        try:
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
        finally:
            self.modes.handler_unblock_by_func(self._on_mode)

    def _populate_mirror_combo(self) -> None:
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

    def _notify_parent(self):
        if self._notify_parent:
            self._notify_parent(self._monitor)

    def get_selected_monitor(self) -> Optional[Monitor]:
        return self._monitor
