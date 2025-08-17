import srt
from datetime import timedelta


def to_srt(segments):
    """
    Converts a list of segments to SRT format content.
    Each segment is a dict with 'start', 'end', 'text'.
    """
    subs = []
    for i, segment in enumerate(segments):
        start_time = timedelta(seconds=segment["start"])
        end_time = timedelta(seconds=segment["end"])
        subtitle = srt.Subtitle(
            index=i + 1,
            start=start_time,
            end=end_time,
            content=segment["text"].strip(),
        )
        subs.append(subtitle)
    return srt.compose(subs)


def to_bilingual_srt(bilingual_subtitles):
    """
    Saves bilingual subtitle data to an SRT file string.
    Format:
    Translated Language
    Original Language
    """
    subs = []
    for i, sub_data in enumerate(bilingual_subtitles):
        content = f"{sub_data['translated_text']}\n{sub_data['original_text']}"
        start_time = (
            sub_data["start"]
            if isinstance(sub_data["start"], timedelta)
            else timedelta(seconds=sub_data["start"])
        )
        end_time = (
            sub_data["end"]
            if isinstance(sub_data["end"], timedelta)
            else timedelta(seconds=sub_data["end"])
        )
        subtitle = srt.Subtitle(
            index=i + 1, start=start_time, end=end_time, content=content
        )
        subs.append(subtitle)
    return srt.compose(subs)


def parse_srt(srt_content):
    """
    Parses SRT content from a string and converts it to a segment list.
    """
    subs = list(srt.parse(srt_content))
    segments = []
    for i, sub in enumerate(subs):
        # 保留所有原文内容（多行内容也完整保留）
        original_text = sub.content.strip()
        segments.append(
            {
                "id": i,
                "start": sub.start.total_seconds(),
                "end": sub.end.total_seconds(),
                "text": original_text,
            }
        )
    return segments
