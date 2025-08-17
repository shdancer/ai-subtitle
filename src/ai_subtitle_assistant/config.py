import configparser
import os
from platformdirs import user_config_dir
from ai_subtitle_assistant.i18n import _
from colorama import Fore, Style, init

init(autoreset=True)

APP_NAME = "ai-subtitle-assistant"
CONFIG_DIR = user_config_dir(APP_NAME, "Lumos")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")

print(
    Fore.YELLOW + _("Config file path: {config_file}").format(config_file=CONFIG_FILE)
)


def load_config():
    """Loads the configuration from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return create_config_interactively()

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    # Check for required keys
    if (
        "DEFAULT" not in config
        or "api_key" not in config["DEFAULT"]
        or "api_base_url" not in config["DEFAULT"]
    ):
        print(Fore.YELLOW + _("Configuration file is incomplete."))
        return create_config_interactively(config)

    return config


def create_config_interactively(existing_config=None):
    """Prompts the user for configuration details and saves them."""
    print(Fore.CYAN + _("\n--- AI Subtitle Assistant Configuration Wizard ---"))
    if not existing_config:
        print(
            Fore.YELLOW
            + _(
                "It seems this is your first time running the program, or the config file is missing."
            )
        )
        existing_config = configparser.ConfigParser()
        # 'DEFAULT' section is created automatically, no need to add it.

    print(_("Please enter the following information to complete the setup:"))

    default_base_url = existing_config.get(
        "DEFAULT", "api_base_url", fallback="https://api.openai.com/v1"
    )
    api_base_url = input(
        _(
            "Enter the Base URL for your LLM provider [default: {default_base_url}]: "
        ).format(default_base_url=default_base_url)
    ).strip()
    if not api_base_url:
        api_base_url = default_base_url

    default_api_key = existing_config.get("DEFAULT", "api_key", fallback="")
    api_key = input(
        _("Enter your API Key [{masked_key}]: ").format(
            masked_key="*" * len(default_api_key) if default_api_key else _("required")
        )
    ).strip()
    if not api_key:
        api_key = default_api_key

    if not api_key:
        print(Fore.RED + _("\nError: API Key is required. Configuration not saved."))
        # Returning an empty config parser
        return configparser.ConfigParser()

    existing_config["DEFAULT"]["api_base_url"] = api_base_url
    existing_config["DEFAULT"]["api_key"] = api_key

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as configfile:
        existing_config.write(configfile)

    print(
        Fore.GREEN
        + _("\nConfiguration successfully saved to: {config_file}").format(
            config_file=CONFIG_FILE
        )
    )
    print(_("You can manually edit this file at any time."))

    return existing_config


def get_config_value(config, key, default=None):
    """Gets a value from the config, with a fallback."""
    if config and "DEFAULT" in config:
        return config["DEFAULT"].get(key, default)
    return default
