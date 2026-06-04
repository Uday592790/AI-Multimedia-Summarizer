import { useState } from 'react';
import { Languages, Loader2 } from 'lucide-react';

const LANGUAGES = [
  { code: 'hi', name: 'Hindi' },
  { code: 'ta', name: 'Tamil' },
  { code: 'te', name: 'Telugu' },
  { code: 'bn', name: 'Bengali' },
  { code: 'mr', name: 'Marathi' },
  { code: 'gu', name: 'Gujarati' },
  { code: 'kn', name: 'Kannada' },
  { code: 'ml', name: 'Malayalam' },
  { code: 'pa', name: 'Punjabi' },
  { code: 'ur', name: 'Urdu' },
  { code: 'or', name: 'Odia' },
  { code: 'as', name: 'Assamese' },
];

export default function TranslationPanel({ translatedText, onTranslate, loading }) {
  const [selectedLanguage, setSelectedLanguage] = useState('');

  const handleTranslate = () => {
    if (!selectedLanguage) return;
    onTranslate(selectedLanguage);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-gray-700">
        <Languages className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Translation Output</h3>
      </div>

      <div className="flex gap-3">
        <select
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          disabled={loading}
        >
          <option value="">Choose a language</option>
          {LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
        <button
          onClick={handleTranslate}
          disabled={loading || !selectedLanguage}
          className="bg-blue-600 text-white py-2 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Translating...
            </>
          ) : (
            <>
              <Languages className="w-4 h-4" />
              Translate
            </>
          )}
        </button>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <textarea
          value={translatedText}
          readOnly
          rows={12}
          className="w-full bg-transparent resize-none focus:outline-none text-gray-800 leading-relaxed"
          placeholder="Translated text will appear here..."
        />
      </div>
    </div>
  );
}
