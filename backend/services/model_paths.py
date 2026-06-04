import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BACKEND_DIR / "models"
HF_HOME = MODELS_DIR / "huggingface"
HF_HUB_CACHE = HF_HOME / "hub"
TRANSFORMERS_CACHE = MODELS_DIR / "transformers"
SENTENCE_TRANSFORMERS_HOME = MODELS_DIR / "sentence-transformers"
TORCH_HOME = MODELS_DIR / "torch"
WHISPER_CACHE = MODELS_DIR / "faster-whisper"


def configure_model_cache_dirs() -> None:
    """Configure local model caches before ML libraries are imported."""
    defaults = {
        "HF_HOME": HF_HOME,
        "HF_HUB_CACHE": HF_HUB_CACHE,
        "SENTENCE_TRANSFORMERS_HOME": SENTENCE_TRANSFORMERS_HOME,
        "TORCH_HOME": TORCH_HOME,
    }

    for name, path in defaults.items():
        os.environ.setdefault(name, str(path))
        Path(os.environ[name]).mkdir(parents=True, exist_ok=True)

    WHISPER_CACHE.mkdir(parents=True, exist_ok=True)
    TRANSFORMERS_CACHE.mkdir(parents=True, exist_ok=True)
