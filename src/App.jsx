import { useState } from 'react';
import { FileText, FileCheck, BarChart3, Search, Languages, Network } from 'lucide-react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import Tabs from './components/Tabs';
import TranscriptionPanel from './components/TranscriptionPanel';
import SummaryPanel from './components/SummaryPanel';
import EvaluationPanel from './components/EvaluationPanel';
import SearchPanel from './components/SearchPanel';
import TranslationPanel from './components/TranslationPanel';
import LdaAnalysisPanel from './components/LdaAnalysisPanel';
import FullscreenOverlay from './components/FullscreenOverlay';
import ProcessingBar from './components/ProcessingBar';
import * as api from './services/api';

function App() {
  const [page, setPage] = useState('landing');
  const [activeTab, setActiveTab] = useState('transcription');
  const [transcription, setTranscription] = useState('');
  const [summary, setSummary] = useState('');
  const [metrics, setMetrics] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [translatedText, setTranslatedText] = useState('');
  const [audioUrl, setAudioUrl] = useState('');

  const [uploadLoading, setUploadLoading] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [evaluationLoading, setEvaluationLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [translationLoading, setTranslationLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);

  const [error, setError] = useState('');

  const tabs = [
    { id: 'transcription', label: 'Transcription', icon: <FileText className="w-4 h-4" /> },
    { id: 'summary', label: 'Summary', icon: <FileCheck className="w-4 h-4" /> },
    { id: 'evaluation', label: 'Evaluation', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'search', label: 'Search', icon: <Search className="w-4 h-4" /> },
    { id: 'lda', label: 'LDA Analysis', icon: <Network className="w-4 h-4" /> },
    { id: 'translation', label: 'Translation', icon: <Languages className="w-4 h-4" /> },
  ];

  const handleFileUpload = async (file) => {
    setUploadLoading(true);
    setError('');
    try {
      const response = await api.uploadFile(file);
      setTranscription(response.transcription);
      setActiveTab('transcription');
      setPage('workspace');
      void handleGenerateSummary(response.transcription);
    } catch (err) {
      setError(`Failed to process file: ${api.getErrorMessage(err)}`);
      console.error(err);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleGenerateSummary = async (textOverride) => {
    const text = textOverride ?? transcription;
    if (!text) return;
    setSummaryLoading(true);
    setError('');
    try {
      const response = await api.generateSummary(text);
      setSummary(response.summary);
      setActiveTab('summary');
    } catch (err) {
      setError(`Failed to generate summary: ${api.getErrorMessage(err)}`);
      console.error(err);
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleEvaluate = async () => {
    if (!transcription || !summary) return;
    setEvaluationLoading(true);
    setError('');
    try {
      const response = await api.evaluateSummary(transcription, summary);
      setMetrics(response);
    } catch (err) {
      setError(`Failed to evaluate summary: ${api.getErrorMessage(err)}`);
      console.error(err);
    } finally {
      setEvaluationLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!transcription) return;
    setSearchLoading(true);
    setError('');
    try {
      const response = await api.semanticSearch(query, transcription);
      setSearchResults(response);
    } catch (err) {
      setError(`Failed to perform search: ${api.getErrorMessage(err)}`);
      console.error(err);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleTranslate = async (targetLanguage) => {
    if (!summary) return;
    setTranslationLoading(true);
    setError('');
    try {
      const response = await api.translateText(summary, targetLanguage);
      setTranslatedText(response.translated_text);
    } catch (err) {
      setError(`Failed to translate text: ${api.getErrorMessage(err)}`);
      console.error(err);
    } finally {
      setTranslationLoading(false);
    }
  };

  const handleGenerateAudio = async () => {
    if (!summary) return;
    setAudioLoading(true);
    setError('');
    try {
      const response = await api.generateAudioSummary(summary);
      setAudioUrl(response.audio_url);
    } catch (err) {
      setError(`Failed to generate audio: ${api.getErrorMessage(err)}`);
      console.error(err);
    } finally {
      setAudioLoading(false);
    }
  };

  const handleReturnHome = () => {
    setPage('landing');
    setActiveTab('transcription');
    setTranscription('');
    setSummary('');
    setMetrics(null);
    setSearchResults([]);
    setTranslatedText('');
    setAudioUrl('');
    setError('');
  };

  return (
    <div
      className={`flex flex-col bg-gradient-to-br from-gray-50 to-gray-100 ${
        page === 'landing' ? 'h-screen overflow-hidden' : 'min-h-screen'
      }`}
    >
      <Header onHome={handleReturnHome} showHomeButton={page === 'workspace'} />

      <main
        className={`container mx-auto flex w-full flex-col px-6 ${
          page === 'landing' ? 'min-h-0 flex-1 py-4' : 'py-8'
        }`}
      >
        <div
          className={`mx-auto w-full ${
            page === 'landing' ? 'flex min-h-0 flex-1 flex-col max-w-6xl' : 'max-w-6xl space-y-6'
          }`}
        >
          {page === 'landing' && (
            <>
              <div className="flex min-h-0 flex-1 flex-col">
                <FileUpload onFileUpload={handleFileUpload} loading={uploadLoading} />
              </div>

              {error && (
                <div className="mt-4 shrink-0 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}
            </>
          )}

          {page === 'workspace' && transcription && (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <Tabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

              {summaryLoading && (
                <div className="px-6 pt-4">
                  <ProcessingBar label="Generating summary..." />
                </div>
              )}

              <div className="p-6">
                {activeTab === 'transcription' && (
                  <TranscriptionPanel transcription={transcription} />
                )}

                {activeTab === 'summary' && (
                  <SummaryPanel
                    fullText={transcription}
                    summary={summary}
                    onGenerateAudio={handleGenerateAudio}
                    loading={summaryLoading}
                    audioUrl={audioUrl}
                    audioLoading={audioLoading}
                  />
                )}

                {activeTab === 'evaluation' && (
                  <EvaluationPanel
                    metrics={metrics}
                    onEvaluate={handleEvaluate}
                    loading={evaluationLoading}
                  />
                )}

                {activeTab === 'search' && (
                  <SearchPanel
                    onSearch={handleSearch}
                    results={searchResults}
                    loading={searchLoading}
                  />
                )}

                {activeTab === 'lda' && (
                  <LdaAnalysisPanel fullText={transcription} summary={summary} />
                )}

                {activeTab === 'translation' && (
                  <TranslationPanel
                    translatedText={translatedText}
                    onTranslate={handleTranslate}
                    loading={translationLoading}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <FullscreenOverlay
        show={
          uploadLoading ||
          translationLoading ||
          evaluationLoading ||
          audioLoading
        }
        label={
          uploadLoading
            ? 'Processing and transcribing...'
            : translationLoading
              ? 'Translating...'
              : evaluationLoading
                ? 'Evaluating score...'
                : audioLoading
                  ? 'Generating audio summary...'
                  : null
        }
      />
    </div>
  );
}

export default App;
