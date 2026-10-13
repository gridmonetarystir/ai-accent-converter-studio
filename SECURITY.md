# Security Policy

## Scope

AI Accent Converter Studio processes local audio files and microphone
input. It does not upload audio anywhere. The only network calls are:

- First-run model download from the pinned CDN (HTTPS, checksum-pinned).
- Optional update check against GitHub Releases (can be disabled in
  `config/default.toml` under `[updates] check_on_start = false`).

## Reporting a vulnerability

Email `security@accentstudio.dev` with a description and repro steps.
Do not open a public issue for anything exploitable.

We aim to respond within 5 business days and ship a fix within 30 days
for confirmed issues.

## Hardening notes for packagers

- Ship the app with the model cache pre-populated so the first-run
  download path is never exercised on locked-down machines.
- The bundled `ffmpeg.exe` is pinned to a specific build; verify the
  hash in `tools/ffmpeg.sha256` before redistributing.
- Do not enable `[debug] allow_remote_dsp = true` in shipped builds.
  It exists only for the DSP team's local iteration.