# YouTube Subtitle Summarizer

A Python tool that **downloads subtitles from any YouTube video** using [`yt_dlp`](https://github.com/yt-dlp/yt-dlp) and then **summarizes the content automatically using local AI** (e.g. Ollama).  
Perfect for extracting key insights from long videos like lectures, interviews, or podcasts.

---

## Features

- **Downloads subtitles** directly from YouTube videos  
- **Supports multiple languages** (default: English)  
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

---

## 🤖 Usage

1. **Run the script**

   ```bash
   python youtube-video-summary.py --url https://www.youtube.com/watch?v=SOMEVIDEOID
    ```

2. **Output**

   ```bash
    output/
    └── example_video_summary.txt
    ```

---

## Requirements

- Python 3.8+
- Ollama
- Internet access
