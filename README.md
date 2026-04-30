# YouTube Subtitle Summarizer

A Python tool that **downloads subtitles from any YouTube video** using [`yt_dlp`](https://github.com/yt-dlp/yt-dlp) and then **summarizes the content automatically using local AI** (e.g. Ollama).  
Also supports **transcribing local audio files** (wav, mp3, etc.) using [OpenAI Whisper](https://github.com/openai/whisper).  
Perfect for extracting key insights from long videos like lectures, interviews, or podcasts.

---

## Features

- **Downloads subtitles** directly from YouTube videos  
- **Transcribes local audio files** (wav, mp3, etc.) using Whisper  
- **Supports multiple languages** (default: English)  
- **Optional language selection** for Whisper transcription  
- **Summarizes the transcript** using AI  
- **Saves subtitles and summaries** to an organized output folder  
- **Configurable options** for subtitle format, language, and model

---

## 📦 Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/henrytriplette/youtube-video-summary
   cd youtube-video-summary
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Install Whisper** for local audio transcription

   ```bash
   pip install openai-whisper
   ```

---

## 🤖 Usage

### Summarize a YouTube video

```bash
python youtube-video-summary.py -u https://www.youtube.com/watch?v=SOMEVIDEOID
```

### Transcribe and summarize a local audio file

```bash
python youtube-video-summary.py -f path/to/recording.wav
```

### Specify transcription language

```bash
python youtube-video-summary.py -f recording.wav -l ja
python youtube-video-summary.py -u https://www.youtube.com/watch?v=ID -l de
```

### Parameters

| Flag | Long | Description |
|------|------|-------------|
| `-u` | `--url` | YouTube video URL |
| `-f` | `--file` | Path to a local audio file (wav, mp3, etc.) |
| `-l` | `--language` | Language code for Whisper transcription (e.g. `en`, `ja`, `de`) |

> **Note:** `-u` and `-f` are mutually exclusive — use one or the other.

### Output

```
output/
└── example_video_summary.txt
```

---

## Requirements

- Python 3.8+
- Ollama
- Internet access

## Export Youtube Cookies

Use [get-cookiestxt-locally](https://chromewebstore.google.com/detail/get-cookiestxt-locally)

## Upgrade packages

   ```bash
   pip install --upgrade -r requirements.txt
   ```
