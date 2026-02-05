from abc import ABC, abstractmethod
from nwg_displays.outputs.model import MonitorOutput


class BaseMonitorOutputRepository(ABC):
    def __init__(self):
        self.outputs = []

    @abstractmethod
    def get_by_name(self, name: str) -> MonitorOutput:
        return next((output for output in self.outputs if output.name == name), None)

    def get_all(self) -> list[MonitorOutput]:
        return self.outputs

    def add(self, output: MonitorOutput):
        self.outputs.append(output)

    def update(self, output: MonitorOutput):
        self.outputs.append(output)
