from abc import ABC, abstractmethod
from typing import List

from nwg_displays.monitor.monitor import Monitor


class MonitorService(ABC):
    @abstractmethod
    def list(self) -> List[Monitor]:
        """Get all monitors."""
        pass
