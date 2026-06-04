import { useRef } from 'react';
import { Upload, Mic, FileText, File as FileIcon } from 'lucide-react';

export default function FileUpload({ onFileUpload, loading }) {
  const videoInputRef = useRef(null);
  const audioInputRef = useRef(null);
  const pdfInputRef = useRef(null);
  const textInputRef = useRef(null);

  const handlePick = (type) => {
    if (loading) return;
    const refMap = {
      video: videoInputRef,
      audio: audioInputRef,
      pdf: pdfInputRef,
      text: textInputRef,
    };
    refMap[type].current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) onFileUpload(file);
    e.currentTarget.value = '';
  };

  const cardClass =
    'h-full w-full rounded-2xl border border-gray-200 px-4 flex flex-col items-center justify-center text-center gap-3 hover:shadow-lg hover:border-blue-300 transition';

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col rounded-2xl bg-white p-6 shadow-md sm:p-8">
      <h3 className="mb-5 shrink-0 text-center text-2xl font-semibold text-gray-800">
        Choose Your Input Method
      </h3>
      <input ref={videoInputRef} type="file" className="hidden" accept="video/*" onChange={handleFileChange} />
      <input ref={audioInputRef} type="file" className="hidden" accept="audio/*" onChange={handleFileChange} />
      <input ref={pdfInputRef} type="file" className="hidden" accept=".pdf" onChange={handleFileChange} />
      <input ref={textInputRef} type="file" className="hidden" accept=".txt" onChange={handleFileChange} />

      <div className="grid min-h-0 flex-1 grid-cols-2 grid-rows-2 gap-4 sm:gap-6">
        <button type="button" onClick={() => handlePick('video')} disabled={loading} className={cardClass}>
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-100 sm:h-20 sm:w-20">
            <Upload className="h-8 w-8 text-blue-600 sm:h-10 sm:w-10" />
          </span>
          <span className="text-lg font-semibold text-gray-900 sm:text-xl">Upload Video</span>
          <span className="text-sm text-gray-500">MP4, MKV, AVI files</span>
        </button>
        <button type="button" onClick={() => handlePick('audio')} disabled={loading} className={cardClass}>
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-green-100 sm:h-20 sm:w-20">
            <Mic className="h-8 w-8 text-green-600 sm:h-10 sm:w-10" />
          </span>
          <span className="text-lg font-semibold text-gray-900 sm:text-xl">Upload Audio</span>
          <span className="text-sm text-gray-500">MP3, WAV files</span>
        </button>
        <button type="button" onClick={() => handlePick('pdf')} disabled={loading} className={cardClass}>
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-orange-100 sm:h-20 sm:w-20">
            <FileIcon className="h-8 w-8 text-orange-600 sm:h-10 sm:w-10" />
          </span>
          <span className="text-lg font-semibold text-gray-900 sm:text-xl">Upload PDF</span>
          <span className="text-sm text-gray-500">PDF documents with OCR</span>
        </button>
        <button type="button" onClick={() => handlePick('text')} disabled={loading} className={cardClass}>
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-purple-100 sm:h-20 sm:w-20">
            <FileText className="h-8 w-8 text-purple-600 sm:h-10 sm:w-10" />
          </span>
          <span className="text-lg font-semibold text-gray-900 sm:text-xl">Upload Text</span>
          <span className="text-sm text-gray-500">TXT files</span>
        </button>
      </div>
    </div>
  );
}
