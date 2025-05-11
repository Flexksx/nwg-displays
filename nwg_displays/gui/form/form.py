from abc import ABC, abstractmethod


class Form(ABC):
    @abstractmethod
    def set_value(self, value):
        """Set the value of the form."""
        pass

    @abstractmethod
    def get_value(self):
        """Get the value of the form."""
        pass

    @abstractmethod
    def set_tooltip_text(self, tooltip: str):
        """Set the tooltip of the form."""
        pass

    @abstractmethod
    def set_sensitive(self, sensitive: bool):
        """Set the sensitivity of the form."""
        pass

    @abstractmethod
    def set_visible(self, visible: bool):
        """Set the visibility of the form."""
        pass

    @abstractmethod
    def get_form(self):
        """Get the form widget."""
        pass
