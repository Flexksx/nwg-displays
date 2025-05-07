import json
from typing import List
from nwg_displays.workspace_rules.hyprland.hyprland_workspace_rule import (
    HyprlandWorkspaceRule,
)
from nwg_displays.workspace_rules.workspace_rule import WorkspaceRule
from nwg_displays.workspace_rules.workspace_rule_service import WorkspaceRuleService
from tools import hyprctl


class HyprlandWorkspaceRuleService(WorkspaceRuleService):
    def list(self) -> List[WorkspaceRule]:
        workspace_rules = json.loads(hyprctl("j/workspacerules"))
        return [
            HyprlandWorkspaceRule.from_hyprland_response(rule)
            for rule in workspace_rules
        ]
