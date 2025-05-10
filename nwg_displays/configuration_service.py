import json
import os
import sys
import logging
from nwg_displays.tools import load_json, save_json


class ConfigurationService:
    def __init__(self, config_dir: str = None, config_file: str = None):
        self.__XDG_CONFIG_HOME = os.getenv("XDG_CONFIG_HOME")
        self.__HOME_DIR = os.getenv("HOME")
        self.__DEFAULT_CONFIG_DIRNAME = ".config"
        self.__DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME = "nwg-displays"
        self.__OLD_DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME = "nwg-outputs"
        self.__DEFAULT_CONFIG_FILENAME = "config"  # Add a default filename

        self.logger = logging.getLogger(__name__)

        if config_dir is None:
            config_dir = self._get_default_config_dir()
        self.config_dir = config_dir

        # Set a default value for config_file if it's None
        if config_file is None:
            config_file = self.__DEFAULT_CONFIG_FILENAME
        self.config_file = config_file

    def get_config_directory(self) -> str:
        """
        Get the configuration directory.
        """
        return self.config_dir

    def set_config_directory(self, config_dir: str) -> None:
        """
        Set the configuration directory.
        """
        self.config_dir = config_dir

    def get_config_file(self) -> str:
        """
        Get the configuration file.
        """
        return self.config_file

    def set_config_file(self, config_file: str) -> None:
        """
        Set the configuration file.
        """
        self.config_file = config_file

    def _config_keys_missing(self, config, config_file):
        key_missing = False
        defaults = {
            "view-scale": 0.15,
            "snap-threshold": 10,
            "indicator-timeout": 500,
            "custom-mode": [],
            "use-desc": False,
            "confirm-timeout": 10,
        }
        for key in defaults:
            if key not in config:
                config[key] = defaults[key]
                print("Added missing config key: '{}'".format(key), file=sys.stderr)
                key_missing = True

        if key_missing:
            save_json(config, config_file)
        return key_missing

    def _get_default_config_dir(self):
        config_home = (
            self.__XDG_CONFIG_HOME
            if self.__XDG_CONFIG_HOME
            else os.path.join(self.__HOME_DIR, self.__DEFAULT_CONFIG_DIRNAME)
        )
        return os.path.join(config_home, self.__DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME)

    def load_config(self) -> dict:
        """
        Load the configuration from the file.
        """
        config_file_path = os.path.join(self.config_dir, self.config_file)

        if not os.path.isfile(config_file_path):
            # migrate old config file, if not yet migrated
            old_config_path = os.path.join(
                self.__OLD_DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME, "config"
            )

            if os.path.isfile(old_config_path):
                print("Migrating config to the proper path...")
                os.rename(
                    self.__OLD_DEFAULT_NWG_DISPLAYS_CONFIG_DIRNAME, self.config_dir
                )
            else:
                if not os.path.isdir(self.config_dir):
                    os.makedirs(self.config_dir, exist_ok=True)

                print("'{}' file not found, creating default".format(self.config_file))
                config = {}  # Initialize an empty config
                save_json(config, config_file_path)  # Save to the full path
        else:
            config = load_json(config_file_path)  # Load from the full path

        if self._config_keys_missing(config, config_file_path):
            config = load_json(config_file_path)

        return config
