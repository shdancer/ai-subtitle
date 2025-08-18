import argparse
import sys
import os
from ai_subtitle_assistant.core.translation import translate_segments
from ai_subtitle_assistant.core.srt_utils import parse_srt, to_bilingual_srt
from ai_subtitle_assistant.config import load_config, get_config_value, CONFIG_FILE
from ai_subtitle_assistant.i18n import _
from colorama import Fore, Style, init

init(autoreset=True)


def configure_parser(parser):
    """
    Configures the parser for the translate command.
    """
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help=_("Path to the input SRT file. If not provided, reads from stdin."),
    )
    parser.add_argument(
        "-o",
        "--output",
        help=_(
            "Path to the output bilingual SRT file. If not specified, prints to stdout."
        ),
    )
    parser.add_argument(
        "-t",
        "--target-language",
        default="Chinese",
        help=_(
            "The target language for translation (e.g., Chinese, English, Japanese)."
        ),
    )
    parser.add_argument(
        "--api-base-url", help=_("Custom base URL for the LLM provider.")
    )
    parser.add_argument("--api-key", help=_("Custom API Key for the LLM provider."))
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help=_("Select the model to use for translation."),
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=5,
        help=_("Maximum number of concurrent translation requests."),
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help=_("List available models and exit."),
    )
    parser.set_defaults(func=run)


def run(args):
    """
    The main function for the translate command.
    """
    config = load_config()

    # Get API credentials
    api_base_url = args.api_base_url or get_config_value(config, "api_base_url")
    api_key = args.api_key or get_config_value(config, "api_key")

    if not api_key or not api_base_url:
        print(
            Fore.RED + _("Error: API Key and Base URL must be configured."),
            file=sys.stderr,
        )
        print(
            Fore.YELLOW
            + _("Please edit the config file at: {config_file}").format(
                config_file=CONFIG_FILE
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    if args.list_models:
        try:
            import openai

            client = openai.OpenAI(base_url=api_base_url, api_key=api_key)
            models = client.models.list()
            print(_("Available models:"))
            for m in models.data:
                print(" -", m.id)
        except Exception as e:
            print(
                Fore.RED + _("Failed to fetch models from API: {e}").format(e=e),
                file=sys.stderr,
            )
        return

    try:
        # 1. Read SRT input
        srt_content = ""
        if args.input_file:
            with open(args.input_file, "r", encoding="utf-8") as f:
                srt_content = f.read()
        elif not sys.stdin.isatty():
            srt_content = sys.stdin.read()
        else:
            print(
                Fore.RED + _("Error: No input file provided and no data from stdin."),
                file=sys.stderr,
            )
            print(Fore.YELLOW + _("Use --help for more information."), file=sys.stderr)
            sys.exit(1)

        # 2. Parse SRT content into segments
        segments = parse_srt(srt_content)
        if not segments:
            print(Fore.RED + _("Error: Could not parse SRT content."), file=sys.stderr)
            sys.exit(1)

        # 3. Translate segments
        bilingual_subtitles = translate_segments(
            segments,
            args.target_language,
            api_base_url,
            api_key,
            args.model,
            args.max_workers,
        )

        # 4. Convert to bilingual SRT format
        output_srt = to_bilingual_srt(bilingual_subtitles)

        # 5. Output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_srt)
            print(
                Fore.GREEN
                + _("Bilingual SRT file saved to {output}").format(output=args.output),
                file=sys.stderr,
            )
        else:
            print(output_srt)

    except FileNotFoundError:
        print(
            Fore.RED
            + _("Error: The input file '{file}' was not found.").format(
                file=args.input_file
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        print(
            Fore.RED + _("An unexpected error occurred: {e}").format(e=e),
            file=sys.stderr,
        )
        sys.exit(1)
