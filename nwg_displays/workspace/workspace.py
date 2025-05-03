from abc import ABC, abstractmethod


class Workspace(ABC):
    """
    Abstract base class for a workspace.
    """

    @abstractmethod
    def get_id(self) -> int:
        """
        Get the ID of the workspace.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the workspace.
        """
        pass

    @abstractmethod
    def get_monitor_name(self) -> str:
        """
        Get the monitor of the workspace.
        """
        pass

    @abstractmethod
    def get_monitor_id(self) -> int:
        """
        Get the ID of the monitor of the workspace.
        """
        pass
