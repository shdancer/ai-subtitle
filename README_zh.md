
# AI 智能字幕助手

这是一个使用 AI 技术（Whisper 和大型语言模型）为视频和音频文件生成高质量字幕的命令行工具。

## 功能

*   **多格式支持**：处理各种常见的视频和音频文件格式。
*   **高精度语音识别**：使用 OpenAI 的 Whisper 模型进行准确的音频转录。
*   **智能翻译与校正**：利用大型语言模型（LLM）进行翻译，并根据上下文修正错误、识别专有名词。
*   **灵活的 LLM 配置**：允许用户自定义 LLM 提供商的 API 地址、密钥和模型。
*   **模型选择**：可以为翻译任务选择不同的 LLM 模型。
*   **并发翻译**：并发处理多个翻译请求，提高处理速度。
*   **翻译验证**：验证 LLM 返回的原文是否与输入原文一致，防止幻觉。
*   **改进的翻译质量**：调整重要性权重，更好地平衡准确性和流畅性（1:0.6）。
*   **上下文限制处理**：检测并警告模型上下文限制可能导致的输出截断问题。
*   **调试模式**：启用中间 JSON 数据的详细输出，用于故障排除。
*   **标准字幕输出**：生成通用的 UTF-8 编码的 SRT 字幕文件。
*   **双语字幕**：可以生成用于语言学习的双语字幕。
*   **内嵌字幕提取**：可以检测并提取视频文件中的现有字幕轨道。
*   **国际化**：用户界面支持多种语言（目前支持英文和中文）。
*   **友好的命令行界面**：提供清晰易用的、带子命令的命令行界面。

## 安装

**推荐方式：从 PyPI 安装**
```bash
pip install ai-subtitle
```

**或从源码安装：**
```bash
git clone https://github.com/shdancer/ai-subtitle
cd subtitle
python3 -m venv venv
source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
pip install .
```

**ffmpeg 必须安装，用于音频处理。**
*   **macOS (Homebrew):**
    ```bash
    brew install ffmpeg
    ```
*   **Debian/Ubuntu:**
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```
*   **Windows (Chocolatey):**
    ```bash
    choco install ffmpeg
    ```

## 使用方法

安装完成后，你可以使用 `ai-subtitle` 命令。

```bash
ai-subtitle <command> [options]
```

### 全局选项
*   `--language {en,zh}`: 设置工具的显示语言。默认为您的系统语言。

### 命令

#### `transcribe`
将音频/视频文件转录为 SRT 文件。

**用法:**
`ai-subtitle transcribe <input_file> [options]`

**参数:**
*   `input_file`: 输入视频或音频文件的路径。

**选项:**
*   `-o, --output`: 输出 SRT 文件的路径。如果未指定，则打印到标准输出。
*   `-m, --model`: 要使用的 Whisper 模型（例如：`tiny`、`base`、`small`、`medium`、`large`）。默认为 `base`。
*   `--force-transcribe`: 即使找到内嵌字幕也强制转录。

**示例:**
```bash
# 转录视频并保存到文件
ai-subtitle transcribe my_video.mp4 -o my_video.srt

# 提取内嵌字幕而不是转录
ai-subtitle transcribe my_movie.mkv -o movie_subs.srt
```

#### `translate`
将现有的 SRT 文件翻译成双语 SRT 文件。

**用法:**
`ai-subtitle translate [input_file] [options]`

**参数:**
*   `input_file`: 输入 SRT 文件的路径。如果未提供，则从标准输入读取。

**选项:**
*   `-o, --output`: 输出双语 SRT 文件的路径。如果未指定，则打印到标准输出。
*   `-t, --target-language`: 翻译的目标语言（例如："Chinese", "English"）。默认为 "Chinese"。
*   `--model`: 选择用于翻译的模型（例如："gpt-3.5-turbo", "gpt-4"）。默认为 "gpt-3.5-turbo"。
*   `--max-workers`: 最大并发翻译请求数。默认为 5。
*   `--list-models`: 列出 API 提供的可用模型并退出。
*   `--api-base-url`: LLM 提供商的自定义基础 URL。
*   `--api-key`: LLM 提供商的自定义 API 密钥。

**示例:**
```bash
# 先转录再翻译
ai-subtitle transcribe my_video.mp4 | ai-subtitle translate -t "Japanese" -o bilingual.srt
```

#### `config`
管理 AI 字幕助手的配置设置。

**用法:**
`ai-subtitle config [options]`

**选项:**
*   `--show-path`: 显示配置文件路径。
*   `--create`: 交互式创建或更新配置。

**示例:**
```bash
# 显示配置文件路径
ai-subtitle config --show-path

# 创建或更新配置
ai-subtitle config --create
```

## 工作原理

1.  **音频提取/转录**：对于 `transcribe` 命令，它会先尝试提取现有字幕，或者使用 `ffmpeg` 提取音频，然后使用 `whisper` 将其转录为带时间戳的文本段落。
2.  **分块与翻译**：对于 `translate` 命令，它会读取一个 SRT 文件，将文本分块以适应 LLM 的上下文窗口，然后发送进行翻译。
3.  **LLM 处理**：文本被发送到配置好的 LLM 进行翻译和优化。该过程包括重试和进度条。
4.  **SRT 生成**：最终处理后的文本被格式化为标准的 `.srt` 文件，可以是简单的转录稿或双语字幕。

## 更新日志

### v0.1.4
- 新增：通过 `--model` 选项为翻译选择模型的功能
- 新增：通过 `--list-models` 选项列出可用模型
- 新增：用于故障排除翻译问题的调试模式（通过 `AI_SUBTITLE_DEBUG=1` 环境变量启用）
- 改进：翻译提示词，更好地处理不同语言结构，防止字幕错位
- 新增：键盘中断（Ctrl+C）的优雅退出处理
- 新增：检查缺失翻译的验证功能
- 新增：并发翻译处理，提高处理性能
- 新增：翻译验证，确保LLM返回的原文与输入原文一致
- 改进：通过调整重要性权重来提高翻译质量，更好地平衡准确性和流畅性（1:0.6）
- 新增：`--max-workers` 选项，用于控制并发翻译请求的数量
- 新增：上下文限制处理，检测并警告输出截断问题

### v0.1.2
- 修复：SRT 多行内容解析 bug，现已完整保留并正确翻译所有行
- 改进：文档结构和 README
- 更新：PyPI 安装说明和项目元数据

### v0.1.1
- 修复了管道操作中的问题，调试输出不再干扰标准输出
- 改进了错误处理和消息提示
- 更新了从PyPI安装的文档说明

### v0.1.0
- 初始版本，包含核心功能
