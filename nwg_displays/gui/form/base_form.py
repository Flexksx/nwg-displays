from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple
from gi.repository import Gtk
from nwg_displays.gui.form.form import Form


class BaseForm(Form, ABC):
    def __init__(
        self,
        builder: Gtk.Builder = None,
        glade_name: str = None,
        on_event_callback: Optional[Tuple[str, Callable]] = None,
        tooltip: Optional[str] = None,
    ):
        self.__builder = builder
        self.__form = self.__builder.get_object(glade_name)
        if self.__form is None:
            raise ValueError(f"Widget '{glade_name}' not found in the builder.")
        if on_event_callback is not None:
            event_name, callback = on_event_callback
            self.__form.connect(event_name, callback)

        if tooltip is not None:
            self.__form.set_tooltip_text(tooltip)

    def get_form(self) -> Gtk.Widget:
        return self.__form

    def set_tooltip_text(self, tooltip: str):
        self.__form.set_tooltip_text(tooltip)

    def set_sensitive(self, sensitive: bool):
        self.__form.set_sensitive(sensitive)

    def set_visible(self, visible: bool):
        self.__form.set_visible(visible)

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def set_value(self, value):
        pass
