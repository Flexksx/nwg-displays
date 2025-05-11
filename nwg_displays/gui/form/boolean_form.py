from typing import Callable, Optional, Tuple
from gi.repository import Gtk
from nwg_displays.gui.form.base_form import BaseForm


class BooleanForm(BaseForm):
    def __init__(
        self,
        builder: Gtk.Builder,
        glade_name: str,
        on_event_callback: Optional[Tuple[str, Callable]] = None,
        tooltip: Optional[str] = None,
    ):
        super().__init__(
            builder=builder,
            glade_name=glade_name,
            on_event_callback=on_event_callback,
            tooltip=tooltip,
        )

    def get_value(self) -> bool:
        return self.get_form().get_active()

    def set_value(self, value: bool):
        self.get_form().set_active(value)
