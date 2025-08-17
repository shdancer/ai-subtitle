import argparse
import sys
from ai_subtitle_assistant.commands import transcribe_cmd, translate_cmd, config_cmd
from ai_subtitle_assistant.i18n import set_language, _


def main():
    parser = argparse.ArgumentParser(
        description=_("A command-line tool for subtitle generation and translation."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--language",
        type=str,
        default="zh",
        help=_('Set the display language (e.g., "en", "zh").'),
    )

    subparsers = parser.add_subparsers(dest="command", help=_("Available commands"))
    subparsers.required = True

    # Transcribe command
    transcribe_parser = subparsers.add_parser(
        "transcribe", help=_("Transcribe audio/video to SRT.")
    )
    transcribe_cmd.configure_parser(transcribe_parser)

    # Translate command
    translate_parser = subparsers.add_parser(
        "translate", help=_("Translate an SRT file.")
    )
    translate_cmd.configure_parser(translate_parser)

    # Config command
    config_parser = subparsers.add_parser(
        "config", help=_("Manage configuration settings.")
    )
    config_cmd.configure_parser(config_parser)

    # First, parse only the language argument
    args, remaining_argv = parser.parse_known_args()

    # Set the language
    set_language(args.language)

    # Now, re-parse all arguments with the correct language set
    # This is a bit of a hack to make help messages translate correctly
    # A better solution might involve a more sophisticated argument parsing library
    parser.set_defaults(language=args.language)
    all_args = parser.parse_args()

    if hasattr(all_args, "func"):
        all_args.func(all_args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
