from nwg_displays.workspace_rules.workspace_rule import WorkspaceRule


class HyprlandWorkspaceRule(WorkspaceRule):
    def __init__(self, workspace_id: str, monitor_name: str, is_default: bool):
        self.workspace_id: str = workspace_id
        self.monitor_name: str = monitor_name
        self.is_default: bool = is_default

    @classmethod
    def from_hyprland_response(cls, data: dict) -> "HyprlandWorkspaceRule":
        workspace_id = data.get("workspaceString", "")
        monitor_name = data.get("monitor", "")
        is_default = data.get("default", False)
        return cls(workspace_id, monitor_name, is_default)

    def get_workspace_id(self):
        return self.workspace_id

    def get_monitor_name(self):
        return self.monitor_name

    def get_is_default(self):
        return self.is_default

    def to_config_string(self):
        return f"workspace={self.workspace_id},monitor:{self.monitor_name},default:{str(self.is_default).lower()}"
