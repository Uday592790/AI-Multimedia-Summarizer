from bert_score import score
from fastapi import HTTPException
import numpy as np
from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize
from services.model_paths import SENTENCE_TRANSFORMERS_HOME


class EvaluationService:
    """Evaluate summary quality using BERTScore + Semantic alignment."""

    def __init__(self, model_type: str = "roberta-large"):
        """
        Initialize the evaluation service.
        """
        # BERT model
        self.model_type = model_type  
        self.embedder = None

    def _load_embedder(self):
        """Lazy load the sentence transformer model."""
        if self.embedder is None:
            try:
                self.embedder = SentenceTransformer(
                    "all-mpnet-base-v2",
                    cache_folder=str(SENTENCE_TRANSFORMERS_HOME),
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to load embedding model: {str(e)}"
                )

    async def evaluate(self, source_text: str, summary_text: str) -> dict:
        """Evaluate summary using BERTScore + semantic alignment."""
        try:
            self._load_embedder()
            
            if not source_text or not summary_text:
                raise HTTPException(
                    status_code=400,
                    detail="Both source and summary text are required"
                )

            #  BERTScore
            P, R, F1 = score(
                [summary_text],
                [source_text],
                lang="en",
                model_type=self.model_type,
                verbose=False
            )

            precision = float(P.mean().item())
            recall = float(R.mean().item())
            f1 = float(F1.mean().item())

            alignment = self._calculate_alignment(source_text, summary_text)

            overall_accuracy = (0.5 * alignment + 0.5 * f1) * 100

            metrics = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "sentence_alignment": alignment,
                "accuracy": round(overall_accuracy/100, 2),
                "compression_ratio": len(summary_text.split()) / max(1, len(source_text.split())),
                "summary_length": len(summary_text.split()),
                "source_length": len(source_text.split()),
            }

            metrics["overall_quality"] = self._calculate_quality_score(metrics)

            return metrics

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Evaluation failed: {str(e)}"
            )

    def _calculate_alignment(self, source: str, summary: str) -> float:
        """Colab-style semantic sentence alignment using cosine similarity."""
        source_sents = sent_tokenize(source)
        summary_sents = sent_tokenize(summary)

        if not source_sents or not summary_sents:
            return 0.0

        src_emb = self.embedder.encode(source_sents, convert_to_tensor=True, normalize_embeddings=True)
        sum_emb = self.embedder.encode(summary_sents, convert_to_tensor=True, normalize_embeddings=True)

        cosine_scores = util.cos_sim(sum_emb, src_emb)

        best_scores = [float(cosine_scores[i].max()) for i in range(len(summary_sents))]

        return round(float(np.mean(best_scores)), 4)

    def _calculate_quality_score(self, metrics: dict) -> str:
        """Quality rating based on BERTScore F1."""
        f1 = metrics["f1_score"]

        if f1 >= 0.8:
            return "Excellent"
        elif f1 >= 0.6:
            return "Good"
        elif f1 >= 0.4:
            return "Fair"
        else:
            return "Poor"

    async def batch_evaluate(self, source_texts: list, summary_texts: list) -> list:
        """Batch evaluate multiple summaries."""
        if len(source_texts) != len(summary_texts):
            raise HTTPException(
                status_code=400,
                detail="Source and summary lists must have the same length"
            )

        results = []
        for source, summary in zip(source_texts, summary_texts):
            metrics = await self.evaluate(source, summary)
            results.append(metrics)

        return results
