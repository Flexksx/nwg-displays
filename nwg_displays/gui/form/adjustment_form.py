from typing import Callable, Optional, Tuple
from gi.repository import Gtk
from nwg_displays.gui.form.base_form import BaseForm


class AdjustmentForm(BaseForm):
    def __init__(
        self,
        builder: Gtk.Builder = None,
        on_event_callback: Optional[Tuple[str, Callable]] = None,
        tooltip: Optional[str] = None,
        glade_name: str = None,
        lower_bound: int | float = None,
        upper_bound: int | float = None,
        step_increment: int | float = None,
        page_increment: int | float = None,
        page_size: int = None,
        climb_rate: int | float = None,
        digits: int = 2,
        initial_value: Optional[int | float] = None,
    ):
        stored_callback = on_event_callback

        super().__init__(
            builder=builder,
            glade_name=glade_name,
            on_event_callback=None,
            tooltip=tooltip,
        )

        if initial_value is None:
            initial_value = lower_bound

        self.get_form().set_digits(digits)

        adjustment = Gtk.Adjustment(
            value=initial_value,
            lower=lower_bound,
            upper=upper_bound,
            step_increment=step_increment,
            page_increment=page_increment,
            page_size=page_size,
        )

        self.get_form().configure(
            adjustment,
            climb_rate,
            digits,
        )

        if stored_callback:
            event_name, callback_func = stored_callback
            self.get_form().connect(event_name, callback_func)

    def get_value(self) -> int | float:
        return self.get_form().get_value()

    def set_value(self, value: int | float):
        self.get_form().set_value(value)
