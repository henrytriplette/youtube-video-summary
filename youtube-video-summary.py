import configparser
import argparse
import os
import re

import ollama
import yt_dlp

# Read Configuration
config = configparser.ConfigParser()
config.read("config.ini")

def transcribe_file(args):
    audio_path = args.file
    language = args.language
    output_dir = config.get('DEFAULT', 'output_dir', fallback='output')
    ai_model = config.get('AI', 'ai_model', fallback='qwen3:30b')

    if not os.path.exists(audio_path):
        print(f"File not found: {audio_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        import whisper
    except ImportError:
        print("Whisper not installed. pip install openai-whisper")
        return

    print(f"Transcribing {audio_path}...")
    model = whisper.load_model("large")
    transcribe_opts = {}
    if language:
        transcribe_opts['language'] = language
    result = model.transcribe(audio_path, **transcribe_opts)
    printed_subtitles = result["text"]

    video_title = re.sub(r'[^A-Za-z0-9 ]+', '', os.path.splitext(os.path.basename(audio_path))[0])

    if config.getboolean('AI', 'ai_enable', fallback=False) == False:
        print("AI summarization disabled. Saving transcription only.")
        out_file = f"{output_dir}/{video_title}_transcription.txt"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(printed_subtitles)
        print(f"Transcription saved to {out_file}")
        return

    if config.getboolean('TRANSCRIPTION', 'save_transcription', fallback=False) == True:
        out_file = f"{output_dir}/{video_title}_transcription.txt"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(printed_subtitles)
        print(f"Transcription saved to {out_file}")

    ai_base_url = config.get('AI', 'base_url', fallback='http://127.0.0.1:11434')
    client = ollama.Client(host=ai_base_url)
    try:
        response = ""
        prompt = f"Summarize the following script by focusing on the relevant points:\n\n{printed_subtitles}"
        stream = client.chat(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        print("Streaming response:\n")
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                print(content, end="", flush=True)
                response += content
        print("\n\n--- Stream complete ---")
    except ollama.ResponseError as e:
        print('Error:', e.error)
        if e.status_code == 404:
            client.pull(ai_model)
            print(f"Model {ai_model} pulled successfully. Please retry.")
        out_file = f"{output_dir}/{video_title}_transcription.txt"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(printed_subtitles)
        print(f"AI failed. Transcription saved to {out_file}")
        return

    summary_file = f"{output_dir}/{video_title}_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("\n\n--- Summary ---\n\n")
        f.write(response)
        f.write("\n\n--- Original Subtitles ---\n\n")
        f.write(printed_subtitles)
    print(f"Summary saved to {summary_file}")


def main(args):
    url = args.url
    output_dir = config.get('DEFAULT', 'output_dir', fallback='output')
    subtitles_dir = config.get('DEFAULT', 'subtitles_dir', fallback='subtitles')
    audio_dir = config.get('DEFAULT', 'audio_dir', fallback='audio')
    ai_model = config.get('AI', 'ai_model', fallback='qwen3:30b')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(subtitles_dir):
        os.makedirs(subtitles_dir)
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    # Fetch video info to get title
    ydl_opts = {
        'skip_download': True,  # Don't download the video itself
        'ignore_no_formats_error': True,
        'player_client': 'web',
        'cookiefile': config.get('DEFAULT', 'cookie_file', fallback=None),
    }
    info_dict = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
    video_title = info_dict.get('title', None)
    # video_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '.', '_')).rstrip()
    video_title = re.sub(r'[^A-Za-z0-9 ]+', '', video_title)

    has_subs = bool(info_dict.get('subtitles')) or bool(info_dict.get('automatic_captions'))
    if not has_subs:
        print("No subtitles found. Downloading audio...")
        ydl_audio_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"{audio_dir}/{video_title}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'player_client': 'web',
            'cookiefile': config.get('DEFAULT', 'cookie_file', fallback=None),
        }
        with yt_dlp.YoutubeDL(ydl_audio_opts) as ydl:
            ydl.download([url])
        
        try:
            import whisper
        except ImportError:
            print("Whisper not installed. pip install openai-whisper")
            return
            
        print("Transcribing audio...")
        model = whisper.load_model("large")
        transcribe_opts = {}
        if args.language:
            transcribe_opts['language'] = args.language
        result = model.transcribe(f"{audio_dir}/{video_title}.mp3", **transcribe_opts)
        printed_subtitles = result["text"]
        
        subtitle_file = f"{subtitles_dir}/{video_title}.txt"
        with open(subtitle_file, 'w', encoding='utf-8') as f:
            f.write(printed_subtitles)
        print(f"Transcription saved to {subtitle_file}")

    else:
        subtitle_file = f"{subtitles_dir}/{video_title}"

        # Download subtitles
        ydl_opts = {
            'skip_download': True,  # Don't download the video itself
            'ignore_no_formats_error': True,
            'writesubtitles': True,  # Download subtitles
            'writeautomaticsub': True,  # Also download auto-generated subtitles if available
            'subtitleslangs': ['en'],  # Change language code(s) as needed
            'subtitlesformat': 'ass/srt/best',  # Format of subtitles (vtt, srt, etc.)
            'outtmpl': subtitle_file,
            'player_client': 'web',
            'cookiefile': config.get('DEFAULT', 'cookie_file', fallback=None),
        }
     
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Read subtitles
        subtitle_file = None
        for ext in ['.en.vtt', '.en.srt', '.en.ass', '.en.srv3']:
            candidate = f"{subtitles_dir}/{video_title}{ext}"
            if os.path.exists(candidate):
                subtitle_file = candidate
                break

        if not subtitle_file:
            print("No subtitle file found.")
            return

        with open(subtitle_file, 'r', encoding='utf-8') as f:
            subtitles = f.read()
        
        # Clean subtitles (remove VTT headers and timestamps)
        cleaned_subtitles = []
        for line in subtitles.splitlines():
            if line.strip() == '' or line.startswith('WEBVTT') or '-->' in line:
                continue
            # Remove content within angle brackets (HTML tags)
            line = ''.join(part for part in line.split('<') if '>' not in part)
            if line.strip():
                cleaned_subtitles.append(line)
            # Remove line with only number and space above
            if re.match(r'^\d+\s*$', line):
                continue

        # Deduplicate consecutive lines
        deduped_subtitles = []
        previous_line = None
        for line in cleaned_subtitles:
            if line != previous_line:
                deduped_subtitles.append(line)
                previous_line = line

        # Check if current line is equal to the beginning of the following line
        for i in range(len(deduped_subtitles) - 1):
            if deduped_subtitles[i+1].startswith(deduped_subtitles[i]):
                deduped_subtitles[i] = ''  # Mark for removal
        deduped_subtitles = [line for line in deduped_subtitles if line != '']

        printed_subtitles = ' '.join(deduped_subtitles)
    # print("Extracted Subtitles:\n", printed_subtitles)
    
    #  Check if AI summarization is enabled
    if config.getboolean('AI', 'ai_enable', fallback=False) == False:
        print("AI summarization is disabled in the configuration.")
        return
    
    # Summarize using AI model
    ai_base_url = config.get('AI', 'base_url', fallback='http://127.0.0.1:11434')
    client = ollama.Client(host=ai_base_url)
    try:
        response = ""
        
        # Start streaming from the model
        prompt = f"Summarize the following script by focusing on the relevant points:\n\n{printed_subtitles}"
        stream = client.chat(
            model=ai_model,
            messages=[{"role": "user", "content": prompt}],
            stream=True  # Enable streaming mode
        )

        print("Streaming response:\n")
        for chunk in stream:
            # Each chunk contains partial output
            content = chunk.get("message", {}).get("content", "")
            if content:
                print(content, end="", flush=True)
                response += content

        print("\n\n--- Stream complete ---")
    except ollama.ResponseError as e:
        print('Error:', e.error)
        if e.status_code == 404:
            client.pull(ai_model)
            
        out_file = f"{output_dir}/{video_title}_transcription.txt"
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(printed_subtitles)
        print(f"AI failed. Transcription saved to {out_file}")
        return
   
    # Save summary to file
    summary_file = f"{output_dir}/{video_title}_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("\n\n--- Summary ---\n\n")
        f.write(response)
        # write original subtitles as well
        f.write("\n\n--- Original Subtitles ---\n\n")
        f.write(printed_subtitles)
        
        print(f"Summary saved to {summary_file}")
    
    # Cleanup subtitle file
    if subtitle_file and os.path.exists(subtitle_file):
        os.remove(subtitle_file)
    
if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description='Download YouTube Subtitles and Summarize')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='YouTube Video URL')
    group.add_argument('-f', '--file', help='Path to a local audio file (e.g. wav, mp3) to transcribe')
    parser.add_argument('-l', '--language', help='Language code for Whisper transcription (e.g. en, ja, de)', default=None)
    
    args = parser.parse_args()
    if args.file:
        transcribe_file(args)
    else:
        main(args)