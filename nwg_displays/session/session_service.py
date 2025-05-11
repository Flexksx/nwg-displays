import os

from nwg_displays.session.session_type import SessionType


class SessionService:
    def __init__(self):
        self._session_type: SessionType = self.determine_session_type()

    @classmethod
    def is_hyprland_session(self) -> bool:
        return os.getenv("HYPRLAND_INSTANCE_SIGNATURE") is not None

    @classmethod
    def is_sway_session(cls) -> bool:
        return os.getenv("SWAYSOCK") is not None

    @classmethod
    def determine_session_type(cls) -> SessionType:
        if cls.is_hyprland_session():
            return SessionType.HYPRLAND
        elif cls.is_sway_session():
            return SessionType.SWAY
        else:
            raise ValueError(
                "Unsupported session type. Only Hyprland and Sway are supported."
            )

    def get_session_type(self) -> SessionType:
        return self._session_type
