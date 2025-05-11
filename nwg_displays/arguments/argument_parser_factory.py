from argparse import ArgumentParser

from nwg_displays.__about__ import __version__
from nwg_displays.session.session_service import SessionService


class ArgumentParserFactory:
    def __init__(self):
        pass

    def create(self, config_directory: str) -> ArgumentParser:
        session_server = SessionService()
        if session_server.is_hyprland_session():
            return self.create_for_hyprland(config_directory)
        elif session_server.is_sway_session():
            return self.create_for_sway(config_directory)

    def create_for_sway(self, config_directory: str) -> ArgumentParser:
        """
        Create an ArgumentParser for Sway.
        :return: An ArgumentParser instance configured for Sway.
        """
        parser = self._get_base_parser()
        parser.add_argument(
            "-o",
            "--outputs_path",
            type=str,
            default="{}/outputs".format(config_directory),
            help="path to save Outputs config to, default: {}".format(
                "{}/outputs".format(config_directory)
            ),
        )

        parser.add_argument(
            "-n",
            "--num_ws",
            type=int,
            default=8,
            help="number of Workspaces in use, default: 8",
        )
        return parser

    def create_for_hyprland(self, config_directory: str) -> ArgumentParser:
        """
        Create an ArgumentParser for Hyprland.
        :return: An ArgumentParser instance configured for Hyprland.
        """
        parser = self._get_base_parser()
        parser.add_argument(
            "-m",
            "--monitors_path",
            type=str,
            default="{}/monitors.conf".format(config_directory),
            help="path to save the monitors.conf file to, default: {}".format(
                "{}/monitors.conf".format(config_directory)
            ),
        )

        parser.add_argument(
            "-n",
            "--num_ws",
            type=int,
            default=10,
            help="number of Workspaces in use, default: 10",
        )

        return parser

    def _add_version_argument(self, parser: ArgumentParser) -> None:
        """
        Add a version argument to the parser.
        :param parser: The ArgumentParser instance to add the version argument to.
        """
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s version {}".format(__version__),
            help="display version information",
        )

    def _get_base_parser(self) -> ArgumentParser:
        """
        Create a base ArgumentParser with common arguments.
        :return: An ArgumentParser instance with common arguments.
        """
        parser = ArgumentParser(description="nwg-displays argument parser")
        self._add_version_argument(parser)
        return parser
