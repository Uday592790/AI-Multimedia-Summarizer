import { useEffect, useState } from 'react';
import { API_BASE_URL } from '../config';

export default function LdaComparison({
  fullText,
  summaryText,
  nTopics = 5,
  topWords = 5,
  enabled = false,
  requestKey = 0,
}) {
  const [imgUrl, setImgUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasRun, setHasRun] = useState(false);

  useEffect(() => {
    let mounted = true;
    if (!fullText || !summaryText) {
      setImgUrl(null);
      setError(null);
      setHasRun(false);
      return;
    }

    if (!enabled) {
      return;
    }

    const fetchImage = async () => {
      setLoading(true);
      setError(null);
      setHasRun(true);
      try {
        const resp = await fetch((API_BASE_URL || '') + '/lda_compare', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            full_text: fullText,
            summary_text: summaryText,
            n_topics: nTopics,
            top_words: topWords,
          }),
        });

        if (!resp.ok) {
          let msg = 'LDA generation failed';
          try {
            const j = await resp.json();
            if (j) msg = j.error || j.detail || JSON.stringify(j);
          } catch {
            try {
              const text = await resp.text();
              if (text) msg = text;
            } catch {
              // ignore
            }
          }
          throw new Error(msg || 'LDA generation failed');
        }

        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        if (mounted) setImgUrl(url);
      } catch (err) {
        console.error('LDA fetch error', err);
        if (mounted) setError(err.message || 'Failed to generate LDA');
      } finally {
        if (mounted) setLoading(false);
      }
    };

    fetchImage();

    return () => {
      mounted = false;
      if (imgUrl) {
        URL.revokeObjectURL(imgUrl);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, requestKey, fullText, summaryText, nTopics, topWords]);

  if (!fullText || !summaryText) return null;

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-700">Topic Distribution (Full Text vs Summary)</h4>
      </div>

      <div className="bg-white rounded-md border border-gray-200 p-2">
        {loading && <div className="text-sm text-gray-500">Generating topic comparison graph...</div>}
        {hasRun && error && <div className="text-sm text-red-600">Error generating graph: {error}</div>}
        {imgUrl && <img src={imgUrl} alt="LDA comparison" className="w-full h-auto rounded" />}
      </div>
    </div>
  );
}
