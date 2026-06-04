from pathlib import Path
import os
from fastapi import HTTPException
from services.model_paths import WHISPER_CACHE


class TranscriptionService:

    def __init__(self, model_size: str | None = None):
        """
        Initialize the transcription service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size or os.getenv("WHISPER_MODEL_SIZE", "base")
        self.model = None

    def _load_model(self):
        """Lazy load the Whisper model on CPU."""
        if self.model is None:
            try:
                print(f"Loading Whisper model '{self.model_size}'...", flush=True)
                os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
                os.environ.setdefault("OMP_NUM_THREADS", "1")
                os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

                from faster_whisper import WhisperModel

                device = "cpu"
                compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "float32")
                self.model = WhisperModel(
                    self.model_size,
                    device=device,
                    compute_type=compute_type,
                    download_root=str(WHISPER_CACHE),
                    cpu_threads=int(os.getenv("WHISPER_CPU_THREADS", "1")),
                    num_workers=1,
                )
                print(
                    f"Whisper model loaded on {device} with {compute_type}.",
                    flush=True,
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load Whisper model: {str(e)}"
                )

    async def transcribe(self, file_path: Path) -> str:
        """
        Transcribe audio/video file to text.

        Args:
            file_path: Path to the audio/video file

        Returns:
            Transcribed text
        """
        try:
            self._load_model()

            segments, info = self.model.transcribe(
                str(file_path),
                beam_size=1,
                language=None
            )

            texts = []
            for segment in segments:
                print(
                    f"Transcribed {segment.end:.1f}s: {segment.text.strip()}",
                    flush=True,
                )
                texts.append(segment.text)

            return " ".join(texts).strip()

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {str(e)}"
            )

    async def transcribe_with_timestamps(self, file_path: Path) -> list:
        """
        Transcribe with timestamp information.

        Returns:
            List of segments with text and timestamps
        """
        try:
            self._load_model()

            segments, info = self.model.transcribe(
                str(file_path),
                beam_size=1
            )

            result = []
            for segment in segments:
                result.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })

            return result

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription with timestamps failed: {str(e)}"
            )
