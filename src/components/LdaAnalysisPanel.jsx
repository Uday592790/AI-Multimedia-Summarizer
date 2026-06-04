import { useState } from 'react';
import { BarChart3 } from 'lucide-react';
import LdaComparison from './LdaComparison';

export default function LdaAnalysisPanel({ fullText, summary, nTopics = 5, topWords = 5 }) {
  const [topics, setTopics] = useState(nTopics);
  const [words, setWords] = useState(topWords);
  const [enabled, setEnabled] = useState(false);
  const [requestKey, setRequestKey] = useState(0);

  if (!fullText || !summary) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-gray-700">
          <BarChart3 className="w-5 h-5" />
          <h3 className="text-lg font-semibold">LDA Analysis</h3>
        </div>
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg">
          Upload content and generate a summary to see LDA topic analysis.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-gray-700">
          <BarChart3 className="w-5 h-5" />
          <h3 className="text-lg font-semibold">LDA Analysis</h3>
        </div>
        <button
          onClick={() => {
            setEnabled(true);
            setRequestKey((k) => k + 1);
          }}
          className="bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Generate Graph
        </button>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Number of Topics</label>
            <input
              type="number"
              min="2"
              max="20"
              value={topics}
              onChange={(e) => setTopics(Math.max(2, Math.min(20, parseInt(e.target.value, 10) || 5)))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Recommended: 3-10</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Top Words per Topic</label>
            <input
              type="number"
              min="1"
              max="20"
              value={words}
              onChange={(e) => setWords(Math.max(1, Math.min(20, parseInt(e.target.value, 10) || 5)))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Recommended: 3-10</p>
          </div>
        </div>

        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-4">Topic Distribution Comparison</h4>
          <LdaComparison
            fullText={fullText}
            summaryText={summary}
            nTopics={topics}
            topWords={words}
            enabled={enabled}
            requestKey={requestKey}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="bg-blue-50 p-3 rounded border border-blue-200">
            <p className="font-medium text-blue-900">Full Text Analysis</p>
            <p className="text-blue-800 text-xs mt-1">Shows all topics extracted from the original content</p>
          </div>
          <div className="bg-green-50 p-3 rounded border border-green-200">
            <p className="font-medium text-green-900">Summary Analysis</p>
            <p className="text-green-800 text-xs mt-1">Shows topics preserved in the generated summary</p>
          </div>
        </div>
      </div>
    </div>
  );
}
