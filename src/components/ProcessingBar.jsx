import { Loader2 } from 'lucide-react';

export default function ProcessingBar({ label }) {
  if (!label) return null;
  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 text-blue-700 mb-1">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="font-medium">{label}</span>
      </div>
      <div className="w-full h-2 bg-blue-100 rounded">
        <div className="h-2 w-1/3 animate-pulse bg-blue-500 rounded" />
      </div>
    </div>
  );
}
