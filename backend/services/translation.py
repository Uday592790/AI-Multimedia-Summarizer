from deep_translator import GoogleTranslator
from fastapi import HTTPException


class TranslationService:
    """Translate text to Indian languages using deep-translator."""

    SUPPORTED_LANGUAGES = {
        "hi": "hindi",
        "ta": "tamil",
        "te": "telugu",
        "bn": "bengali",
        "mr": "marathi",
        "gu": "gujarati",
        "kn": "kannada",
        "ml": "malayalam",
        "pa": "punjabi",
        "ur": "urdu",
        "or": "odia",
        "as": "assamese"
    }

    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en"
    ) -> str:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code (hi, ta, te, bn, etc.)
            source_language: Source language code (default: en)

        Returns:
            Translated text
        """
        try:
            if not text:
                raise HTTPException(
                    status_code=400,
                    detail="Text cannot be empty"
                )

            if target_language not in self.SUPPORTED_LANGUAGES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported language: {target_language}. "
                           f"Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}"
                )

            translator = GoogleTranslator(
                source=source_language,
                target=target_language
            )

            if len(text) > 5000:
                chunks = self._chunk_text(text, 5000)
                translations = []

                for chunk in chunks:
                    translation = translator.translate(chunk)
                    translations.append(translation)

                return " ".join(translations)
            else:
                translation = translator.translate(text)
                return translation

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Translation failed: {str(e)}"
            )

    async def translate_multiple(
        self,
        text: str,
        target_languages: list
    ) -> dict:
        """
        Translate text to multiple languages.

        Args:
            text: Text to translate
            target_languages: List of target language codes

        Returns:
            Dictionary with language codes as keys and translations as values
        """
        translations = {}

        for lang in target_languages:
            try:
                translation = await self.translate(text, lang)
                translations[lang] = translation
            except Exception as e:
                translations[lang] = f"Translation failed: {str(e)}"

        return translations

    def _chunk_text(self, text: str, max_length: int) -> list:
        """
        Split text into chunks for translation.

        Args:
            text: Text to chunk
            max_length: Maximum length of each chunk

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

    def get_supported_languages(self) -> dict:
        """Get list of supported Indian languages."""
        return self.SUPPORTED_LANGUAGES
