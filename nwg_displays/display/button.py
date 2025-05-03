import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from nwg_displays.ui.indicator import Indicator

# Event mask for button events
EvMask = Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK


class DisplayButton(Gtk.Button):
    def __init__(
        self,
        name,
        description,
        x,
        y,
        physical_width,
        physical_height,
        transform,
        scale,
        scale_filter,
        refresh,
        modes,
        active,
        dpms,
        adaptive_sync_status,
        ten_bit,
        custom_mode_status,
        focused,
        monitor,
        mirror="",
        on_button_press=None,
        on_motion_notify=None,
    ):
        super().__init__()
        # Output properties
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.physical_width = physical_width
        self.physical_height = physical_height
        self.transform = transform
        self.scale = scale
        self.scale_filter = scale_filter
        self.refresh = refresh
        self.modes = []
        for m in modes:
            if m not in self.modes:
                self.modes.append(m)
        self.active = active
        self.dpms = dpms
        self.adaptive_sync = (
            adaptive_sync_status == "enabled"
        )  # converts "enabled | disabled" to bool
        self.custom_mode = custom_mode_status
        self.focused = focused
        self.mirror = mirror
        self.ten_bit = ten_bit

        # Event handlers
        self.on_button_press = on_button_press
        self.on_motion_notify = on_motion_notify

        # Button properties
        self.selected = False
        self.set_can_focus(False)
        self.set_events(EvMask)

        if self.on_button_press:
            self.connect("button_press_event", self.on_button_press)

        if self.on_motion_notify:
            self.connect("motion_notify_event", self.on_motion_notify)

        self.set_always_show_image(True)
        self.set_label(self.name)

        self.rescale_transform()
        self.set_property("name", "output")

        self.indicator = Indicator(
            monitor,
            name,
            round(self.physical_width * self._get_view_scale()),
            round(self.physical_height * self._get_view_scale()),
            self._get_indicator_timeout(),
        )

        self.show()

    def _get_view_scale(self):
        # This should be implemented to access the config
        # Can't access global config directly in this refactored version
        # Will be provided via dependency injection or context
        return 0.2  # Default value, should be replaced with actual config

    def _get_indicator_timeout(self):
        # Similar to above, access config via proper channels
        return 1000  # Default value

    @property
    def logical_width(self):
        if self._is_rotated(self.transform):
            return self.physical_height / self.scale
        else:
            return self.physical_width / self.scale

    @property
    def logical_height(self):
        if self._is_rotated(self.transform):
            return self.physical_width / self.scale
        else:
            return self.physical_height / self.scale

    def _is_rotated(self, transform):
        return transform in ["90", "270", "flipped-90", "flipped-270"]

    def select(self):
        self.selected = True
        self.set_property("name", "selected-output")

    def unselect(self):
        self.set_property("name", "output")

    def rescale_transform(self, view_scale=None):
        if view_scale is None:
            view_scale = self._get_view_scale()

        self.set_size_request(
            round(self.logical_width * view_scale),
            round(self.logical_height * view_scale),
        )

    def on_active_check_button_toggled(self, w):
        self.active = w.get_active()
        if not self.active:
            self.set_property("name", "inactive-output")
        else:
            if self.selected:
                self.set_property("name", "selected-output")
            else:
                self.set_property("name", "output")
