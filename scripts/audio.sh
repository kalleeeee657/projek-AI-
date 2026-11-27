#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -s public/narasi.mp3 ]; then exit 0; fi
if ! command -v ffmpeg >/dev/null || ! command -v ffprobe >/dev/null; then
  sudo apt-get update
  sudo apt-get install -y ffmpeg
fi
python3 -m venv .venv
.venv/bin/python -m pip install edge-tts
.venv/bin/python buat-suara.py
