import argparse
import sys
from ai_subtitle_assistant.core.transcription import transcribe
from ai_subtitle_assistant.core.srt_utils import to_srt
from ai_subtitle_assistant.core.video_utils import probe_subtitles, extract_subtitle
from ai_subtitle_assistant.i18n import _
from colorama import Fore, Style, init

init(autoreset=True)


def configure_parser(parser):
    """
    Configures the parser for the transcribe command.
    """
    parser.add_argument("input_file", help=_("Path to the input video or audio file."))
    parser.add_argument(
        "-o",
        "--output",
        help=_("Path to the output SRT file. If not specified, prints to stdout."),
    )
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        help=_(
            "Name of the Whisper model to use (e.g., tiny, base, small, medium, large)."
        ),
    )
    parser.add_argument(
        "--force-transcribe",
        action="store_true",
        help=_("Force transcription even if embedded subtitles are found."),
    )
    parser.set_defaults(func=run)


def run(args):
    """
    The main function for the transcribe command.
    """
    try:
        # Check for embedded subtitles if it's a video file and not forced
        if not args.force_transcribe and args.input_file.lower().endswith(
            (".mp4", ".mkv", ".avi", ".mov")
        ):
            subtitle_streams = probe_subtitles(args.input_file)
            if subtitle_streams:
                print(
                    Fore.YELLOW + _("Found embedded subtitle streams:"), file=sys.stderr
                )
                for i, stream in enumerate(subtitle_streams):
                    lang = stream.get("tags", {}).get("language", _("unknown"))
                    title = stream.get("tags", {}).get("title", _("No Title"))
                    print(
                        f"  {i}: "
                        + Fore.CYAN
                        + _("Language: {lang}, Title: {title}").format(
                            lang=lang, title=title
                        ),
                        file=sys.stderr,
                    )

                try:
                    print(
                        Fore.GREEN
                        + _(
                            "Enter the number of the subtitle to extract, or press Enter to transcribe instead: "
                        ),
                        file=sys.stderr,
                    )
                    choice = input()
                    if choice.strip().isdigit():
                        stream_index = int(choice.strip())
                        if 0 <= stream_index < len(subtitle_streams):
                            # Extract the chosen subtitle stream
                            srt_content = extract_subtitle(
                                args.input_file, stream_index
                            )
                            if srt_content:
                                # Output the extracted subtitle
                                if args.output:
                                    with open(args.output, "w", encoding="utf-8") as f:
                                        f.write(srt_content)
                                    print(
                                        Fore.GREEN
                                        + _(
                                            "Extracted subtitle saved to {output}"
                                        ).format(output=args.output),
                                        file=sys.stderr,
                                    )
                                else:
                                    print(srt_content)
                                sys.exit(0)  # Success
                            else:
                                print(
                                    Fore.RED
                                    + _(
                                        "Failed to extract subtitle. Proceeding with transcription."
                                    ),
                                    file=sys.stderr,
                                )
                        else:
                            print(
                                Fore.RED
                                + _(
                                    "Invalid selection. Proceeding with transcription."
                                ),
                                file=sys.stderr,
                            )
                    else:
                        print(
                            Fore.YELLOW
                            + _("No selection made. Proceeding with transcription."),
                            file=sys.stderr,
                        )
                except (EOFError, KeyboardInterrupt):
                    print(
                        Fore.RED + _("\nOperation cancelled by user. Exiting."),
                        file=sys.stderr,
                    )
                    sys.exit(1)

        # 1. Transcribe audio
        print(
            Fore.BLUE + _("No subtitles extracted. Starting transcription..."),
            file=sys.stderr,
        )
        transcription_result = transcribe(args.input_file, args.model)

        # 2. Convert to SRT format
        srt_content = to_srt(transcription_result["segments"])

        # 3. Output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(srt_content)
                print(
                    Fore.GREEN
                    + _("Transcription saved to {output}").format(output=args.output),
                    file=sys.stderr,
                )
        else:
            print(srt_content)

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
