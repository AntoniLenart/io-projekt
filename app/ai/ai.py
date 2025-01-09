from openai import OpenAI
from pathlib import Path
import os
client = OpenAI()

def transcribe_audio(record_dir: str):
    audio_file_path = os.path.join(record_dir, "combined_audio.mp3")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=Path(audio_file_path),
        language="en"
    )
    
    transcript_file_path = os.path.join(record_dir, "transcription.txt")
    text = transcript.text
    with open(transcript_file_path, "w") as tr:
        tr.write(text)
    
def summarize_transcript(record_dir: str):
    transcript_file_path = os.path.join(record_dir, "transcription.txt")
    summary_file_path = os.path.join(record_dir, "summary.txt")
    text = None
    with open(transcript_file_path, "r") as tr:
        text = tr.read()
    
    summary = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"developer",
             "content":"Your task is to summarize audio transcript, so that main ideas are present and crucial points are preserved."},
            {"role":"user",
             "content":f"Summarize this transcript:\n{text}"}
        ]
    )
    
    summary_text = summary.choices[0].message.content
    with open(summary_file_path, "w") as su:
        su.write(summary_text)
    


    