import configparser
import argparse
import os
import re

import ollama
import yt_dlp

# Read Configuration
config = configparser.ConfigParser()
config.read("config.ini")

def main(args):
    url = args.url
    output_dir = config.get('DEFAULT', 'output_dir', fallback='output')
    ai_model = config.get('AI', 'ai_model', fallback='qwen3:30b')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Download subtitles
    info_dict = yt_dlp.YoutubeDL().extract_info(url, download=False)
    video_title = info_dict.get('title', None)
    # video_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '.', '_')).rstrip()
    video_title = re.sub(r'[^A-Za-z0-9 ]+', '', video_title)

    subtitle_file = f"{output_dir}/{video_title}"

    ydl_opts = {
        'skip_download': True,  # Don't download the video itself
        'writesubtitles': True,  # Download subtitles
        'writeautomaticsub': True,  # Also download auto-generated subtitles if available
        'subtitleslangs': ['en'],  # Change language code(s) as needed
        'subtitlesformat': 'vtt',  # Format of subtitles (vtt, srt, etc.)
        'outtmpl': subtitle_file 
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Read subtitles
    subtitle_file = f"{output_dir}/{video_title}.en.vtt"
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
    try:
        response = ""
        
        # Start streaming from the model
        prompt = f"Summarize the following script by focusing on the relevant points:\n\n{printed_subtitles}"
        stream = ollama.chat(
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
            ollama.pull(ai_model)
   
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
    os.remove(subtitle_file)
    
if __name__ == "__main__":  
    parser = argparse.ArgumentParser(description='Download YouTube Subtitles and Summarize')
    parser.add_argument('-u', '--url', help='YouTube Video URL', required=True)
    
    args = parser.parse_args()
    main(args)