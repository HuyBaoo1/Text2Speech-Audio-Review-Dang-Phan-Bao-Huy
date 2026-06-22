from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import os
import time
import wave
from email.utils import formatdate
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional
from urllib.parse import urlencode, urlparse

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


def transcribe_openai_realtime_api(
    audio_path: str,
    openai_api_key: Optional[str] = None,
    model: str = "gpt-realtime-2",
    language: Optional[str] = "vi",
) -> str:
    """Ask a Realtime model to return a verbatim transcript for one audio file.

    Realtime models are not accepted by ``/audio/transcriptions``.  This adapter
    sends PCM16 audio over a dedicated WebSocket session and collects the text
    response.  It deliberately creates one session per file: that makes a
    stopped benchmark safely resumable from its per-file checkpoint.
    """
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    import websocket
    import librosa
    import numpy as np

    audio, _ = librosa.load(audio_path, sr=24000, mono=True)
    pcm16 = (np.clip(audio, -1.0, 1.0) * 32767.0).astype("<i2").tobytes()
    url = f"wss://api.openai.com/v1/realtime?model={model}"
    ws = websocket.create_connection(
        url,
        # The Realtime API is GA; sending the retired beta header is rejected.
        header=[f"Authorization: Bearer {api_key}"],
        timeout=180,
    )
    prompt_language = language or "the audio's original language"
    instruction = (
        f"Transcribe the input audio verbatim in {prompt_language}. "
        "Return only the transcript; do not translate, summarize, or add commentary."
    )
    text_parts: list[str] = []
    try:
        ws.send(
            json.dumps(
                {
                    "type": "session.update",
                    "session": {
                        "type": "realtime",
                        "output_modalities": ["text"],
                        "instructions": instruction,
                        "audio": {
                            "input": {
                                "format": {"type": "audio/pcm", "rate": 24000},
                                "turn_detection": None,
                            }
                        },
                    },
                }
            )
        )
        # Do not append audio until the server confirms the GA session settings.
        # Otherwise the first buffer can be interpreted with the default format.
        while True:
            event = json.loads(ws.recv())
            event_type = event.get("type", "")
            if event_type == "session.updated":
                break
            if event_type == "error":
                error = event.get("error", {})
                raise RuntimeError(f"OpenAI Realtime failed: {error.get('message', error)}")
        # Keep events comfortably below the Realtime event-size limit.
        for offset in range(0, len(pcm16), 24_000):
            ws.send(
                json.dumps(
                    {
                        "type": "input_audio_buffer.append",
                        "audio": base64.b64encode(pcm16[offset : offset + 24_000]).decode("ascii"),
                    }
                )
            )
        ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        ws.send(
            json.dumps(
                {
                    "type": "response.create",
                    "response": {"output_modalities": ["text"], "instructions": instruction},
                }
            )
        )

        while True:
            event = json.loads(ws.recv())
            event_type = event.get("type", "")
            if event_type in {"response.output_text.delta", "response.text.delta"}:
                text_parts.append(event.get("delta", ""))
            elif event_type == "error":
                error = event.get("error", {})
                raise RuntimeError(f"OpenAI Realtime failed: {error.get('message', error)}")
            elif event_type in {"response.done", "response.completed"}:
                break
    finally:
        ws.close()

    return "".join(text_parts).strip()


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
    api_key = (elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY") or os.getenv("XI_API_KEY") or "").strip()
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
    if response.status_code >= 400:
        raise RuntimeError(f"ElevenLabs transcription failed with HTTP {response.status_code}: {response.text[:300]}")
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
        "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
    }
    audio_payload = _audio_to_wav_pcm16_16k_mono(audio_path)
    response = requests.post(url, params=params, headers=headers, data=audio_payload, timeout=120)
    if response.status_code >= 400:
        raise RuntimeError(f"Azure transcription failed with HTTP {response.status_code}: {response.text[:300]}")
    payload = response.json()
    if payload.get("NBest"):
        return payload["NBest"][0].get("Display", "").strip()
    return payload.get("DisplayText", "").strip()


def _iflytek_auth_url(host_url: str, api_key: str, api_secret: str) -> str:
    parsed = urlparse(host_url)
    request_line = f"GET {parsed.path} HTTP/1.1"
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    signature_origin = f"host: {parsed.netloc}\ndate: {date}\n{request_line}"
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature = base64.b64encode(signature_sha).decode("utf-8")
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    params = {
        "authorization": base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8"),
        "date": date,
        "host": parsed.netloc,
    }
    return f"{host_url}?{urlencode(params)}"


