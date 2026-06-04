import { BarChart3, Loader2 } from 'lucide-react';

export default function EvaluationPanel({ metrics, onEvaluate, loading }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-gray-700">
          <BarChart3 className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Evaluation Metrics</h3>
        </div>
        {!metrics && (
          <button
            onClick={onEvaluate}
            disabled={loading}
            className="bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Evaluating...
              </>
            ) : (
              'Run Evaluation'
            )}
          </button>
        )}
      </div>

      {metrics ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {metrics.bertscore && (
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
              <h4 className="font-semibold text-blue-900 mb-4">BERTScore</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Precision</span>
                  <span className="font-bold text-blue-700">
                    {(metrics.bertscore.precision * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Recall</span>
                  <span className="font-bold text-blue-700">
                    {(metrics.bertscore.recall * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">F1 Score</span>
                  <span className="font-bold text-blue-700">
                    {(metrics.bertscore.f1 * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          {metrics.accuracy !== undefined && (
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
              <h4 className="font-semibold text-green-900 mb-4">Accuracy</h4>
              <div className="text-4xl font-bold text-green-700">
                {(metrics.accuracy * 100).toFixed(2)}%
              </div>
            </div>
          )}

          {Object.entries(metrics)
            .filter(([key]) => key !== 'bertscore' && key !== 'accuracy')
            .map(([key, value]) => (
              <div
                key={key}
                className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200"
              >
                <h4 className="font-semibold text-purple-900 mb-2 capitalize">
                  {key.replace(/_/g, ' ')}
                </h4>
                <div className="text-2xl font-bold text-purple-700">
                  {typeof value === 'number' ? value.toFixed(4) : JSON.stringify(value)}
                </div>
              </div>
            ))}
        </div>
      ) : (
        <div className="bg-gray-50 rounded-lg p-8 border border-gray-200 text-center text-gray-500">
          <BarChart3 className="w-12 h-12 mx-auto mb-3 text-gray-400" />
          <p>Click &quot;Run Evaluation&quot; to see metrics</p>
        </div>
      )}
    </div>
  );
}
