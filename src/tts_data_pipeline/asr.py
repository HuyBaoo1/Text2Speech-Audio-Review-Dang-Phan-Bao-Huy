from __future__ import annotations

import os
from functools import lru_cache
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from transformers import Pipeline


@lru_cache(maxsize=4)
def _load_whisper_pipeline(model_name: str = "openai/whisper-small") -> "Pipeline":
    from transformers import pipeline

    return pipeline("automatic-speech-recognition", model=model_name, chunk_length_s=30)


def transcribe_whisper_local(audio_path: str, model_name: str = "openai/whisper-small") -> str:
    recognizer = _load_whisper_pipeline(model_name)
    output = recognizer(audio_path)
    return output.get("text", "").strip()


def transcribe_openai_api(
    audio_path: str,
    openai_api_key: Optional[str] = None,
    model: str = "gpt-4o-mini-transcribe",
) -> str:
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(file=audio_file, model=model)
    return transcription.text.strip()


def compare_transcriptions(reference: str, hypothesis: str) -> Dict[str, float | str]:
    from jiwer import cer, wer

    return {
        "wer": float(wer(reference, hypothesis)),
        "cer": float(cer(reference, hypothesis)),
        "reference": reference,
        "hypothesis": hypothesis,
    }
