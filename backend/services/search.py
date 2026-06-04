from sentence_transformers import SentenceTransformer, util
import numpy as np
from fastapi import HTTPException
from services.model_paths import SENTENCE_TRANSFORMERS_HOME


class SemanticSearchService:
    """Perform semantic search on text using sentence transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic search service.

        Args:
            model_name: Sentence transformer model name
        """
        self.model_name = model_name
        self.model = None

    def _load_model(self):
        """Lazy load the sentence transformer model."""
        if self.model is None:
            try:
                self.model = SentenceTransformer(
                    self.model_name,
                    cache_folder=str(SENTENCE_TRANSFORMERS_HOME),
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load semantic search model: {str(e)}"
                )

    async def search(
        self,
        text: str,
        query: str,
        top_k: int = 5,
        chunk_size: int = 200
    ) -> list:
        """
        Perform semantic search on text.

        Args:
            text: Full text to search in
            query: Search query
            top_k: Number of top results to return
            chunk_size: Size of text chunks in words

        Returns:
            List of relevant text passages with scores
        """
        try:
            self._load_model()

            if not text or not query:
                raise HTTPException(
                    status_code=400,
                    detail="Both text and query are required"
                )

            chunks = self._chunk_text(text, chunk_size)

            if len(chunks) == 0:
                return []

            query_embedding = self.model.encode(query, convert_to_tensor=True)
            chunk_embeddings = self.model.encode(chunks, convert_to_tensor=True)

            similarities = util.pytorch_cos_sim(
                query_embedding,
                chunk_embeddings
            )[0]

            top_results = []
            top_indices = similarities.argsort(descending=True)[:top_k]

            for idx in top_indices:
                idx_val = idx.item()
                score = similarities[idx_val].item()

                top_results.append({
                    "text": chunks[idx_val],
                    "score": round(float(score), 4),
                    "chunk_index": idx_val
                })

            return top_results

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Semantic search failed: {str(e)}"
            )

    def _chunk_text(self, text: str, chunk_size: int) -> list:
        """
        Split text into chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in words

        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks

    async def find_similar_sentences(
        self,
        text: str,
        query: str,
        threshold: float = 0.5
    ) -> list:
        """
        Find sentences similar to query above a threshold.

        Args:
            text: Full text to search in
            query: Query text
            threshold: Minimum similarity score

        Returns:
            List of similar sentences with scores
        """
        try:
            self._load_model()

            sentences = [s.strip() for s in text.split('.') if s.strip()]

            if len(sentences) == 0:
                return []

            query_embedding = self.model.encode(query, convert_to_tensor=True)
            sentence_embeddings = self.model.encode(
                sentences,
                convert_to_tensor=True
            )

            similarities = util.pytorch_cos_sim(
                query_embedding,
                sentence_embeddings
            )[0]

            results = []
            for idx, score in enumerate(similarities):
                score_val = score.item()
                if score_val >= threshold:
                    results.append({
                        "sentence": sentences[idx],
                        "score": round(float(score_val), 4),
                        "index": idx
                    })

            results.sort(key=lambda x: x["score"], reverse=True)

            return results

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Similar sentence search failed: {str(e)}"
            )
