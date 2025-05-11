from typing import Callable, Optional, Tuple
from gi.repository import Gtk
from nwg_displays.gui.form.base_form import BaseForm


class TextForm(BaseForm):
    def __init__(
        self,
        builder: Gtk.Builder = None,
        glade_name: str = None,
        on_event_callback: Optional[Tuple[str, Callable]] = None,
        tooltip: Optional[str] = None,
    ):
        super().__init__(
            builder=builder,
            glade_name=glade_name,
            on_event_callback=on_event_callback,
            tooltip=tooltip,
        )

    def get_value(self) -> str:
        return self.get_form().get_text()

    def set_value(self, value: str):
        self.get_form().set_text(value)
