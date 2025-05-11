from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from gi.repository import Gdk, Gtk

from nwg_displays.configuration_service import ConfigurationService
from nwg_displays.gui.monitor_button_indicator import MonitorButtonIndicator
from nwg_displays.logger import logger
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode

BUTTON_MASK = Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK
DEFAULT_VIEW_SCALE = 0.15
DEFAULT_SNAP_PX = 10


def nearest_multiple(value: int, step: int) -> int:
    remainder = value % step
    return value - remainder if remainder < step / 2 else value + step - remainder


class DragState:
    def __init__(self) -> None:
        self.origin: Tuple[int, int] = (0, 0)
        self.bound: Tuple[int, int] = (0, 0)
        self.previous: Tuple[int, int] = (-1, -1)


class DraggableMonitorButton(Gtk.Button):
    """
    A Gtk.Button that mirrors the state of a Monitor instance
    and lets the user reposition that monitor by dragging.
    """

    def __init__(
        self,
        monitor: Monitor,
        canvas: Optional[Gtk.Fixed] = None,
        config: Optional[dict] = None,
        after_move: Optional[Callable[[Gtk.Widget], None]] = None,
    ) -> None:
        super().__init__()

        self.monitor = monitor
        self.canvas = canvas
        self.after_move = after_move
        self.cfg = config or ConfigurationService().load_config()

        self.drag = DragState()
        self._is_selected = False
        self._is_active = True

        self.add_events(BUTTON_MASK)
        self.connect("button_press_event", self._on_press)
        self.connect("motion_notify_event", self._on_motion)

        self.monitor.connect("property-changed", self._on_model_change)

        self.indicator = MonitorButtonIndicator(
            monitor.get_gdk_monitor(),
            monitor.get_name(),
            round(monitor.get_width() * self.scale_factor),
            round(monitor.get_height() * self.scale_factor),
            self.cfg.get("indicator-timeout", 0),
        )

        self._init_appearance()
        self.show()

    def _init_appearance(self) -> None:
        self.set_label(self.monitor.get_name())
        self.set_always_show_image(True)
        self.set_property("name", "output")
        self.rescale_transform()

    def _on_press(self, _w: Gtk.Widget, event: Gdk.EventButton) -> None:
        if event.button != 1:
            return

        parent = self.get_parent().get_window()
        win_x, win_y = parent.get_position()
        self.drag.origin = (win_x + int(event.x), win_y + int(event.y))

        canvas_alloc = self.canvas.get_allocation()
        alloc = self.get_allocation()
        self.drag.bound = (
            canvas_alloc.width - alloc.width,
            canvas_alloc.height - alloc.height,
        )

        self._select_exclusively()
        self.indicator.show_up()
        if self.after_move:
            self.after_move(self)

    def _on_motion(self, _w: Gtk.Widget, event: Gdk.EventMotion) -> None:
        raw_x = int(event.x_root - self.drag.origin[0])
        raw_y = int(event.y_root - self.drag.origin[1])

        x = nearest_multiple(max(0, min(raw_x, self.drag.bound[0])), 1)
        y = nearest_multiple(max(0, min(raw_y, self.drag.bound[1])), 1)

        if (x, y) == self.drag.previous:
            return
        self.drag.previous = (x, y)

        x, y = self._apply_snapping(x, y)

        self._move_to(x, y)
        if self.after_move:
            self.after_move(self)

    def _apply_snapping(self, x: int, y: int) -> Tuple[int, int]:
        horiz, vert = self._collect_snap_sets()
        w = self.get_logical_width() * self.scale_factor
        h = self.get_logical_height() * self.scale_factor
        thr = self.snap_threshold

        def snap(val: int, pts: set[int], size: float) -> int:
            for p in pts:
                if abs(val - p) < thr:
                    return p
                if abs(val + size - p) < thr:
                    return p - int(size)
            return val

        return snap(x, horiz, w), snap(y, vert, h)

    def _collect_snap_sets(self) -> Tuple[set[int], set[int]]:
        sx, sy = {0}, {0}
        for btn in self._siblings():
            if btn is self:
                continue
            sx.update(
                {
                    btn.get_x() * self.scale_factor,
                    (btn.get_x() + btn.get_logical_width()) * self.scale_factor,
                }
            )
            sy.update(
                {
                    btn.get_y() * self.scale_factor,
                    (btn.get_y() + btn.get_logical_height()) * self.scale_factor,
                }
            )
        return sx, sy

    def _move_to(self, x_canvas: int, y_canvas: int) -> None:
        self.canvas.move(self, x_canvas, y_canvas)

        sf = self.scale_factor
        self.monitor.set_x(round(x_canvas / sf))
        self.monitor.set_y(round(y_canvas / sf))

    def _on_model_change(self, _monitor: Monitor, field: str, _value) -> None:
        if field in {"x", "y"}:
            self.canvas.move(
                self,
                round(self.monitor.get_x() * self.scale_factor),
                round(self.monitor.get_y() * self.scale_factor),
            )
        if field in {"width", "height", "scale", "transform"}:
            self.rescale_transform()

    def get_logical_width(self) -> float:
        t = self.monitor.get_transform()
        if t in (MonitorTransformMode.ROTATE_90, MonitorTransformMode.ROTATE_270):
            return self.monitor.get_height() / self.monitor.get_scale()
        return self.monitor.get_width() / self.monitor.get_scale()

    def get_logical_height(self) -> float:
        t = self.monitor.get_transform()
        if t in (MonitorTransformMode.ROTATE_90, MonitorTransformMode.ROTATE_270):
            return self.monitor.get_width() / self.monitor.get_scale()
        return self.monitor.get_height() / self.monitor.get_scale()

    def rescale_transform(self) -> None:
        self.set_size_request(
            round(self.get_logical_width() * self.scale_factor),
            round(self.get_logical_height() * self.scale_factor),
        )

    def _select_exclusively(self) -> None:
        for btn in self._siblings():
            btn.select() if btn is self else btn.unselect()

    def select(self) -> None:
        self._is_selected = True
        self.set_property("name", "selected-output")

    def unselect(self) -> None:
        self._is_selected = False
        self.set_property("name", "output")

    def on_active_check_button_toggled(self, src: Gtk.CheckButton) -> None:
        self._is_active = src.get_active()
        self._update_visual_state()

    def _update_visual_state(self) -> None:
        if not self._is_active:
            self.set_property("name", "inactive-output")
        else:
            self.set_property(
                "name", "selected-output" if self._is_selected else "output"
            )

    @property
    def scale_factor(self) -> float:
        v = self.cfg.get("view-scale", DEFAULT_VIEW_SCALE)
        return v if v else DEFAULT_VIEW_SCALE

    @property
    def snap_threshold(self) -> int:
        return round(
            self.cfg.get("snap-threshold", DEFAULT_SNAP_PX) * self.scale_factor
        )

    def _siblings(self) -> List["DraggableMonitorButton"]:
        return self.canvas.get_children() if self.canvas else []

    def get_monitor(self) -> Monitor:
        return self.monitor

    def get_x(self) -> int:
        return self.monitor.get_x()

    def get_y(self) -> int:
        return self.monitor.get_y()

    def detach(self) -> None:
        self.monitor.disconnect_by_func(self._on_model_change)
        for h in self._handlers:
            self.disconnect(h)
