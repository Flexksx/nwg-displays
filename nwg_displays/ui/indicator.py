import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, GLib, GtkLayerShell


class Indicator(Gtk.Window):
    def __init__(self, monitor, name, width, height, timeout):
        super().__init__()
        self.timeout = timeout
        self.monitor = monitor
        self.set_property("name", "indicator")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        if monitor:
            GtkLayerShell.set_monitor(self, monitor)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)
        label = Gtk.Label()
        box.set_property("name", "indicator-label")
        label.set_text(name)
        box.pack_start(label, True, True, 10)

        self.set_size_request(width, height)
        if self.timeout > 0:
            self.show_up(self.timeout * 2)

    def show_up(self, timeout=None):
        if self.timeout > 0 and self.monitor:
            self.show_all()
            if timeout:
                GLib.timeout_add(timeout, self.hide)
            else:
                GLib.timeout_add(self.timeout, self.hide)