def _audio_to_pcm16_16k_mono(audio_path: str) -> bytes:
    import librosa
    import numpy as np

    audio, _ = librosa.load(audio_path, sr=16000, mono=True)
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767.0).astype("<i2").tobytes()


def _audio_to_wav_pcm16_16k_mono(audio_path: str) -> bytes:
    """Normalise input before Azure's short-audio endpoint validates it."""
    pcm_audio = _audio_to_pcm16_16k_mono(audio_path)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(pcm_audio)
    return buffer.getvalue()


def _extract_iflytek_text(payload: dict[str, object], join_with_space: bool) -> str:
    result = payload.get("data", {}).get("result", {})  # type: ignore[union-attr]
    words = result.get("ws", []) if isinstance(result, dict) else []
    parts: list[str] = []
    for word in words:
        if not isinstance(word, dict):
            continue
        candidates = word.get("cw", [])
        if isinstance(candidates, list) and candidates:
            first = candidates[0]
            if isinstance(first, dict):
                parts.append(str(first.get("w", "")))
    return (" " if join_with_space else "").join(parts)


def transcribe_iflytek_api(
    audio_path: str,
    iflytek_app_id: Optional[str] = None,
    iflytek_api_key: Optional[str] = None,
    iflytek_api_secret: Optional[str] = None,
    model: str = "iat-niche",
    language: Optional[str] = "vi",
) -> str:
    app_id = (iflytek_app_id or os.getenv("IFLYTEK_APP_ID") or "").strip()
    api_key = (iflytek_api_key or os.getenv("IFLYTEK_API_KEY") or "").strip()
    api_secret = (iflytek_api_secret or os.getenv("IFLYTEK_API_SECRET") or "").strip()
    if not app_id or not api_key or not api_secret:
        raise ValueError("IFLYTEK_APP_ID, IFLYTEK_API_KEY, and IFLYTEK_API_SECRET must be set.")

    import websocket

    chosen_language = (language or os.getenv("IFLYTEK_LANGUAGE") or "vi").strip()
    endpoint = (os.getenv("IFLYTEK_HOST_URL") or "").strip()
    if not endpoint:
        endpoint = "wss://iat-niche-api.xfyun.cn/v2/iat" if chosen_language not in {"zh_cn", "en_us", "en"} else "wss://iat-api.xfyun.cn/v2/iat"

    business = {
        "domain": "iat",
        "language": chosen_language,
    }
    if chosen_language == "zh_cn":
        business["accent"] = os.getenv("IFLYTEK_ACCENT", "mandarin")

    pcm_audio = _audio_to_pcm16_16k_mono(audio_path)
    if len(pcm_audio) > 16000 * 2 * 60:
        raise ValueError("iFLYTEK iat supports audio up to 60 seconds.")

    auth_url = _iflytek_auth_url(endpoint, api_key, api_secret)
    ws = websocket.create_connection(auth_url, timeout=180)
    chunks = [pcm_audio[index : index + 1280] for index in range(0, len(pcm_audio), 1280)]
    transcript_parts: list[str] = []
    try:
        for index, chunk in enumerate(chunks):
            status = 0 if index == 0 else 1
            payload = {
                "data": {
                    "status": status,
                    "format": "audio/L16;rate=16000",
                    "encoding": "raw",
                    "audio": base64.b64encode(chunk).decode("utf-8"),
                }
            }
            if index == 0:
                payload["common"] = {"app_id": app_id}
                payload["business"] = business
            ws.send(json.dumps(payload, ensure_ascii=False))
            time.sleep(0.04)

        ws.send(json.dumps({"data": {"status": 2}}, ensure_ascii=False))
        while True:
            message = ws.recv()
            if not message:
                break
            payload = json.loads(message)
            code = int(payload.get("code", 0))
            if code != 0:
                raise RuntimeError(f"iFLYTEK transcription failed with code {code}: {payload.get('message', '')}")
            text = _extract_iflytek_text(payload, join_with_space=chosen_language != "zh_cn")
            if text:
                transcript_parts.append(text)
            data = payload.get("data", {})
            if isinstance(data, dict) and data.get("status") == 2:
                break
    finally:
        ws.close()

    return (" " if chosen_language != "zh_cn" else "").join(transcript_parts).strip()


def compare_transcriptions(reference: str, hypothesis: str) -> Dict[str, float | str]:
    from jiwer import cer, wer

    return {
        "wer": float(wer(reference, hypothesis)),
        "cer": float(cer(reference, hypothesis)),
        "reference": reference,
        "hypothesis": hypothesis,
    }
