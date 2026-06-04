import { Home } from 'lucide-react';

export default function Header({ onHome, showHomeButton = false }) {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg">
      <div className="container mx-auto px-6 py-[21px]">
        <div className="flex items-center justify-between">
          {showHomeButton && (
            <button
              onClick={onHome}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
              title="Return to home"
            >
              <Home className="w-5 h-5" />
              <span className="text-sm font-medium">Home</span>
            </button>
          )}
          
          <div className="flex-1 flex flex-col items-center text-center">
            <h1 className="text-2xl font-bold tracking-tight">AI Multimedia Summarizer</h1>

            <p className="mt-1 text-sm max-w-2xl text-blue-100">
              Upload media files to generate AI-powered summaries
            </p>
          </div>

          {showHomeButton && <div className="w-20"></div>}
        </div>
      </div>
    </header>
  );
}
