from __future__ import annotations

import base64
import os
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from transformers import Pipeline


@lru_cache(maxsize=4)
def _load_whisper_pipeline(model_name: str = "openai/whisper-small") -> "Pipeline":
    from transformers import pipeline

    return pipeline("automatic-speech-recognition", model=model_name, chunk_length_s=30)


def transcribe_whisper_local(audio_path: str, model_name: str = "openai/whisper-small") -> str:
    recognizer = _load_whisper_pipeline(model_name)
    import librosa

    audio, sample_rate = librosa.load(audio_path, sr=16000, mono=True)
    output = recognizer({"array": audio, "sampling_rate": sample_rate})
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


def transcribe_groq_api(
    audio_path: str,
    groq_api_key: Optional[str] = None,
    model: str = "whisper-large-v3-turbo",
) -> str:
    api_key = groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(file=audio_file, model=model)
    return transcription.text.strip()


def transcribe_deepgram_api(
    audio_path: str,
    deepgram_api_key: Optional[str] = None,
    model: str = "nova-3",
    language: Optional[str] = "vi",
) -> str:
    api_key = deepgram_api_key or os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY is not set.")

    import requests

    params = {"model": model, "smart_format": "true"}
    if language:
        params["language"] = language

    content_type = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
        ".ogg": "audio/ogg",
        ".webm": "audio/webm",
    }.get(Path(audio_path).suffix.lower(), "application/octet-stream")

    with open(audio_path, "rb") as audio_file:
        response = requests.post(
            "https://api.deepgram.com/v1/listen",
            params=params,
            headers={"Authorization": f"Token {api_key}", "Content-Type": content_type},
            data=audio_file,
            timeout=120,
        )
    response.raise_for_status()
    payload = response.json()
    alternatives = payload.get("results", {}).get("channels", [{}])[0].get("alternatives", [])
    if not alternatives:
        return ""
    return alternatives[0].get("transcript", "").strip()


def transcribe_gemini_api(
    audio_path: str,
    gemini_api_key: Optional[str] = None,
    model: str = "gemini-2.5-flash",
    language: Optional[str] = "Vietnamese",
) -> str:
    api_key = gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is not set.")

    import requests

    mime_type = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
        ".ogg": "audio/ogg",
        ".webm": "audio/webm",
    }.get(Path(audio_path).suffix.lower(), "application/octet-stream")
    audio_b64 = base64.b64encode(Path(audio_path).read_bytes()).decode("ascii")
    prompt_language = language or "Vietnamese"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            f"Transcribe this audio exactly in {prompt_language}. "
                            "Return only the transcript text. Do not summarize, translate, add timestamps, "
                            "or add explanations."
                        )
                    },
                    {"inline_data": {"mime_type": mime_type, "data": audio_b64}},
                ],
            }
        ],
        "generationConfig": {"temperature": 0},
    }
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        json=payload,
        timeout=180,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Gemini transcription failed with HTTP {response.status_code}: {response.text[:300]}")
    parts = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return " ".join(part.get("text", "") for part in parts).strip()


def transcribe_elevenlabs_api(
    audio_path: str,
    elevenlabs_api_key: Optional[str] = None,
    model: str = "scribe_v2",
    language: Optional[str] = "vie",
) -> str:
    api_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY or XI_API_KEY is not set.")

    import requests

    data = {"model_id": model}
    if language:
        data["language_code"] = language

    with open(audio_path, "rb") as audio_file:
        response = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={"xi-api-key": api_key},
            data=data,
            files={"file": (Path(audio_path).name, audio_file)},
            timeout=180,
        )
    response.raise_for_status()
    payload = response.json()
    return payload.get("text", "").strip()


def transcribe_azure_api(
    audio_path: str,
    azure_speech_key: Optional[str] = None,
    azure_speech_region: Optional[str] = None,
    model: str = "azure-short-audio",
    language: Optional[str] = "vi-VN",
) -> str:
    del model
    api_key = azure_speech_key or os.getenv("AZURE_SPEECH_KEY") or os.getenv("SPEECH_KEY")
    region = azure_speech_region or os.getenv("AZURE_SPEECH_REGION") or os.getenv("SPEECH_REGION")
    endpoint = os.getenv("AZURE_SPEECH_ENDPOINT") or os.getenv("SPEECH_ENDPOINT")
    if not api_key:
        raise ValueError("AZURE_SPEECH_KEY or SPEECH_KEY is not set.")
    if not region and not endpoint:
        raise ValueError("AZURE_SPEECH_REGION/SPEECH_REGION or AZURE_SPEECH_ENDPOINT/SPEECH_ENDPOINT is not set.")

    import requests

    base_url = endpoint.rstrip("/") if endpoint else f"https://{region}.stt.speech.microsoft.com"
    url = f"{base_url}/speech/recognition/conversation/cognitiveservices/v1"
    params = {"language": language or "vi-VN"}
    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Accept": "application/json",
        "Content-Type": "audio/wav; codecs=audio/pcm",
    }
    with open(audio_path, "rb") as audio_file:
        response = requests.post(url, params=params, headers=headers, data=audio_file, timeout=120)
    response.raise_for_status()
    payload = response.json()
    if payload.get("NBest"):
        return payload["NBest"][0].get("Display", "").strip()
    return payload.get("DisplayText", "").strip()


def compare_transcriptions(reference: str, hypothesis: str) -> Dict[str, float | str]:
    from jiwer import cer, wer

    return {
        "wer": float(wer(reference, hypothesis)),
        "cer": float(cer(reference, hypothesis)),
        "reference": reference,
        "hypothesis": hypothesis,
    }
