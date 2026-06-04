import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

export default function SearchPanel({ onSearch, results, loading }) {
  const [query, setQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-gray-700 mb-4">
        <Search className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Semantic Search</h3>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your search query..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="bg-blue-600 text-white py-2 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Search
            </>
          )}
        </button>
      </form>

      {results.length > 0 ? (
        <div className="space-y-3 mt-6">
          <h4 className="font-medium text-gray-700">Search Results</h4>
          {results.map((result, index) => (
            <div
              key={index}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start gap-3">
                <p className="text-gray-800 flex-1 leading-relaxed">{result.sentence}</p>
                <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap">
                  {(result.score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-50 rounded-lg p-8 border border-gray-200 text-center text-gray-500 mt-6">
          <Search className="w-12 h-12 mx-auto mb-3 text-gray-400" />
          <p>Enter a query to search through the transcription</p>
        </div>
      )}
    </div>
  );
}
