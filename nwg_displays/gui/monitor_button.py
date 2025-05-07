from gi.repository import Gtk
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.gui.drag import Draggable  # ← the helper you just created


class MonitorButton(Gtk.Button):
    """
    A button that represents a monitor in the display manager.
    """

    def __init__(
        self,
        monitor: Monitor,
        *,
        canvas: Gtk.Fixed,
        scale_fn,
        snap_fn,
        siblings_fn,
        after_move_cb=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._monitor = monitor
        self.set_label(monitor.get_name())
        self.set_can_focus(False)

        self._draggable = Draggable(
            widget=self,
            canvas=canvas,
            scale_fn=scale_fn,
            snap_fn=snap_fn,
            siblings_fn=siblings_fn,
            after_move_cb=after_move_cb,
        )

    @property
    def x(self):
        return self._monitor.get_x()

    @x.setter
    def x(self, value):
        self._monitor.config.x = value
