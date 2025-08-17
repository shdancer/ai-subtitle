import argparse
import os
from platformdirs import user_config_dir
from ai_subtitle_assistant.i18n import _
from colorama import Fore, Style, init

init(autoreset=True)

APP_NAME = "ai-subtitle"
CONFIG_DIR = user_config_dir(APP_NAME, "Lumos")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")


def configure_parser(parser):
    """Configure the config command parser."""
    parser.add_argument(
        "--show-path",
        action="store_true",
        help=_("Show the configuration file path"),
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help=_("Create or update configuration interactively"),
    )
    parser.set_defaults(func=handle_command)


def handle_command(args):
    """Handle the config command."""
    if args.show_path:
        print_config_path()
    elif args.create:
        create_or_update_config()
    else:
        # If no specific action is provided, show the path by default
        print_config_path()


def print_config_path():
    """Print the configuration file path."""
    print(
        Fore.YELLOW
        + _("Config file path: {config_file}").format(config_file=CONFIG_FILE)
    )


def create_or_update_config():
    """Create or update configuration interactively."""
    # Import the config module here to avoid circular imports
    from ai_subtitle_assistant.config import create_config_interactively, load_config

    print(Fore.CYAN + _("\n--- AI Subtitle Assistant Configuration Wizard ---"))
    config = load_config()
    if config:
        print(Fore.GREEN + _("Configuration already exists. Updating..."))
    create_config_interactively(config)
