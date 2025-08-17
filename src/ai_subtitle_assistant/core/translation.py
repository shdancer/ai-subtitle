import openai
import json
import time
from datetime import timedelta
import sys
from tqdm import tqdm
from ai_subtitle_assistant.i18n import _
from colorama import Fore, Style

# Define a safe character count threshold to avoid token limits
# 4000 characters is a conservative value, as tokens are often more numerous than characters.
CHUNK_SIZE_LIMIT = 8000
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def _translate_chunk(client, chunk_segments, target_language):
    """
    Translates a single chunk of text with retry logic.
    """
    if not chunk_segments:
        return []

    segments_json_str = json.dumps(chunk_segments, ensure_ascii=False, indent=2)

    prompt = f"""
You are a professional subtitle translator. Your task is to translate the following subtitle segments into {target_language}.
The input is a JSON array of objects, where each object has an "id" and a "text" from the original ASR (Automatic Speech Recognition).
Please maintain the original meaning, fix any potential ASR errors based on context, and ensure the translation is natural and fluent.

Your output MUST be a valid JSON object that can be parsed by a JSON loader. The JSON object should contain a key "translations" which is an array of objects, with each object containing the original "id" and the "translated_text".
Do NOT add any extra explanations or text outside of the JSON object. The structure must be:
{{
  "translations": [
    {{
      "id": <original_id>,
      "translated_text": "<your_translation>"
    }},
    ...
  ]
}}

Here is the JSON data to translate:
{segments_json_str}
"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Or any other model you prefer
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional subtitle translator translating subtitles into {target_language}. Your output must be a valid JSON object.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            response_data = json.loads(response.choices[0].message.content)

            # Basic validation
            if "translations" in response_data and isinstance(
                response_data["translations"], list
            ):
                return response_data.get("translations", [])
            else:
                raise ValueError(_("Invalid JSON structure in response"))

        except Exception as e:
            print(
                Fore.YELLOW
                + _("Attempt {attempt}/{max_retries} failed: {e}").format(
                    attempt=attempt + 1, max_retries=MAX_RETRIES, e=e
                )
                + Style.RESET_ALL,
                file=sys.stderr,
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(
                    Fore.RED
                    + _("Error translating chunk after multiple retries.")
                    + Style.RESET_ALL,
                    file=sys.stderr,
                )
                return [
                    {
                        "id": seg["id"],
                        "translated_text": _("[Chunk Translation Failed]"),
                    }
                    for seg in chunk_segments
                ]
    return []  # Should not be reached, but as a fallback


def translate_segments(segments, target_language, api_base_url, api_key):
    """
    Uses a large language model to translate and correct text segments, returning structured data.
    This function implements chunking to handle long texts.
    """
    client = openai.OpenAI(base_url=api_base_url, api_key=api_key)

    all_translated_segments = []
    current_chunk = []
    current_chunk_char_count = 0
    chunks_to_process = []

    # First, divide the segments into chunks
    for segment in segments:
        segment_text = segment["text"].strip()
        simple_segment = {"id": segment["id"], "text": segment_text}
        estimated_added_len = len(json.dumps(simple_segment, ensure_ascii=False))

        if current_chunk and (
            current_chunk_char_count + estimated_added_len > CHUNK_SIZE_LIMIT
        ):
            chunks_to_process.append(current_chunk)
            current_chunk = [simple_segment]
            current_chunk_char_count = estimated_added_len
        else:
            current_chunk.append(simple_segment)
            current_chunk_char_count += estimated_added_len

    if current_chunk:
        chunks_to_process.append(current_chunk)

    # Now, process the chunks with a progress bar
    print(
        Fore.CYAN
        + _("Translating {count} chunks...").format(count=len(chunks_to_process))
        + Style.RESET_ALL,
        file=sys.stderr,
    )

    with tqdm(
        total=len(chunks_to_process), desc=_("Translating"), unit="chunk"
    ) as pbar:
        for chunk in chunks_to_process:
            translated_chunk = _translate_chunk(client, chunk, target_language)
            all_translated_segments.extend(translated_chunk)
            pbar.update(1)

    print(Fore.GREEN + _("All chunks translated.") + Style.RESET_ALL, file=sys.stderr)

    translation_map = {
        item["id"]: item["translated_text"] for item in all_translated_segments
    }

    bilingual_subtitles = []
    for segment in segments:
        segment_id = segment["id"]
        original_text = segment["text"].strip()
        translated_text = translation_map.get(segment_id, _("[Translation Failed]"))

        bilingual_subtitles.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "original_text": original_text,
                "translated_text": translated_text,
            }
        )

    return bilingual_subtitles
