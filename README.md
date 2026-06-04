# AI Multimedia Summarizer

A full-stack AI app for working with video, audio, PDF, and text content.

Features:
- Transcribe video/audio with Whisper
- Summarize extracted text with BART
- Evaluate summary quality
- Search semantically inside extracted text
- Translate summaries
- Generate LDA topic comparison charts
- Convert summaries to speech

## Requirements

Install these before running the project on a new computer:

- Node.js 18 or newer
- npm
- Python 3.11 64-bit
- Internet access for first-time AI model downloads

The project already includes FFmpeg here:

```text
backend/ffmpeg/bin/
```

You do not need to install FFmpeg separately unless you remove that folder.

## Important GitHub Notes

Do not upload generated dependency/model folders to GitHub.

These are already ignored:

```text
node_modules/
dist/
backend/venv/
backend/models/
backend/__pycache__/
```

`backend/models/` is created automatically when the app downloads AI models.

## Project Structure

```text
project/
  backend/
    main.py
    requirements.txt
    ffmpeg/
    services/
    input/
    output/
    models/       # generated automatically, do not commit
    venv/         # generated locally, do not commit
  src/
  package.json
  vite.config.js
  README.md
```

## Setup On A New Computer

### 1. Clone Or Download The Project

Open PowerShell in the folder where you want the project.

```powershell
cd "C:\path\to\project"
```

### 2. Install Frontend Dependencies

From the project root:

```powershell
npm install
```

### 3. Create Backend Virtual Environment

From the backend folder:

```powershell
cd backend
py -3.11 -m venv venv
```

If `py -3.11` is not found, install Python 3.11 64-bit and try again.

### 4. Install Backend Dependencies

Still inside `backend/`:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Check the key native package version:

```powershell
python -c "import ctranslate2; print(ctranslate2.__version__)"
```

Expected:

```text
4.4.0
```

## Run The App

Use two PowerShell terminals.

### Terminal 1: Backend

```powershell
cd "C:\path\to\project\backend"
.\venv\Scripts\Activate.ps1
python main.py
```

Backend URL:

```text
http://localhost:8000
```

API docs:

```text
http://localhost:8000/docs
```

### Terminal 2: Frontend

```powershell
cd "C:\path\to\project"
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Model Behavior

Models download on first use, not when the backend starts.

Default transcription model:

```text
Whisper base
```

The transcription service uses `faster-whisper` on CPU by default:

```text
device = cpu
compute_type = float32
cpu_threads = 1
```

This is slower than GPU, but it is more reliable across Windows machines.

Downloaded models are stored in:

```text
backend/models/
```

First use may take several minutes because the app downloads and loads models.

Examples:
- Uploading video/audio downloads the Whisper model.
- Generating a summary downloads the BART summarization model.
- Semantic search downloads a sentence-transformer model.
- Evaluation downloads BERTScore and embedding models.

## Optional Model Settings

You can change the Whisper model before starting the backend:

```powershell
$env:WHISPER_MODEL_SIZE="tiny"
python main.py
```

Available values:

```text
tiny, base, small, medium, large
```

The default is:

```text
base
```

You can also override CPU settings if needed:

```powershell
$env:WHISPER_COMPUTE_TYPE="int8"
$env:WHISPER_CPU_THREADS="2"
python main.py
```

## Common Problems

### Backend closes while loading Whisper

Use the pinned dependency versions in `backend/requirements.txt`.

Reinstall backend dependencies:

```powershell
cd "C:\path\to\project\backend"
.\venv\Scripts\Activate.ps1
python -m pip install --force-reinstall -r requirements.txt
```

Then verify:

```powershell
python -c "import ctranslate2; print(ctranslate2.__version__)"
python -c "import pkg_resources; print('pkg_resources ok')"
```

Expected:

```text
4.4.0
pkg_resources ok
```

### PowerShell blocks Activate.ps1

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

This only changes the policy for the current PowerShell window.

### Backend uses the wrong Python

Always activate the backend venv before running:

```powershell
cd "C:\path\to\project\backend"
.\venv\Scripts\Activate.ps1
python main.py
```

### Frontend command fails

Install frontend dependencies again:

```powershell
cd "C:\path\to\project"
npm install
npm run dev
```

### First request seems stuck

This is usually model download or model loading. Watch the backend terminal for progress messages such as:

```text
Loading Whisper model 'base'...
Whisper model loaded on cpu with float32.
Transcribed 12.3s: ...
```

## Useful Checks

```powershell
node -v
npm -v
py -3.11 --version
```

Backend package check:

```powershell
cd "C:\path\to\project\backend"
.\venv\Scripts\Activate.ps1
python -m pip check
```

FFmpeg files:

```powershell
Get-ChildItem .\ffmpeg\bin\*.exe
```

## Fresh Install Checklist

On a new computer:

- Install Node.js 18+
- Install Python 3.11 64-bit
- Run `npm install` in the project root
- Create `backend/venv`
- Install `backend/requirements.txt`
- Start backend with `python main.py`
- Start frontend with `npm run dev`
- Upload a file and allow first-time model downloads to finish

## License

MIT
