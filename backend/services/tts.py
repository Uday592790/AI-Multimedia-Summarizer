import os
from gtts import gTTS
from pathlib import Path
from fastapi import HTTPException
import uuid


class TTSService:
    """Generate text-to-speech audio files using gTTS."""

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "ur": "Urdu"
    }

    def __init__(self, output_dir: Path):
        """
        Initialize the TTS service.

        Args:
            output_dir: Directory to save generated audio files
        """
        self.output_dir = output_dir

    async def generate(
        self,
        text: str,
        language: str = "en",
        slow: bool = False
    ) -> Path:
        """
        Generate text-to-speech audio file.

        Args:
            text: Text to convert to speech
            language: Language code (en, hi, ta, etc.)
            slow: Whether to generate slow speech

        Returns:
            Path to generated audio file
        """
        try:
            if not text:
                raise HTTPException(
                    status_code=400,
                    detail="Text cannot be empty"
                )

            if language not in self.SUPPORTED_LANGUAGES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported language: {language}. "
                           f"Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}"
                )

            tts = gTTS(text=text, lang=language, slow=slow)

            filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = self.output_dir / filename

            tts.save(str(audio_path))

            return audio_path

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"TTS generation failed: {str(e)}"
            )

    async def generate_multiple(
        self,
        text: str,
        languages: list
    ) -> dict:
        """
        Generate TTS audio in multiple languages.

        Args:
            text: Text to convert to speech
            languages: List of language codes

        Returns:
            Dictionary with language codes as keys and audio paths as values
        """
        audio_files = {}

        for lang in languages:
            try:
                audio_path = await self.generate(text, lang)
                audio_files[lang] = str(audio_path)
            except Exception as e:
                audio_files[lang] = f"Generation failed: {str(e)}"

        return audio_files

    def get_supported_languages(self) -> dict:
        """Get list of supported languages for TTS."""
        return self.SUPPORTED_LANGUAGES

    async def generate_with_chunks(
        self,
        text: str,
        language: str = "en",
        max_chunk_length: int = 5000
    ) -> Path:
        """
        Generate TTS for long text by chunking.

        Args:
            text: Text to convert to speech
            language: Language code
            max_chunk_length: Maximum characters per chunk

        Returns:
            Path to combined audio file
        """
        if len(text) <= max_chunk_length:
            return await self.generate(text, language)

        from pydub import AudioSegment

        ffmpeg_dir = Path(__file__).resolve().parent.parent / "ffmpeg" / "bin"
        if ffmpeg_dir.exists():
            ffmpeg_path = ffmpeg_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
            ffprobe_path = ffmpeg_dir / ("ffprobe.exe" if os.name == "nt" else "ffprobe")
            AudioSegment.converter = str(ffmpeg_path)
            AudioSegment.ffmpeg = str(ffmpeg_path)
            AudioSegment.ffprobe = str(ffprobe_path)

        chunks = self._chunk_text(text, max_chunk_length)
        audio_segments = []

        for chunk in chunks:
            chunk_path = await self.generate(chunk, language)
            audio = AudioSegment.from_mp3(str(chunk_path))
            audio_segments.append(audio)

        combined = sum(audio_segments)

        filename = f"tts_combined_{uuid.uuid4().hex[:8]}.mp3"
        output_path = self.output_dir / filename

        combined.export(str(output_path), format="mp3")

        return output_path

    def _chunk_text(self, text: str, max_length: int) -> list:
        """
        Split text into chunks.

        Args:
            text: Text to chunk
            max_length: Maximum length per chunk

        Returns:
            List of text chunks
        """
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
