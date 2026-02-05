from argparse import ArgumentParser, Namespace


class ArgumentParserFactory:
    @staticmethod
    def create_hyprland_parser() -> ArgumentParser:
        parser = ArgumentParser(description="Hyprland display configuration utility")

    def __add_base_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-m",
            "--monitors_path",
            type=str,
            default="/tmp/hypr/monitors",
            help="Path to the Hyprland monitors file",
        )
        parser.add_argument(
            "-c",
            "--config_path",
            type=str,
            default="/tmp/hypr/hyprland.conf",
            help="Path to the Hyprland configuration file",
        )
