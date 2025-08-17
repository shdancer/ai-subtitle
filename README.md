# AI Subtitle Assistant / AI 智能字幕助手

This is a command-line tool that uses AI technologies (Whisper and Large Language Models) to generate high-quality subtitles for video and audio files.

这是一个使用 AI 技术（Whisper 和大型语言模型）为视频和音频文件生成高质量字幕的命令行工具。

## Features / 功能

*   **Multi-format Support**: Handles various common video and audio file formats.
    *   **多格式支持**：处理各种常见的视频和音频文件格式。
*   **High-precision Speech Recognition**: Uses OpenAI's Whisper model for accurate audio transcription.
    *   **高精度语音识别**：使用 OpenAI 的 Whisper 模型进行准确的音频转录。
*   **Intelligent Translation and Correction**: Leverages Large Language Models (LLMs) for translation, correcting errors based on context, and identifying proper nouns.
    *   **智能翻译与校正**：利用大型语言模型（LLM）进行翻译，并根据上下文修正错误、识别专有名词。
*   **Flexible LLM Configuration**: Allows users to customize the API base URL and key for their LLM provider.
    *   **灵活的 LLM 配置**：允许用户自定义 LLM 提供商的 API 地址和密钥。
*   **Standard Subtitle Output**: Generates standard UTF-8 encoded SRT subtitle files.
    *   **标准字幕输出**：生成通用的 UTF-8 编码的 SRT 字幕文件。
*   **Bilingual Subtitles**: Can generate bilingual subtitles for language learning.
    *   **双语字幕**：可以生成用于语言学习的双语字幕。
*   **Embedded Subtitle Extraction**: Can detect and extract existing subtitle tracks from video files.
    *   **内嵌字幕提取**：可以检测并提取视频文件中的现有字幕轨道。
*   **Internationalization**: Supports multiple languages for the user interface (currently English and Chinese).
    *   **国际化**：用户界面支持多种语言（目前支持英文和中文）。
*   **User-friendly CLI**: Provides a clear and easy-to-use command-line interface with subcommands.
    *   **友好的命令行界面**：提供清晰易用的、带子命令的命令行界面。

## Installation / 安装

1.  **Clone the repository / 克隆仓库**

    ```bash
    git clone <your-repo-url>
    cd subtitle
    ```

2.  **Install dependencies / 安装依赖**

    It is recommended to use a virtual environment:
    建议在虚拟环境中使用：

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate` / 在 Windows 上使用 `venv\Scripts\activate`
    ```

    Then install the required packages:
    然后安装所需的包：

    ```bash
    pip install -r requirements.txt
    ```
    
    Alternatively, install using `setup.py`, which will handle dependencies and set up the command-line entry point:
    或者，使用 `setup.py` 进行安装，这将自动处理依赖并设置命令行入口：
    
    ```bash
    pip install .
    ```

