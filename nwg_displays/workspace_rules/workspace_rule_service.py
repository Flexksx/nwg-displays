from abc import ABC, abstractmethod
from typing import List

from nwg_displays.workspace_rules.workspace_rule import WorkspaceRule


class WorkspaceRuleService(ABC):

    @abstractmethod
    def list(self) -> List[WorkspaceRule]:
        """
        List all workspace rules.
        """
        pass
