import ffmpeg
import sys


def probe_subtitles(video_file):
    """
    Probes a video file to find available subtitle streams.
    Returns a list of subtitle streams found.
    """
    try:
        print(f"Probing '{video_file}' for subtitle streams...", file=sys.stderr)
        probe = ffmpeg.probe(video_file)
        subtitle_streams = [
            stream for stream in probe["streams"] if stream["codec_type"] == "subtitle"
        ]
        return subtitle_streams
    except ffmpeg.Error as e:
        # Hide error if it's just about not finding streams, but show other errors
        if "could not find stream" not in e.stderr.decode(errors="ignore").lower():
            print(
                f"ffmpeg probe error: {e.stderr.decode(errors='ignore')}",
                file=sys.stderr,
            )
        return []


def extract_subtitle(video_file, stream_index):
    """
    Extracts a specific subtitle stream from a video file and returns it as SRT content.
    """
    print(f"Extracting subtitle stream {stream_index}...", file=sys.stderr)
    stream_specifier = f"0:s:{stream_index}"
    try:
        out, err = (
            ffmpeg.input(video_file)
            .output("pipe:", format="srt", map=stream_specifier)
            .run(capture_stdout=True, capture_stderr=True)
        )
        srt_content = out.decode("utf-8")
        if not srt_content.strip() and err:
            print(
                f"ffmpeg extraction warning: {err.decode(errors='ignore')}",
                file=sys.stderr,
            )
        return srt_content
    except ffmpeg.Error as e:
        print(
            f"Error extracting subtitle: {e.stderr.decode(errors='ignore')}",
            file=sys.stderr,
        )
        return None
