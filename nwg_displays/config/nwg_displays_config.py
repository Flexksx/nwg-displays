import json
import os
import sys
import threading
from nwg_displays.tools import load_json, save_json
from nwg_displays.logger import get_class_logger

DEFAULT_VIEW_SCALE = 0.15
DEFAULT_SNAP_THRESHOLD = 10
DEFAULT_INDICATOR_TIMEOUT = 500
DEFAULT_CUSTOM_MODE = []
DEFAULT_USE_DESC = False
DEFAULT_CONFIRM_TIMEOUT = 10

CONFIG_LOCK = threading.Lock()


class NwgDisplaysConfig:
    def __init__(
        self,
        view_scale: float = DEFAULT_VIEW_SCALE,
        snap_threshold: int = DEFAULT_SNAP_THRESHOLD,
        indicator_timeout: int = DEFAULT_INDICATOR_TIMEOUT,
        custom_mode: list = None,
        use_desc: bool = DEFAULT_USE_DESC,
        confirm_timeout: int = DEFAULT_CONFIRM_TIMEOUT,
        _on_change=None,
    ):
        self.__logger = get_class_logger(self.__class__)
        self._on_change = _on_change

        self._view_scale = view_scale
        self._snap_threshold = snap_threshold
        self._indicator_timeout = indicator_timeout
        self._custom_mode = custom_mode if custom_mode is not None else []
        self._use_desc = use_desc
        self._confirm_timeout = confirm_timeout

    @classmethod
    def from_dict(cls, config_dict: dict, _on_change=None):
        return cls(
            view_scale=config_dict.get("view-scale", DEFAULT_VIEW_SCALE),
            snap_threshold=config_dict.get("snap-threshold", DEFAULT_SNAP_THRESHOLD),
            indicator_timeout=config_dict.get(
                "indicator-timeout", DEFAULT_INDICATOR_TIMEOUT
            ),
            custom_mode=config_dict.get("custom-mode", DEFAULT_CUSTOM_MODE),
            use_desc=config_dict.get("use-desc", DEFAULT_USE_DESC),
            confirm_timeout=config_dict.get("confirm-timeout", DEFAULT_CONFIRM_TIMEOUT),
            _on_change=_on_change,
        )

    def __str__(self):
        return (
            f"NwgDisplaysConfig(view_scale={self.view_scale}, "
            f"snap_threshold={self.snap_threshold}, "
            f"indicator_timeout={self.indicator_timeout}, "
            f"custom_mode={self.custom_mode}, "
            f"use_desc={self.use_desc}, "
            f"confirm_timeout={self.confirm_timeout})"
        )

    def __repr__(self):
        return self.to_dict().__repr__()

    def to_dict(self) -> dict:
        return {
            "view-scale": self.view_scale,
            "snap-threshold": self.snap_threshold,
            "indicator-timeout": self.indicator_timeout,
            "custom-mode": self.custom_mode,
            "use-desc": self.use_desc,
            "confirm-timeout": self.confirm_timeout,
        }

    @property
    def view_scale(self) -> float:
        return self._view_scale

    @view_scale.setter
    def view_scale(self, value: float) -> None:
        if value != self._view_scale:
            self._view_scale = value
            self._emit_change("view-scale", value)

    @property
    def snap_threshold(self) -> int:
        return self._snap_threshold

    @snap_threshold.setter
    def snap_threshold(self, value: int) -> None:
        if value != self._snap_threshold:
            self._snap_threshold = value
            self._emit_change("snap-threshold", value)

    @property
    def indicator_timeout(self) -> int:
        return self._indicator_timeout

    @indicator_timeout.setter
    def indicator_timeout(self, value: int) -> None:
        if value != self._indicator_timeout:
            self._indicator_timeout = value
            self._emit_change("indicator-timeout", value)

    @property
    def custom_mode(self) -> list:
        return self._custom_mode

    @custom_mode.setter
    def custom_mode(self, value: list) -> None:
        if value != self._custom_mode:
            self._custom_mode = value
            self._emit_change("custom-mode", value)

    @property
    def use_desc(self) -> bool:
        return self._use_desc

    @use_desc.setter
    def use_desc(self, value: bool) -> None:
        if value != self._use_desc:
            self._use_desc = value
            self._emit_change("use-desc", value)

    @property
    def confirm_timeout(self) -> int:
        return self._confirm_timeout

    @confirm_timeout.setter
    def confirm_timeout(self, value: int) -> None:
        if value != self._confirm_timeout:
            self._confirm_timeout = value
            self._emit_change("confirm-timeout", value)

    def _emit_change(self, field: str, value):
        self.__logger.info(f"Changed {field} to {value}")
        if self._on_change:
            self._on_change()