3.  **Install ffmpeg / 安装 ffmpeg**

    Whisper requires `ffmpeg` to process audio. Make sure it is installed on your system.
    Whisper 需要 `ffmpeg` 来处理音频。请确保你的系统上已经安装了它。

    *   **On macOS (using Homebrew):**
    *   **在 macOS 上 (使用 Homebrew):**
        ```bash
        brew install ffmpeg
        ```
    *   **On Debian/Ubuntu:**
    *   **在 Debian/Ubuntu 上:**
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```
    *   **On Windows (using Chocolatey):**
    *   **在 Windows 上 (使用 Chocolatey):**
        ```bash
        choco install ffmpeg
        ```

## Usage / 使用方法

After installation, you can use the `ai-subtitle` command.
安装完成后，你可以使用 `ai-subtitle` 命令。

```bash
ai-subtitle <command> [options]
```

### Global Options / 全局选项
*   `--language {en,zh}`: Sets the display language for the tool. Defaults to your system's language.
    *   `--language {en,zh}`: 设置工具的显示语言。默认为您的系统语言。

### Commands / 命令

#### `transcribe`
Transcribes an audio/video file to an SRT file.
将音频/视频文件转录为 SRT 文件。

**Usage / 用法:**
`ai-subtitle transcribe <input_file> [options]`

**Arguments / 参数:**
*   `input_file`: Path to the input video or audio file.
    *   `input_file`: 输入视频或音频文件的路径。

**Options / 选项:**
*   `-o, --output`: Path to the output SRT file. If not specified, prints to standard output.
    *   `-o, --output`: 输出 SRT 文件的路径。如果未指定，则打印到标准输出。
*   `-m, --model`: The Whisper model to use (e.g., `tiny`, `base`, `small`, `medium`, `large`). Default is `base`.
    *   `-m, --model`: 要使用的 Whisper 模型（例如：`tiny`、`base`、`small`、`medium`、`large`）。默认为 `base`。
*   `--force-transcribe`: Force transcription even if embedded subtitles are found.
    *   `--force-transcribe`: 即使找到内嵌字幕也强制转录。

**Example / 示例:**
```bash
# Transcribe a video and save to a file / 转录视频并保存到文件
ai-subtitle transcribe my_video.mp4 -o my_video.srt

# Extract an embedded subtitle instead of transcribing / 提取内嵌字幕而不是转录
ai-subtitle transcribe my_movie.mkv -o movie_subs.srt
```

#### `translate`
Translates an existing SRT file into a bilingual SRT file.
将现有的 SRT 文件翻译成双语 SRT 文件。

**Usage / 用法:**
`ai-subtitle translate [input_file] [options]`

**Arguments / 参数:**
*   `input_file`: Path to the input SRT file. Reads from standard input if not provided.
    *   `input_file`: 输入 SRT 文件的路径。如果未提供，则从标准输入读取。

**Options / 选项:**
*   `-o, --output`: Path to the output bilingual SRT file. Prints to standard output if not specified.
    *   `-o, --output`: 输出双语 SRT 文件的路径。如果未指定，则打印到标准输出。
*   `-t, --target-language`: The target language for translation (e.g., "Chinese", "English"). Default is "Chinese".
    *   `-t, --target-language`: 翻译的目标语言（例如："Chinese", "English"）。默认为 "Chinese"。
*   `--api-base-url`: Custom base URL for the LLM provider.
    *   `--api-base-url`: LLM 提供商的自定义基础 URL。
*   `--api-key`: Custom API key for the LLM provider.
    *   `--api-key`: LLM 提供商的自定义 API 密钥。

**Example / 示例:**
```bash
# Transcribe and then translate / 先转录再翻译
ai-subtitle transcribe my_video.mp4 | ai-subtitle translate -t "Japanese" -o bilingual.srt
```

## How It Works / 工作原理

1.  **Audio Extraction/Transcription**: For the `transcribe` command, it either extracts existing subtitles or uses `ffmpeg` to extract audio and `whisper` to transcribe it into timed text segments.
    *   **音频提取/转录**：对于 `transcribe` 命令，它会先尝试提取现有字幕，或者使用 `ffmpeg` 提取音频，然后使用 `whisper` 将其转录为带时间戳的文本段落。
2.  **Chunking & Translation**: For the `translate` command, it reads an SRT file, chunks the text to fit the LLM's context window, and sends it for translation.
    *   **分块与翻译**：对于 `translate` 命令，它会读取一个 SRT 文件，将文本分块以适应 LLM 的上下文窗口，然后发送进行翻译。
3.  **LLM Processing**: The text is sent to the configured LLM for translation and refinement. The process includes retries and a progress bar.
    *   **LLM 处理**：文本被发送到配置好的 LLM 进行翻译和优化。该过程包括重试和进度条。
4.  **SRT Generation**: The final processed text is formatted into a standard `.srt` file, either as a simple transcription or a bilingual subtitle.
    *   **SRT 生成**：最终处理后的文本被格式化为标准的 `.srt` 文件，可以是简单的转录稿或双语字幕。
