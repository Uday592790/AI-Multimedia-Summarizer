import { useState } from 'react';
import { FileText, Loader2, Volume2, Download } from 'lucide-react';

export default function SummaryPanel({
  summary,
  onGenerateAudio,
  loading,
  audioUrl,
  audioLoading,
}) {
  const [audioPlaying, setAudioPlaying] = useState(false);

  const handlePlayAudio = () => {
    const audio = document.getElementById('summary-audio');
    if (audio) {
      if (audioPlaying) {
        audio.pause();
        setAudioPlaying(false);
      } else {
        audio.play();
        setAudioPlaying(true);
      }
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-gray-700">
          <FileText className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Generated Summary</h3>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <textarea
          value={summary}
          readOnly
          rows={12}
          className="w-full bg-transparent resize-none focus:outline-none text-gray-800 leading-relaxed"
          placeholder={loading ? 'Generating summary...' : 'Summary will appear here after generation...'}
        />
      </div>

      {summary && (
        <div className="flex gap-3">
          <button
            onClick={onGenerateAudio}
            disabled={audioLoading}
            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {audioLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating Audio...
              </>
            ) : (
              <>
                <Volume2 className="w-4 h-4" />
                Generate Audio Summary
              </>
            )}
          </button>

          {audioUrl && (
            <>
              <button
                onClick={handlePlayAudio}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <Volume2 className="w-4 h-4" />
                {audioPlaying ? 'Pause' : 'Play'}
              </button>
              <a
                href={audioUrl}
                download="summary.mp3"
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </a>
              <audio
                id="summary-audio"
                src={audioUrl}
                onEnded={() => setAudioPlaying(false)}
                className="hidden"
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}
