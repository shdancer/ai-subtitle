import whisper
from ai_subtitle_assistant.i18n import _
from colorama import Fore, Style, init

init(autoreset=True)


def transcribe(audio_file, model_name="base"):
    """
    Transcribes an audio file using Whisper.
    """
    print(
        Fore.BLUE
        + _("Loading Whisper model '{model_name}'...").format(model_name=model_name)
    )
    model = whisper.load_model(model_name)
    print(Fore.BLUE + _("Model loaded. Starting transcription..."))
    result = model.transcribe(audio_file, verbose=True)
    print(Fore.GREEN + _("Transcription finished."))
    return result
