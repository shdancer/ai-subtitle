import openai
import json
import time
from datetime import timedelta
import sys
import os
import concurrent.futures
import threading
from tqdm import tqdm
from ai_subtitle_assistant.i18n import _
from colorama import Fore, Style

# 调试模式标志
DEBUG_MODE = os.environ.get("AI_SUBTITLE_DEBUG", "0") == "1"
# 线程锁，用于确保调试输出的线程安全
_debug_lock = threading.Lock()


def debug_print(message, data=None):
    """调试输出函数"""
    if DEBUG_MODE:
        with _debug_lock:
            print(f"\n[DEBUG] {message}", file=sys.stderr)
            if data is not None:
                if isinstance(data, str):
                    print(data, file=sys.stderr)
                else:
                    print(
                        json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr
                    )
            print("-" * 50, file=sys.stderr)


# Define a safe character count threshold to avoid token limits
# 4000 characters is a conservative value, as tokens are often more numerous than characters.
CHUNK_SIZE_LIMIT = 8000
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def _translate_chunk(client, chunk_segments, target_language, model):
    debug_print(f"翻译块开始，使用模型: {model}，目标语言: {target_language}")
    debug_print("输入段落:", chunk_segments)
    """
    Translates a single chunk of text with retry logic.
    """
    if not chunk_segments:
        return []

    segments_json_str = json.dumps(chunk_segments, ensure_ascii=False, indent=2)

    prompt = f"""
You are a professional subtitle translator. Your task is to translate the following subtitle segments into {target_language}.
The input is a JSON array of objects, where each object has an "id" and a "text" from the original ASR (Automatic Speech Recognition).

CRITICAL TRANSLATION RULES:
1. ACCURACY IS THE HIGHEST PRIORITY (1.0) - Each segment must be translated to contain ONLY the content from that specific segment
2. DO CONSIDER CONTEXT from surrounding segments to understand pronouns, proper nouns, and references
3. DO NOT MOVE ANY CONTENT between segments - this is absolutely forbidden
4. DO NOT REORDER SENTENCE STRUCTURE across segments
5. Each segment must stand on its own, even if it results in less natural phrasing

BALANCING CONTEXT AND ACCURACY WITH FLUENCY:
- USE context from other segments to understand meaning (pronouns, references, etc.)
- BUT translate ONLY the content within each specific segment
- STRIVE FOR NATURAL LANGUAGE FLOW within each segment (importance: 0.6)
- Pay attention to cultural context and idiomatic expressions in {target_language} (importance: 0.6)

EXAMPLES:

ORIGINAL SEGMENTS:
- Segment 278: "The first and most important rule of gunrunning"
- Segment 279: "is never get shot with your own merchandise."
- Segment 280: "You okay?"

CORRECT TRANSLATIONS:
- Segment 278: "枪械交易的第一条也是最重要的规则" (ONLY translates segment 278)
- Segment 279: "就是永远不要被自己的货物击中。" (ONLY translates segment 279)
- Segment 280: "你还好吗？" (ONLY translates segment 280)

INCORRECT TRANSLATIONS (DO NOT DO THIS):
- Segment 278: "枪械交易的第一条也是最重要的规则就是永远不要" (adding content from segment 279)
- Segment 279: "被自己的货物击中。你还好吗？" (adding content from segment 280)
- Segment 280: "我想是的。" (translating content from a different segment)

IMPORTANT: Even if a sentence is split across multiple segments, each segment must be translated separately. Do not attempt to create a more natural flow by moving content between segments.

Your output MUST be a valid JSON object that can be parsed by a JSON loader. The JSON object should contain a key "translations" which is an array of objects, with each object containing:
1. The original "id"
2. The "original_text" (exactly as provided, do not modify it)
3. The "translated_text" (your translation)

Do NOT add any extra explanations or text outside of the JSON object. The structure must be:
{{
  "translations": [
    {{
      "id": <original_id>,
      "original_text": "<original_text_exactly_as_provided>",
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
            debug_print("发送到API的提示:", prompt)
            response = client.chat.completions.create(
                model=model,
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
            response_content = response.choices[0].message.content
            debug_print("API响应:", response_content)
            response_data = json.loads(response_content)

            # Basic validation
            if "translations" in response_data and isinstance(
                response_data["translations"], list
            ):
                translations = response_data.get("translations", [])
                debug_print("解析后的翻译:", translations)

                # 检查返回的翻译数量是否与输入段落数量一致
                if len(translations) != len(chunk_segments):
                    print(
                        Fore.YELLOW
                        + _(
                            "Warning: Translation count mismatch. Expected {expected}, got {actual}. "
                            "This may be due to model context limits. Consider using a model with larger context or reducing input size."
                        ).format(expected=len(chunk_segments), actual=len(translations))
                        + Style.RESET_ALL,
                        file=sys.stderr,
                    )

                return translations
            else:
                raise ValueError(_("Invalid JSON structure in response"))

        except Exception as e:
            # 检查是否是JSON截断错误
            if "Unterminated string" in str(e) or "JSON" in str(e):
                print(
                    Fore.YELLOW
                    + _("Attempt {attempt}/{max_retries} failed: {e}").format(
                        attempt=attempt + 1, max_retries=MAX_RETRIES, e=e
                    )
                    + Style.RESET_ALL,
                    file=sys.stderr,
                )
                print(
                    Fore.YELLOW
                    + _(
                        "Warning: Output may be truncated due to model context limits. Consider using a model with larger context or reducing input size."
                    )
                    + Style.RESET_ALL,
                    file=sys.stderr,
                )
            else:
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


def _process_chunk(chunk_data):
    """处理单个块的内部函数"""
    client, chunk, target_language, model = chunk_data
    return _translate_chunk(client, chunk, target_language, model)


def translate_segments(
    segments,
    target_language,
    api_base_url,
    api_key,
    model="gpt-3.5-turbo",
    max_workers=5,
):
    debug_print("翻译开始，总段落数:", len(segments))
    debug_print("原始段落样本(前3个):", segments[:3] if len(segments) > 3 else segments)
    """
    Uses a large language model to translate and correct text segments, returning structured data.
    This function implements chunking to handle long texts and processes chunks concurrently.
    """
    client = openai.OpenAI(base_url=api_base_url, api_key=api_key)

    all_translated_segments = []
    current_chunk = []
    current_chunk_char_count = 0
    chunks_to_process = []

    debug_print(f"使用模型: {model}, 目标语言: {target_language}")
    debug_print(f"API基础URL: {api_base_url}")

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

    debug_print(f"分块完成，共 {len(chunks_to_process)} 个块")

    # Now, process the chunks concurrently with a progress bar
    with _debug_lock:
        print(
            Fore.CYAN
            + _("Translating {count} chunks...").format(count=len(chunks_to_process))
            + Style.RESET_ALL,
            file=sys.stderr,
        )

    # Prepare data for concurrent processing
    chunk_data_list = [
        (client, chunk, target_language, model) for chunk in chunks_to_process
    ]

    # Process chunks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_chunk = {
            executor.submit(_process_chunk, chunk_data): chunk_data
            for chunk_data in chunk_data_list
        }

        # Collect results with progress bar
        with tqdm(
            total=len(chunks_to_process), desc=_("Translating"), unit="chunk"
        ) as pbar:
            for future in concurrent.futures.as_completed(future_to_chunk):
                try:
                    translated_chunk = future.result()
                    # 验证返回的翻译结果
                    for item in translated_chunk:
                        # 检查是否包含original_text字段
                        if "original_text" in item:
                            # 验证original_text是否与本地原文一致
                            chunk_id = item["id"]
                            # 找到对应的原始段落
                            original_segment = next(
                                (seg for seg in segments if seg["id"] == chunk_id), None
                            )
                            if original_segment:
                                original_text = original_segment["text"].strip()
                                if item["original_text"] != original_text:
                                    debug_print(
                                        f"警告: ID {chunk_id} 的原文不匹配。本地: '{original_text}', 返回: '{item['original_text']}'"
                                    )
                                    # 如果不匹配，使用本地原文
                                    item["original_text"] = original_text
                        else:
                            # 如果没有original_text字段，从原始段落中获取
                            chunk_id = item["id"]
                            original_segment = next(
                                (seg for seg in segments if seg["id"] == chunk_id), None
                            )
                            if original_segment:
                                item["original_text"] = original_segment["text"].strip()

                    all_translated_segments.extend(translated_chunk)
                except Exception as e:
                    print(
                        Fore.RED
                        + _("Error processing chunk: {e}").format(e=e)
                        + Style.RESET_ALL,
                        file=sys.stderr,
                    )
                pbar.update(1)

    with _debug_lock:
        print(
            Fore.GREEN + _("All chunks translated.") + Style.RESET_ALL, file=sys.stderr
        )

    translation_map = {
        item["id"]: item["translated_text"] for item in all_translated_segments
    }

    debug_print("翻译映射:", translation_map)

    # 验证所有段落是否都有对应的翻译
    missing_ids = []
    for segment in segments:
        if segment["id"] not in translation_map:
            missing_ids.append(segment["id"])

    if missing_ids:
        debug_print(f"警告: 以下ID没有对应的翻译: {missing_ids}")
        with _debug_lock:
            print(
                Fore.YELLOW
                + _(
                    "Warning: {count} segments have no corresponding translations."
                ).format(count=len(missing_ids))
                + Style.RESET_ALL,
                file=sys.stderr,
            )

    bilingual_subtitles = []
    for segment in segments:
        segment_id = segment["id"]
        original_text = segment["text"].strip()
        translated_text = translation_map.get(segment_id, _("[Translation Failed]"))

        # 如果使用了默认值，给出警告
        if translated_text == _("[Translation Failed]"):
            with _debug_lock:
                print(
                    Fore.YELLOW
                    + _(
                        "Warning: Translation failed for segment {id}. Using default value."
                    ).format(id=segment_id)
                    + Style.RESET_ALL,
                    file=sys.stderr,
                )

        bilingual_subtitles.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "original_text": original_text,
                "translated_text": translated_text,
            }
        )

    debug_print(
        "最终双语字幕样本(前3个):",
        (
            bilingual_subtitles[:3]
            if len(bilingual_subtitles) > 3
            else bilingual_subtitles
        ),
    )
    return bilingual_subtitles