class ConfigurationService:
    _instance = None
    _init_lock = threading.Lock()

    @classmethod
    def get(cls):
        """Get the singleton instance of ConfigurationService."""
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self, config_dir: str = None, config_file: str = None):
        if hasattr(self, "_initialized"):
            return  # Don't allow re-init
        self._initialized = True

        self.logger = get_class_logger(self.__class__)

        self.__XDG_CONFIG_HOME = os.getenv("XDG_CONFIG_HOME")
        self.__HOME_DIR = os.getenv("HOME")
        self.__DEFAULT_CONFIG_DIRNAME = ".config"
        self.__DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME = "nwg-displays"
        self.__OLD_DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME = "nwg-outputs"
        self.__DEFAULT_CONFIG_FILENAME = "config"

        if config_dir is None:
            config_dir = self._get_default_config_dir()
        self.config_dir = config_dir

        if config_file is None:
            config_file = self.__DEFAULT_CONFIG_FILENAME
        self.config_file = config_file
        self._config_path = os.path.join(self.config_dir, self.config_file)

        self._config = None
        self.reload()

    def get_config(self) -> NwgDisplaysConfig:
        return self._config

    def save(self):
        """Save the config to disk (thread-safe)."""
        with CONFIG_LOCK:
            data = self._config.to_dict()
            os.makedirs(self.config_dir, exist_ok=True)
            save_json(data, self._config_path)
            self.logger.info(f"Saved config to: '{self._config_path}'")

    def reload(self):
        """Reload config from disk (replaces the config instance)."""
        with CONFIG_LOCK:
            if not os.path.isfile(self._config_path):
                # Try to migrate from old config path
                old_config_path = os.path.join(
                    self.__OLD_DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME, "config"
                )
                if os.path.isfile(old_config_path):
                    self.logger.info("Migrating config to the proper path...")
                    os.rename(
                        self.__OLD_DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME, self.config_dir
                    )
            if not os.path.isdir(self.config_dir):
                os.makedirs(self.config_dir, exist_ok=True)
            if not os.path.isfile(self._config_path):
                self.logger.warning(f"'{self.config_file}' not found, creating default")
                data = NwgDisplaysConfig().to_dict()
                save_json(data, self._config_path)
            else:
                try:
                    data = load_json(self._config_path)
                    # Check if data is None or not a dictionary
                    if data is None or not isinstance(data, dict):
                        self.logger.warning(
                            f"Invalid config file format in '{self._config_path}', using defaults"
                        )
                        data = NwgDisplaysConfig().to_dict()
                        save_json(data, self._config_path)
                except Exception as e:
                    self.logger.error(
                        f"Failed to load config from '{self._config_path}': {e}. Falling back to default config."
                    )
                    data = NwgDisplaysConfig().to_dict()
                    save_json(data, self._config_path)

            # Ensure all default keys exist
            key_missing = False
            defaults = NwgDisplaysConfig().to_dict()
            for k in defaults:
                if k not in data:
                    data[k] = defaults[k]
                    key_missing = True
                    self.logger.info(f"Added missing config key: '{k}'")
            if key_missing:
                save_json(data, self._config_path)

            self._config = NwgDisplaysConfig.from_dict(data, _on_change=self.save)
            self.logger.info(f"Loaded config from: '{self._config_path}':")
            self.logger.info(f"Config: {json.dumps(data)}")

    def _get_default_config_dir(self):
        config_home = (
            self.__XDG_CONFIG_HOME
            if self.__XDG_CONFIG_HOME
            else os.path.join(self.__HOME_DIR, self.__DEFAULT_CONFIG_DIRNAME)
        )
        return os.path.join(config_home, self.__DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME)
