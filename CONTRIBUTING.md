# Contributing to AI Accent Converter Studio

Thanks for wanting to help. This project is a Windows desktop tool for
converting speech between English accents (US, UK, AU, IE, IN, ZA, NZ)
using a phoneme-preserving voice-conversion pipeline. It runs fully
offline after first model download.

## Dev setup

1. Install Python 3.11 or 3.12 (3.13 works but ONNX Runtime wheels lag).
2. Clone the repo and create a venv:
   ```
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   ```
3. Install dev requirements:
   ```
   pip install -r requirements.txt
   ```
4. Pull the reference voice packs (about 340 MB):
   ```
   python -m accent_studio.tools.fetch_voicepacks --all
   ```
5. Run the app:
   ```
   python -m accent_studio
   ```

## What we want PRs for

- New accent profiles (see `accent_studio/voices/profiles.py`)
- Better phoneme alignment for non-rhotic targets
- Batch queue improvements in `accent_studio/services/batch_queue.py`
- UI polish in `accent_studio/ui/`
- Tests — especially regression tests for the DSP chain

## Code style

- `ruff` for lint, `black` for format, line length 100.
- Type hints required on public functions.
- No new heavy deps without discussion. We already carry onnxruntime,
  librosa, soundfile, numpy, scipy, and PySide6.

## Commit messages

Short imperative subject, body if needed. Example:
```
voices: fix rhoticity drift on AU profile at f0 > 220Hz
```

## Reporting bugs

Open an issue with: OS build, Python version, input sample rate,
target accent, and the console log. Attach the input WAV if you can.