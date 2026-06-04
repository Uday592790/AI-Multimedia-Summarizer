import { Loader2 } from 'lucide-react';

export default function FullscreenOverlay({ show, label }) {
  if (!show) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center">
      <div className="bg-white/90 rounded-2xl shadow-xl px-8 py-6 text-center">
        <div className="flex items-center justify-center mb-3">
          <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
        </div>
        <div className="text-gray-800 font-medium">{label || 'Processing...'}</div>
      </div>
    </div>
  );
}
