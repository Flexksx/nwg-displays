from __future__ import annotations

"""GTK drag-and-drop helper used by nwg-displays widgets.

This module exposes **Draggable**, a small utility class you attach to any
`Gtk.Widget` that lives inside a `Gtk.Fixed` canvas.

Example
-------
```
from nwg_displays.gui.drag import Draggable

btn = DisplayButton(...)
fixed.put(btn, x, y)
Draggable(
    widget=btn,
    canvas=fixed,
    scale_fn=lambda: config["view-scale"],
    snap_fn=lambda: snap_threshold_scaled,
    siblings_fn=lambda: display_buttons,
    after_move_cb=update_form_from_widget,
)
```

The class keeps **all runtime state internally** (no globals) and cleans up
its signal handlers in `detach()`.
"""

from typing import Callable, Sequence, Tuple

from gi.repository import Gtk, Gdk

__all__ = ["Draggable"]

# Mask for the events we care about – left‑button press + motion
_EV_MASK = Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK


def _nearest_multiple(value: int, step: int) -> int:
    """Round *value* to the nearest multiple of *step* (ties → up)."""
    rem = value % step
    return value - rem if rem < step / 2 else value + (step - rem)


class _State:
    """Private mutable state kept between motion events."""

    offset: Tuple[int, int]  # pointer→widget anchor vector
    max_xy: Tuple[int, int]  # max coords inside the canvas
    prev_xy: Tuple[int, int]  # last position recorded

    def __init__(self) -> None:
        self.offset = (0, 0)
        self.max_xy = (0, 0)
        self.prev_xy = (-1, -1)


class Draggable:
    """
    Attach drag behaviour to *widget*.
    This class is used to make a widget draggable within a `Gtk.Fixed` canvas.
    It handles the drag-and-drop functionality, including snapping to
    nearby widgets and maintaining the widget's position within the canvas.

    """

    def __init__(
        self,
        *,
        widget: Gtk.Widget,
        canvas: Gtk.Fixed,
        scale_fn: Callable[[], float],
        snap_fn: Callable[[], int],
        siblings_fn: Callable[[], Sequence[Gtk.Widget]],
        after_move_cb: Callable[[Gtk.Widget], None] | None = None,
    ) -> None:
        self._w = widget
        self._canvas = canvas
        self._scale = scale_fn
        self._snap = snap_fn
        self._siblings = siblings_fn
        self._after_move = after_move_cb
        self._state = _State()

        # attach signals
        widget.add_events(_EV_MASK)
        self._handlers = (
            widget.connect("button_press_event", self._on_press),
            widget.connect("motion_notify_event", self._on_motion),
        )

    def detach(self) -> None:
        """Disconnect signal handlers – call before destroying *widget*."""
        for hid in self._handlers:
            self._w.disconnect(hid)

    def _on_press(self, _w: Gtk.Widget, ev: Gdk.EventButton) -> None:
        if ev.button != 1:
            return  # only left‑click starts drag

        # 1. store offset from cursor to widget origin
        parent_win = self._w.get_parent().get_window()
        px, py = parent_win.get_position()
        self._state.offset = (px + int(ev.x), py + int(ev.y))

        # 2. calc movement bounds
        alloc = self._canvas.get_allocation()
        w_alloc = self._w.get_allocation()
        self._state.max_xy = (
            alloc.width - w_alloc.width,
            alloc.height - w_alloc.height,
        )

    def _on_motion(self, _w: Gtk.Widget, ev: Gdk.EventMotion) -> None:
        st = self._state

        # translate to canvas coords and round to sensitivity grid (1 px)
        x = int(ev.x_root - st.offset[0])
        y = int(ev.y_root - st.offset[1])
        x = _nearest_multiple(max(0, min(x, st.max_xy[0])), 1)
        y = _nearest_multiple(max(0, min(y, st.max_xy[1])), 1)

        if (x, y) == st.prev_xy:
            return  # no change
        st.prev_xy = (x, y)

        scale = self._scale()
        snap_threshold = self._snap()

        snap_x = {0}
        snap_y = {0}
        for sib in self._siblings():
            if sib is self._w:
                continue
            sx, sy = sib.x * scale, sib.y * scale
            snap_x.update({sx, sx + sib.logical_width * scale})
            snap_y.update({sy, sy + sib.logical_height * scale})

        def maybe_snap(coord: int, choices: set[int]) -> int:
            for c in choices:
                if abs(coord - c) < snap_threshold:
                    return c
            return coord

        x = maybe_snap(x, snap_x)
        y = maybe_snap(y, snap_y)

        self._canvas.move(self._w, x, y)
        self._w.x = round(x / scale)
        self._w.y = round(y / scale)

        if self._after_move:
            self._after_move(self._w)
