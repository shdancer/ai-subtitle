

# AI Subtitle Assistant

[中文版本 (Chinese Version)](README_zh.md)

AI Subtitle Assistant is a command-line tool that uses AI technologies (Whisper and Large Language Models) to generate high-quality subtitles for video and audio files.

## Features

*   **Multi-format Support**: Handles various common video and audio file formats.
*   **High-precision Speech Recognition**: Uses OpenAI's Whisper model for accurate audio transcription.
*   **Intelligent Translation and Correction**: Leverages Large Language Models (LLMs) for translation, correcting errors based on context, and identifying proper nouns.
*   **Flexible LLM Configuration**: Allows users to customize the API base URL, key, and model for their LLM provider.
*   **Model Selection**: Choose from different LLM models for translation tasks.
*   **Debug Mode**: Enables detailed output of intermediate JSON data for troubleshooting.
*   **Standard Subtitle Output**: Generates standard UTF-8 encoded SRT subtitle files.
*   **Bilingual Subtitles**: Can generate bilingual subtitles for language learning.
*   **Embedded Subtitle Extraction**: Can detect and extract existing subtitle tracks from video files.
*   **Internationalization**: Supports multiple languages for the user interface (currently English and Chinese).
*   **User-friendly CLI**: Provides a clear and easy-to-use command-line interface with subcommands.

## Installation

**Recommended: Install from PyPI**
```bash
pip install ai-subtitle
```

**Or install from source:**
```bash
git clone https://github.com/shdancer/ai-subtitle
cd subtitle
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install .
```

**ffmpeg is required for audio processing.**
*   **On macOS (using Homebrew):**
    ```bash
    brew install ffmpeg
    ```
*   **On Debian/Ubuntu:**
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```
*   **On Windows (using Chocolatey):**
    ```bash
    choco install ffmpeg
    ```

## Usage

After installation, you can use the `ai-subtitle` command.

```bash
ai-subtitle <command> [options]
```

### Global Options
*   `--language {en,zh}`: Sets the display language for the tool. Defaults to your system's language.

### Commands

#### `transcribe`
Transcribes an audio/video file to an SRT file.

**Usage:**
`ai-subtitle transcribe <input_file> [options]`

**Arguments:**
*   `input_file`: Path to the input video or audio file.

**Options:**
*   `-o, --output`: Path to the output SRT file. If not specified, prints to standard output.
*   `-m, --model`: The Whisper model to use (e.g., `tiny`, `base`, `small`, `medium`, `large`). Default is `base`.
*   `--force-transcribe`: Force transcription even if embedded subtitles are found.

**Example:**
```bash
# Transcribe a video and save to a file
ai-subtitle transcribe my_video.mp4 -o my_video.srt

# Extract an embedded subtitle instead of transcribing
ai-subtitle transcribe my_movie.mkv -o movie_subs.srt
```

#### `translate`
Translates an existing SRT file into a bilingual SRT file.

**Usage:**
`ai-subtitle translate [input_file] [options]`

**Arguments:**
*   `input_file`: Path to the input SRT file. Reads from standard input if not provided.

**Options:**
*   `-o, --output`: Path to the output bilingual SRT file. Prints to standard output if not specified.
*   `-t, --target-language`: The target language for translation (e.g., "Chinese", "English"). Default is "Chinese".
*   `--model`: Select the model to use for translation (e.g., "gpt-3.5-turbo", "gpt-4"). Default is "gpt-3.5-turbo".
*   `--list-models`: List available models from the API and exit.
*   `--api-base-url`: Custom base URL for the LLM provider.
*   `--api-key`: Custom API key for the LLM provider.

**Example:**
```bash
# Transcribe and then translate
ai-subtitle transcribe my_video.mp4 | ai-subtitle translate -t "Japanese" -o bilingual.srt
```

#### `config`
Manages configuration settings for the AI Subtitle Assistant.

**Usage:**
`ai-subtitle config [options]`

**Options:**
*   `--show-path`: Show the configuration file path.
*   `--create`: Create or update configuration interactively.

**Example:**
```bash
# Show the configuration file path
ai-subtitle config --show-path

# Create or update configuration
ai-subtitle config --create
```

## How It Works

1.  **Audio Extraction/Transcription**: For the `transcribe` command, it either extracts existing subtitles or uses `ffmpeg` to extract audio and `whisper` to transcribe it into timed text segments.
2.  **Chunking & Translation**: For the `translate` command, it reads an SRT file, chunks the text to fit the LLM's context window, and sends it for translation.
3.  **LLM Processing**: The text is sent to the configured LLM for translation and refinement. The process includes retries and a progress bar.
4.  **SRT Generation**: The final processed text is formatted into a standard `.srt` file, either as a simple transcription or a bilingual subtitle.

## Changelog

### v0.1.3 (Upcoming)
- Added: Model selection feature for translation with `--model` option
- Added: List available models with `--list-models` option
- Added: Debug mode for troubleshooting translation issues (enabled via `AI_SUBTITLE_DEBUG=1` environment variable)
- Improved: Translation prompt to better handle different language structures and prevent subtitle misalignment
- Added: Graceful exit handling for keyboard interrupts (Ctrl+C)
- Added: Validation to check for missing translations

### v0.1.2
- Fixed: SRT multi-line content parsing bug, now all lines are preserved and correctly translated
- Improved: Documentation and README structure
- Updated: PyPI installation instructions and project metadata

### v0.1.1
- Fixed issue with pipeline operations where debug output was interfering with standard output
- Improved error handling and messaging
- Updated documentation with installation instructions from PyPI

### v0.1.0
- Initial release with core functionality
