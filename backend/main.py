from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, Response
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import traceback
import nltk

from services.model_paths import configure_model_cache_dirs

# Configure local model cache directories before ML libraries are imported.
configure_model_cache_dirs()

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception as e:
    print(f"Warning: Could not download NLTK data: {e}")

from services.file_handler import FileHandler
from services.transcription import TranscriptionService
from services.summarization import SummarizationService
from services.evaluation import EvaluationService
from services.search import SemanticSearchService
from services.translation import TranslationService
from services.tts import TTSService
from services.analysis import lda_compare_full_summary_image

app = FastAPI(
    title="Video Content Summarizer API",
    description="Backend API for summarizing video, audio, PDF, and text content",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

file_handler = FileHandler(INPUT_DIR, OUTPUT_DIR)
transcription_service = TranscriptionService()
summarization_service = SummarizationService()
evaluation_service = EvaluationService()
search_service = SemanticSearchService()
translation_service = TranslationService()
tts_service = TTSService(OUTPUT_DIR)


class SummarizeRequest(BaseModel):
    text: str
    max_length: Optional[int] = 150
    min_length: Optional[int] = 50


class EvaluateRequest(BaseModel):
    source_text: str
    summary_text: str


class SearchRequest(BaseModel):
    text: str
    query: str
    top_k: Optional[int] = 5


class TranslateRequest(BaseModel):
    text: str
    target_language: str


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = "en"


class LDARequest(BaseModel):
    full_text: str
    summary_text: str
    n_topics: Optional[int] = 5
    top_words: Optional[int] = 5


@app.get("/")
async def root():
    return {
        "message": "Video Content Summarizer API",
        "endpoints": {
            "/upload": "Upload file",
            "/summarize": "Summarize text content",
            "/evaluate": "Evaluate summary quality",
            "/search": "Semantic search on text",
            "/translate": "Translate text to Indian languages",
            "/tts": "Generate text-to-speech audio"
        }
    }


@app.post("/upload")
async def upload_file(
    file: Optional[UploadFile] = File(None)
):
    """
    Upload a file (video, audio, PDF, text).
    Returns the extracted/transcribed text.
    """
    try:
        if not file:
            raise HTTPException(
                status_code=400,
                detail="A file must be provided"
            )

        result = await file_handler.process_upload(file)
        if result["type"] in ["video", "audio"]:
            print(f"Starting transcription for {result['filename']}...", flush=True)
            text = await transcription_service.transcribe(result["path"])
            print(f"Finished transcription for {result['filename']}.", flush=True)
        elif result["type"] == "pdf":
            print(f"Starting PDF extraction for {result['filename']}...", flush=True)
            text = await file_handler.extract_pdf_text(result["path"])
            print(f"Finished PDF extraction for {result['filename']}.", flush=True)
        else:
            text = result["text"]

        return JSONResponse({
            "success": True,
            "file_type": result["type"],
            "text": text,
            "file_path": str(result["path"])
        })

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """
    Summarize the provided text using BART model.
    """
    try:
        summary = await summarization_service.summarize(
            request.text,
            max_length=request.max_length,
            min_length=request.min_length
        )

        return JSONResponse({
            "success": True,
            "summary": summary,
            "original_length": len(request.text.split()),
            "summary_length": len(summary.split()),
            "compression_ratio": round(len(summary.split()) / len(request.text.split()), 2)
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
async def evaluate_summary(request: EvaluateRequest):
    """
    Evaluate summary quality using BERTScore metrics.
    """
    try:
        metrics = await evaluation_service.evaluate(
            request.source_text,
            request.summary_text
        )

        return JSONResponse({
            "success": True,
            "metrics": metrics
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search on the text to find relevant passages.
    """
    try:
        results = await search_service.search(
            request.text,
            request.query,
            top_k=request.top_k
        )

        return JSONResponse({
            "success": True,
            "query": request.query,
            "results": results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate")
async def translate_text(request: TranslateRequest):
    """
    Translate text to Indian languages (Hindi, Tamil, Telugu, Bengali, etc.).
    Supported languages: hi, ta, te, bn, mr, gu, kn, ml, pa
    """
    try:
        translation = await translation_service.translate(
            request.text,
            request.target_language
        )

        return JSONResponse({
            "success": True,
            "original_text": request.text,
            "translated_text": translation,
            "target_language": request.target_language
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Generate text-to-speech audio file from text.
    Returns the URL/path to the generated audio file.
    """
    try:
        audio_path = await tts_service.generate(
            request.text,
            language=request.language
        )

        return JSONResponse({
            "success": True,
            "audio_path": str(audio_path),
            "audio_url": f"/audio/{audio_path.name}",
            "text": request.text,
            "language": request.language
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve generated audio files.
    """
    audio_path = OUTPUT_DIR / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(audio_path, media_type="audio/mpeg")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/lda_compare")
async def lda_compare(request: LDARequest):
    """Generate LDA comparison PNG for full text vs summary and return image bytes."""
    try:
        img_bytes = lda_compare_full_summary_image(
            request.full_text,
            request.summary_text,
            n_topics=request.n_topics or 5,
            top_words=request.top_words or 5
        )
        return Response(content=img_bytes, media_type="image/png")
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
