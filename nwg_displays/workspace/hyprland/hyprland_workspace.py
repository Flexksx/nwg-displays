from nwg_displays.workspace.workspace import Workspace


class HyprlandWorkspace(Workspace):
    def __init__(
        self, name: str = "", id: int = 0, monitor_name: str = "", monitor_id: int = 0
    ):
        self.name = name
        self.id = id
        self.monitor_name = monitor_name
        self.monitor_id = monitor_id

    @classmethod
    def from_hyprland_response(cls, data: dict) -> "HyprlandWorkspace":
        return cls(
            name=data["name"],
            id=data["id"],
            monitor_name=data["monitor"],
            monitor_id=data["monitorID"],
        )

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_monitor_name(self):
        return self.monitor_name

    def get_monitor_id(self):
        return self.monitor_id
