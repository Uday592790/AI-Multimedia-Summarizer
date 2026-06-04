import re

from fastapi import HTTPException
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

from services.model_paths import SENTENCE_TRANSFORMERS_HOME, TRANSFORMERS_CACHE


class SummarizationService:
    """Summarize text using BART with filler removal and deduplication."""

    FILLER_PATTERNS = [
        r"\bthanks?( everyone| all)?\b",
        r"\bthank you( so much| very much)?\b",
        r"\bthat(\'s| is) (all|it)( for (today|now))?\b",
        r"\bin conclusion\b",
        r"\bto sum up\b",
        r"\bto summarize\b",
        r"\bin summary\b",
        r"\bplease (like|subscribe|share|follow|comment)\b",
        r"\bdon\'t forget to (like|subscribe|share)\b",
        r"\bmake sure to (check out|follow|subscribe)\b",
        r"\bin this (video|course|lesson|tutorial|paper|article|document)\b",
        r"\btoday (we )?(will )?(be )?(learn|discuss|talk about|cover)\b",
        r"\bwe (will|\'ll) (be )?(learn|cover|discuss|talk about)\b",
        r"\bwelcome (to|back|everyone)\b",
        r"\bthis (report|paper|presentation|chapter) (is|will be) about\b",
        r"\bso (yeah|uh|okay|alright)\b",
        r"\bum+\b|\buh+\b|\boh+\b",
        r"\byou know\b",
        r"\bi mean\b",
        r"\bkind of\b",
        r"\bsort of\b",
        r"\bokay so\b",
        r"\ball right\b",
        r"\blet(\'s)? get started\b",
        r"\band that\'s how (it|this) (works|is done)\b",
        r"\bas you can see\b",
        r"\bas I mentioned (earlier|before)\b",
        r"^\W*$",
    ]

    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.model_name = model_name
        self._summarizer = None
        self._embedder = None

    def _load_models(self):
        """Lazy load summarization pipeline and sentence embedder."""
        try:
            if self._summarizer is None:
                device = -1
                try:
                    import torch

                    device = 0 if torch.cuda.is_available() else -1
                except Exception:
                    pass

                tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    cache_dir=str(TRANSFORMERS_CACHE),
                )
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    cache_dir=str(TRANSFORMERS_CACHE),
                )
                self._summarizer = pipeline(
                    "summarization",
                    model=model,
                    tokenizer=tokenizer,
                    device=device,
                )

            if self._embedder is None:
                self._embedder = SentenceTransformer(
                    "all-MiniLM-L6-v2",
                    cache_folder=str(SENTENCE_TRANSFORMERS_HOME),
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load summarization components: {str(e)}",
            )

    def _filter_filler_sentences(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        cleaned = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) <= 5:
                continue
            if any(re.search(pattern, sentence.lower()) for pattern in self.FILLER_PATTERNS):
                continue
            cleaned.append(sentence)
        return " ".join(cleaned)

    async def summarize(
        self,
        text: str,
        max_length: int = 130,
        min_length: int = 60,
        chunk_size: int = 1024,
        overlap: int = 150,
        dedup_threshold: float = 0.85,
    ) -> str:
        """Summarize text in chunks, then remove filler and duplicate sentences."""
        try:
            self._load_models()

            text = text.strip()
            if not text:
                raise HTTPException(status_code=400, detail="Input text cannot be empty")

            step = max(1, chunk_size - overlap)
            chunks = [text[i:i + chunk_size] for i in range(0, len(text), step)]
            chunk_summaries = self._summarizer(
                chunks,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
            )
            summary_text = " ".join(item["summary_text"] for item in chunk_summaries)
            summary_text = self._filter_filler_sentences(summary_text)

            sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", summary_text)
                if len(sentence.strip()) > 10
            ]
            if not sentences:
                return summary_text

            embeddings = self._embedder.encode(
                sentences,
                convert_to_tensor=True,
                normalize_embeddings=True,
            )

            import torch

            kept = []
            kept_embeddings = []
            for index, sentence in enumerate(sentences):
                embedding = embeddings[index]
                if kept_embeddings:
                    kept_tensor = torch.stack(kept_embeddings)
                    similarities = util.cos_sim(embedding, kept_tensor)[0]
                    if similarities.max().item() > dedup_threshold:
                        continue

                kept.append(sentence)
                kept_embeddings.append(embedding)

            return " ".join(kept) if kept else summary_text

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {str(e)}",
            )

    async def summarize_long_text(
        self,
        text: str,
        chunk_size: int = 1024,
        max_length: int = 130,
        min_length: int = 60,
    ) -> str:
        return await self.summarize(
            text,
            max_length=max_length,
            min_length=min_length,
            chunk_size=chunk_size,
        )
