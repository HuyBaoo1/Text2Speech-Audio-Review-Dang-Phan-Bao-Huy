from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np


AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".webm"}


@dataclass
class AudioSample:
    path: str
    duration: float
    sample_rate: int
    channels: int
    rms: float
    peak: float
    snr: Optional[float]
    silence_ratio: float
    clipping_ratio: float
    dc_offset: float
    pass_quality_gate: bool
    transcript: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


def scan_audio_files(folder: str, limit: Optional[int] = 100, extensions: Optional[Iterable[str]] = None) -> List[str]:
    allowed = {item.lower() for item in (extensions or AUDIO_EXTENSIONS)}
    paths: List[str] = []
    for root, _, files in os.walk(folder):
        for name in files:
            if Path(name).suffix.lower() in allowed:
                paths.append(str(Path(root) / name))
    paths = sorted(paths)
    return paths[:limit] if limit else paths


def load_audio(path: str, target_sr: int = 22050) -> Tuple[np.ndarray, int]:
    import librosa

    audio, sr = librosa.load(path, sr=target_sr, mono=False)
    return audio, sr


def compute_audio_metrics(audio: np.ndarray, sr: int) -> Dict[str, float]:
    if audio.ndim == 1:
        channels = 1
        channel_audio = [audio]
    else:
        channels = int(audio.shape[0])
        channel_audio = [audio[index] for index in range(channels)]

    def channel_stats(signal: np.ndarray) -> Dict[str, float]:
        abs_signal = np.abs(signal)
        rms = float(np.sqrt(np.mean(signal**2) + 1e-9))
        peak = float(np.max(abs_signal) + 1e-9)
        quiet = abs_signal[abs_signal < 0.001]
        noise_floor = float(np.mean(quiet) + 1e-9) if quiet.size else 1e-9
        snr = float(20 * np.log10(rms / noise_floor)) if noise_floor > 0 else 99.0
        return {
            "rms": rms,
            "peak": peak,
            "snr": snr,
            "silence_ratio": float(np.mean(abs_signal < 0.01)),
            "clipping_ratio": float(np.mean(abs_signal >= 0.999)),
            "dc_offset": float(np.mean(signal)),
        }

    stats = [channel_stats(channel) for channel in channel_audio]
    return {
        "duration": float(audio.shape[-1] / sr),
        "sample_rate": float(sr),
        "channels": float(channels),
        "rms": float(np.mean([item["rms"] for item in stats])),
        "peak": float(np.max([item["peak"] for item in stats])),
        "snr": float(np.mean([item["snr"] for item in stats])),
        "silence_ratio": float(np.mean([item["silence_ratio"] for item in stats])),
        "clipping_ratio": float(np.mean([item["clipping_ratio"] for item in stats])),
        "dc_offset": float(np.mean([item["dc_offset"] for item in stats])),
    }


def normalize_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").replace("\t", " ").strip().split())


def quality_filter(
    metrics: Dict[str, float],
    min_snr: float = 20.0,
    max_silence: float = 0.35,
    min_duration: float = 1.0,
    max_duration: float = 20.0,
    max_clipping_ratio: float = 0.001,
    max_abs_dc_offset: float = 0.02,
) -> bool:
    if metrics["duration"] < min_duration or metrics["duration"] > max_duration:
        return False
    if metrics["snr"] < min_snr:
        return False
    if metrics["silence_ratio"] > max_silence:
        return False
    if metrics["clipping_ratio"] > max_clipping_ratio:
        return False
    if abs(metrics["dc_offset"]) > max_abs_dc_offset:
        return False
    return True


def build_sample_record(path: str, target_sr: int = 22050) -> AudioSample:
    audio, sr = load_audio(path, target_sr=target_sr)
    metrics = compute_audio_metrics(audio, sr)
    return AudioSample(
        path=path,
        duration=metrics["duration"],
        sample_rate=int(metrics["sample_rate"]),
        channels=int(metrics["channels"]),
        rms=metrics["rms"],
        peak=metrics["peak"],
        snr=metrics["snr"],
        silence_ratio=metrics["silence_ratio"],
        clipping_ratio=metrics["clipping_ratio"],
        dc_offset=metrics["dc_offset"],
        pass_quality_gate=quality_filter(metrics),
        metadata={"source_file": Path(path).name},
    )


def inspect_samples(folder: str, limit: Optional[int] = 100, target_sr: int = 22050) -> List[AudioSample]:
    return [build_sample_record(path, target_sr=target_sr) for path in scan_audio_files(folder, limit=limit)]


def write_csv(path: str, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
