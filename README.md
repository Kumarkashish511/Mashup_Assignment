# Mashup_Assignment


A Flask web app that lets you search YouTube for any artist, download their top audio tracks, trim and merge them into one mashup, zip it up, and deliver it straight to your inbox — all from a simple web form.

---

## 🌐 Live Demo

👉 [https://github.com/Kumarkashish511/Mashup_Assignment](https://github.com/Kumarkashish511/Mashup_Assignment)

---

## 🛠️ Tech Stack

| Library | Role |
|--------|------|
| [Flask](https://flask.palletsprojects.com/) | Web framework & routing |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube search & audio download |
| [pydub](https://github.com/jiaaro/pydub) | Audio trimming & concatenation |
| [SendGrid](https://sendgrid.com/) | Transactional email with ZIP attachment |
| [Gunicorn](https://gunicorn.org/) | Production WSGI server |
| [ffmpeg](https://ffmpeg.org/) | Audio backend (required by pydub & yt-dlp) |

---

## ✨ Features

- 🔍 **YouTube Search** — Searches YouTube for the given singer and fetches the top N audio tracks via yt-dlp.
- ✂️ **Clip Trimming** — Trims each downloaded track to your chosen duration (in seconds).
- 🎶 **Mashup Creation** — Concatenates all trimmed clips into a single `mashup.mp3`.
- 📦 **ZIP Packaging** — Bundles the mashup into `mashup.zip`.
- 📧 **Email Delivery** — Sends the ZIP as an attachment via SendGrid to the provided address.
- 🖥️ **Clean Web UI** — Minimal, styled HTML form — no coding needed to use it.

---

## 📁 Project Structure

```
Mashup_Assignment/
├── app.py                  # Flask app — routes, mashup logic, email sending
├── 102317239.py            # CLI version of the mashup pipeline
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn entry point for deployment
├── index.html              # Mashup request form
├── success.html            # Result / status page
├── mashup.mp3              # Sample output mashup
└── 102317239-output.mp3    # Sample CLI output
```

---

## 📋 Prerequisites

1. **Python 3.8+**
2. **System-level `ffmpeg`** — required by pydub for audio processing

### Install ffmpeg

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install ffmpeg` |
| Debian / Ubuntu | `sudo apt update && sudo apt install -y ffmpeg` |
| Windows | [Download from ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH |

---

## ⚙️ Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/Kumarkashish511/Mashup_Assignment.git
cd Mashup_Assignment
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **requirements.txt includes:** `flask`, `flask-mail`, `yt-dlp`, `pydub`, `gunicorn`, `sendgrid`

### 4. Set environment variables

The app uses **SendGrid** for email. Set these before running:

```bash
# macOS / Linux
export SENDGRID_API_KEY="your-sendgrid-api-key"
export FROM_EMAIL="your-verified-sender@example.com"

# Windows (PowerShell)
$env:SENDGRID_API_KEY="your-sendgrid-api-key"
$env:FROM_EMAIL="your-verified-sender@example.com"
```

> 💡 Get a free API key at [sendgrid.com](https://sendgrid.com). Make sure your `FROM_EMAIL` is a verified sender in your SendGrid account.

---

## ▶️ Running the App

### Development

```bash
python app.py
```

Starts a dev server at: [http://0.0.0.0:5000](http://0.0.0.0:5000)

### Production (Gunicorn)

```bash
gunicorn app:app
```

The included `Procfile` already defines: `web: gunicorn app:app`

---

## 🖥️ Using the Web UI

Open the app in your browser and fill in the form:

| Field | Description | Validation |
|-------|-------------|-----------|
| **Singer Name** | Artist to search on YouTube | Required |
| **Number of Videos** | How many tracks to download | Must be `> 10` |
| **Duration (seconds)** | Length of each clip | Must be `> 20` |
| **Email Address** | Where to send the mashup | Valid email |

Hit **Generate Mashup** — the app downloads audio, trims clips, merges them, zips the result, and emails it.

### Status messages on the result page

| Outcome | Message |
|---------|---------|
| ✅ Success | *"Mashup created and sent to your email."* |
| ⚠️ Email failed | *"Mashup created but email could not be sent."* |
| ❌ Processing error | *"Could not create mashup (YouTube may have blocked requests)."* |

---

## 💻 CLI Usage (`102317239.py`)

The repo also includes a standalone command-line version:

```bash
python 102317239.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>
```

**Example:**

```bash
python 102317239.py "Arijit Singh" 15 30 arijit_mashup.mp3
```

**CLI pipeline steps:**
1. Downloads videos from YouTube into `downloads/`
2. Converts each video to MP3 into `audios/`
3. Trims each MP3 to the given duration into `cuts/`
4. Merges all clips into the output file
5. Cleans up all temporary folders automatically

> ⚠️ CLI version uses `moviepy` for video-to-audio conversion — install it with: `pip install moviepy`

---

## ☁️ Deployment (Heroku / Render)

1. Push the repo to your hosting platform.
2. The `Procfile` is already configured: `web: gunicorn app:app`
3. Set `SENDGRID_API_KEY` and `FROM_EMAIL` as environment variables on the platform.
4. Ensure `ffmpeg` is available — on Heroku, add the [ffmpeg buildpack](https://elements.heroku.com/buildpacks/jonathanong/heroku-buildpack-ffmpeg-latest).

---

## 🐞 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ffmpeg not found` | Install ffmpeg and confirm it's in your PATH |
| `"No audio downloaded"` | Try a different artist name or increase the number of videos |
| yt-dlp download failures | Some videos may be region-locked; the app skips them and continues |
| SendGrid auth errors | Check `SENDGRID_API_KEY` is correct and `FROM_EMAIL` is a verified sender |
| Slow or timed-out jobs | Large jobs take time — consider background job queues (Celery/RQ) for production |

---

## ⚠️ Legal & Ethical Notice

- This project downloads audio from YouTube programmatically. Ensure compliance with [YouTube's Terms of Service](https://www.youtube.com/t/terms) and applicable copyright laws.
- Provided **for educational purposes only**.
- No rate-limiting, authentication, or abuse controls are implemented. Do not expose to the public internet without adding proper security.

---

## 🔮 Possible Extensions

- [ ] Background job queue (Celery / RQ) for long downloads with progress updates
- [ ] Direct download link instead of (or alongside) email delivery
- [ ] Crossfade transitions between clips using pydub effects
- [ ] Per-user authentication and request quotas
- [ ] `.env.example` with `python-dotenv` for easier local config

---

## 🤝 Contributing

1. Fork the repo and create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes with a clear message
3. Open a Pull Request at [github.com/Kumarkashish511/Mashup_Assignment](https://github.com/Kumarkashish511/Mashup_Assignment) with a description of what changed and why
4. Include tests and update docs where appropriate

---

## 📄 License

No license file is included. Until one is added, no permission to use, copy, modify, or distribute this code is granted by default. Consider adding an [MIT License](https://choosealicense.com/licenses/mit/) if you plan to share it.

---

*Made with ❤️ | Roll No: 102317239*
