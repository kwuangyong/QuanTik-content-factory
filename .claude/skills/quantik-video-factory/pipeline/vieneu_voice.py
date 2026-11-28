"""Local VieNeu-TTS narration shared by the two video pipelines."""
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path


VOICE = "Phạm Tuyên"
LABEL = f"VieNeu-TTS · {VOICE} (nam miền Bắc)"


@lru_cache(maxsize=1)
def _model():
    try:
        from vieneu import Vieneu
    except ModuleNotFoundError as exc:
        if exc.name != "vieneu":
            raise
        raise RuntimeError("Cài VieNeu-TTS bằng: python -m pip install vieneu==3.8.5") from exc
    model = Vieneu(mode="v3turbo", device="cpu", backend="onnx")
    return model, model.get_preset_voice(VOICE)


def speak(text, destination):
    model, voice = _model()
    waveform = model.infer(text, voice=voice)
    if not waveform.size or not waveform.any():
        raise RuntimeError(f"{LABEL} không tạo được âm thanh")
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / "voice.wav"
        model.save(waveform, source)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(source),
             "-ac", "1", "-ar", "44100", str(destination)],
            check=True,
        )
