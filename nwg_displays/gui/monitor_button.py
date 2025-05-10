from gi.repository import Gtk
from nwg_displays.monitor.monitor import Monitor
from nwg_displays.monitor.monitor_transform_mode import MonitorTransformMode
from nwg_displays.configuration_service import ConfigurationService


class MonitorButton(Gtk.Button):
    def __init__(
        self,
        monitor: Monitor,
    ):
        super().__init__()
        self._monitor = monitor
        self.__config = ConfigurationService().load_config()
        self._is_selected = False

    def get_x(self):
        return self._monitor.get_x()

    def set_x(self, value):
        self._monitor.config.x = value

    def get_logical_width(self):
        if self._monitor.get_transform() in [
            MonitorTransformMode.ROTATE_90,
            MonitorTransformMode.ROTATE_270,
        ]:
            return self._monitor.get_height() / self._monitor.get_scale()
        return self._monitor.get_width() / self._monitor.get_scale()

    def get_logical_height(self):
        if self._monitor.get_transform() in [
            MonitorTransformMode.ROTATE_90,
            MonitorTransformMode.ROTATE_270,
        ]:
            return self._monitor.get_width() / self._monitor.get_scale()
        return self._monitor.get_height() / self._monitor.get_scale()

    def select(self):
        self.selected = True
        self.set_property("name", "selected-output")
        global selected_output_button
        selected_output_button = self

    def unselect(self):
        self.set_property("name", "output")

    def rescale_transform(self):
        self.set_size_request(
            round(self.get_logical_width() * self.__config["view-scale"]),
            round(self.get_logical_height() * self.__config["view-scale"]),
        )

    def on_active_check_button_toggled(self, button):
        self.active = button.get_active()
        if not self.active:
            self.set_property("name", "inactive-output")
        else:
            if self == selected_output_button:
                self.set_property("name", "selected-output")
            else:
                self.set_property("name", "output")

    def get_monitor(self) -> Monitor:
        return self._monitor
