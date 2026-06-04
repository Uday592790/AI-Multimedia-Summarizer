import os
import shutil
from pathlib import Path
from typing import Dict
from fastapi import UploadFile, HTTPException

import pdfplumber
from langdetect import detect
from deep_translator import GoogleTranslator
import re


class FileHandler:
    """Handle file uploads and processing for various file types."""

    ALLOWED_EXTENSIONS = {
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
        'audio': ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg'],
        'pdf': ['.pdf'],
        'text': ['.txt']
    }

    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir

    async def process_upload(self, file: UploadFile) -> Dict:
        """Process uploaded file and return file info."""
        file_extension = Path(file.filename).suffix.lower()
        file_type = self._get_file_type(file_extension)

        if not file_type:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}"
            )

        file_path = self.input_dir / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = {
            "type": file_type,
            "path": file_path,
            "filename": file.filename
        }

        if file_type == "text":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            text = self._clean_text(text)
            # If not English, translate to English for downstream pipeline
            try:
                lang = detect(text[:500]) if text else "en"
                if text and lang != "en":
                    text = self._translate_to_en(text, lang)
            except Exception:
                # If detection fails, keep original
                pass
            result["text"] = text

        return result

    async def extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            # Try pdfplumber with OCR for images
            text = ""
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    if t:
                        text += t.strip() + " "
                    # Attempt OCR on page images
                    try:
                        if page.images:
                            from PIL import Image
                            import pytesseract
                            img = page.to_image(resolution=300)
                            ocr_text = pytesseract.image_to_string(img.original)
                            if ocr_text and ocr_text.strip():
                                text += ocr_text.strip() + " "
                    except Exception:
                        # OCR is best-effort; ignore errors
                        pass

            text = self._clean_text(text)
            if text:
                try:
                    lang = detect(text[:500])
                    if lang != "en":
                        text = self._translate_to_en(text, lang)
                except Exception:
                    pass
            return text.strip()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract PDF text: {str(e)}"
            )

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r'\s([?.!"](?:\s|$))', r"\1", text)
        text = re.sub(r"\n\s*\n", "\n", text)
        text = re.sub(r"Page \d+ of \d+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _translate_to_en(self, text: str, src_lang: str) -> str:
        # Chunk translation to avoid limits
        chunks = self._chunk_text(text, max_len=500)
        translated = [GoogleTranslator(source=src_lang, target="en").translate(c) for c in chunks]
        return " ".join(translated)

    def _chunk_text(self, txt: str, max_len: int = 500) -> list:
        words, cur, chunks = txt.split(), [], []
        for w in words:
            if sum(len(x) for x in cur) + len(cur) + len(w) > max_len:
                chunks.append(" ".join(cur))
                cur = []
            cur.append(w)
        if cur:
            chunks.append(" ".join(cur))
        return chunks

    def _get_file_type(self, extension: str) -> str:
        """Determine file type from extension."""
        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return file_type
        return None


