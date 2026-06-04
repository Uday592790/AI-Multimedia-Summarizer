import { FileText } from 'lucide-react';

export default function TranscriptionPanel({ transcription }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-gray-700">
        <FileText className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Transcription Preview</h3>
      </div>
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <textarea
          value={transcription}
          readOnly
          rows={12}
          className="w-full bg-transparent resize-none focus:outline-none text-gray-800 leading-relaxed"
          placeholder="Transcription will appear here..."
        />
      </div>
      <div className="text-sm text-gray-500">Characters: {transcription.length}</div>
    </div>
  );
}
