from abc import ABC, abstractmethod

from nwg_displays.monitor.monitor_base_configuration import MonitorConfiguration


class MonitorService(ABC):
    @abstractmethod
    def list(self) -> list[MonitorConfiguration]:
        pass
