from nwg_displays.monitor.hyprland.hyprland_monitor_service import (
    HyprlandMonitorService,
)
from nwg_displays.workspace_rules.hyprland.hyprland_workspace_rule_service import (
    HyprlandWorkspaceRuleService,
)


hyprland_monitor_service = HyprlandMonitorService()
print(hyprland_monitor_service.list())

hyprland_workspace_rule_service = HyprlandWorkspaceRuleService()
print(hyprland_workspace_rule_service.list())
