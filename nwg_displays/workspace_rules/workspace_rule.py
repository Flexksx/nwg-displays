from abc import ABC, abstractmethod


class WorkspaceRule(ABC):
    @abstractmethod
    def get_workspace_id(self) -> str:
        """Get the workspace ID."""
        pass

    @abstractmethod
    def get_monitor_name(self) -> str:
        """Get the monitor name."""
        pass

    @abstractmethod
    def get_is_default(self) -> bool:
        """Check if the workspace is set as default for the monitor."""
        pass

    @abstractmethod
    def to_config_string(self) -> str:
        """Convert the workspace rule to a configuration string."""
        pass
