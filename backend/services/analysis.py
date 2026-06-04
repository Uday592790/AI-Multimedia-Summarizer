# Backend analysis utilities (LDA comparison)
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
from nltk.tokenize import sent_tokenize


def lda_compare_full_summary_image(full_text: str, summary_text: str, n_topics: int = 5, top_words: int = 5) -> bytes:
    """Generate a PNG image comparing topic distributions between full_text and summary_text.

    Returns PNG image bytes.
    """
    # Tokenize into sentences; fall back to raw text if tokenization fails
    full_sentences = sent_tokenize(full_text) if full_text and isinstance(full_text, str) else []
    summary_sentences = sent_tokenize(summary_text) if summary_text and isinstance(summary_text, str) else []

    if len(full_sentences) == 0 and full_text:
        full_sentences = [full_text]
    if len(summary_sentences) == 0 and summary_text:
        summary_sentences = [summary_text]

    # If there's effectively no content, return a simple PNG explaining the issue
    if (not full_sentences or all(len(s.strip()) == 0 for s in full_sentences)) and (
        not summary_sentences or all(len(s.strip()) == 0 for s in summary_sentences)
    ):
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, "Insufficient content for LDA", ha="center", va="center", fontsize=12)
        ax.axis('off')
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    # Try vectorization with a stricter min_df, then relax if necessary
    vectorizer = None
    X_full = None
    for min_df in (2, 1, 0):
        try:
            # min_df=0 is acceptable to CountVectorizer (interpreted as 0.0), but keep 1 as min count
            actual_min_df = min_df if min_df > 0 else 1
            vectorizer = CountVectorizer(max_df=0.95, min_df=actual_min_df, stop_words="english")
            X_full = vectorizer.fit_transform(full_sentences)
            # If vocabulary is empty or matrix has zero features, try a less strict pass
            if X_full.shape[1] == 0:
                continue
            break
        except Exception:
            vectorizer = None
            X_full = None
            continue

    if vectorizer is None or X_full is None or X_full.shape[1] == 0:
        # Create fallback image explaining failure
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, "LDA failed: insufficient vocabulary", ha="center", va="center", fontsize=12)
        ax.axis('off')
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    # Fit LDA with at most as many components as features
    n_components = min(n_topics, max(1, X_full.shape[1]))
    try:
        lda = LatentDirichletAllocation(n_components=n_components, random_state=42)
        lda.fit(X_full)
    except Exception:
        # If fitting fails, return a descriptive image instead of raising
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.text(0.5, 0.5, "LDA fitting failed", ha="center", va="center", fontsize=12)
        ax.axis('off')
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    vocab = np.array(vectorizer.get_feature_names_out())
    topic_words = lda.components_
    full_topic_dist = lda.transform(X_full)
    full_assigned = np.argmax(full_topic_dist, axis=1) if full_topic_dist.size else np.array([])

    # Transform summary sentences; if transform fails, treat as zero assignment
    try:
        X_summary = vectorizer.transform(summary_sentences)
        summary_topic_dist = lda.transform(X_summary)
        summary_assigned = np.argmax(summary_topic_dist, axis=1) if summary_topic_dist.size else np.array([])
    except Exception:
        summary_assigned = np.array([])

    topic_info = []
    for topic_idx, topic_dist in enumerate(topic_words):
        top_word_ids = topic_dist.argsort()[-top_words:][::-1]
        topic_title = ", ".join(vocab[top_word_ids[:3]]) if len(vocab) > 0 else f"Topic {topic_idx}"
        full_perc = (np.sum(full_assigned == topic_idx) / len(full_sentences) * 100) if len(full_sentences) > 0 else 0.0
        sum_perc = (np.sum(summary_assigned == topic_idx) / len(summary_sentences) * 100) if len(summary_sentences) > 0 else 0.0
        topic_info.append((topic_title, full_perc, sum_perc))

    # Prepare graph
    x = np.arange(len(topic_info))
    full_vals = [t[1] for t in topic_info]
    sum_vals = [t[2] for t in topic_info]
    topics = [t[0] for t in topic_info]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - 0.2, full_vals, width=0.4, label="Full Text")
    ax.bar(x + 0.2, sum_vals, width=0.4, label="Summary")
    ax.set_xticks(x)
    ax.set_xticklabels(topics, rotation=30, ha="right")
    ax.set_ylabel("Percentage of Sentences (%)")
    ax.set_title("Topic Distribution: Full Text vs Summary")
    ax.legend()
    plt.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
