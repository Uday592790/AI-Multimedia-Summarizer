# Check and optionally install FFmpeg on Windows
# Run from project root: .\scripts\check-ffmpeg.ps1

$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpeg) {
    Write-Host "FFmpeg is already installed:" $ffmpeg.Source
    exit 0
}

Write-Host "FFmpeg is not installed on this machine."

if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "Installing FFmpeg with Chocolatey..."
    choco install ffmpeg -y
    exit $LASTEXITCODE
}

if (Get-Command scoop -ErrorAction SilentlyContinue) {
    Write-Host "Installing FFmpeg with Scoop..."
    scoop install ffmpeg
    exit $LASTEXITCODE
}

Write-Host "Could not install FFmpeg automatically."
Write-Host "Please install it manually from https://ffmpeg.org/download.html and ensure 'ffmpeg' is on your PATH."
exit 1
