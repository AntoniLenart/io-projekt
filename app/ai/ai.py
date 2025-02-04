from openai import OpenAI
from pathlib import Path
import os

# client = YOUR API KEY


def transcribe_audio(record_dir: str, lang: str):
    """
    Transcribes the combined audio file from a recording directory using OpenAI's Whisper API.

    Args:
        record_dir (str): Path to the directory containing the audio file.
        lang (str): Language used in recorded meeting.

    Raises:
        FileNotFoundError: If the combined audio file does not exist.
    """
    audio_file_path = os.path.join(record_dir, "combined_audio.mp3")

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=Path(audio_file_path),
        language=lang
    )

    transcript_file_path = os.path.join(record_dir, "transcription.txt")
    with open(transcript_file_path, "w", encoding="utf-8") as tr:
        tr.write(transcript.text)

def summarize_transcript(record_dir: str, lang: str):
    """
    Summarizes the transcript of an audio recording using OpenAI's ChatGPT model.

    Args:
        record_dir (str): Path to the directory containing the transcript file.
        lang (str): Language used in recorded meetings.

    Raises:
        FileNotFoundError: If the transcript file does not exist.
    """
    transcript_file_path = os.path.join(record_dir, "transcription.txt")
    summary_file_path = os.path.join(record_dir, "summary.txt")

    if not os.path.exists(transcript_file_path):
        raise FileNotFoundError(f"Transcript file not found: {transcript_file_path}")
    
    with open(transcript_file_path, "r", encoding="utf-8") as tr:
        text = tr.read()
    
    summary = None
    if lang == "en":
        summary = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "Your task is to summarize audio transcripts to capture the main ideas and crucial points."},
            {"role": "user", "content": f"Summarize this transcript:\n{text}"}
        ]
    )
    elif lang == "pl":
        summary = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": "Twoim zadaniem jest podsumować daną transkrybcję audio i zachować najważnejsze punkty."},
            {"role": "user", "content": f"Stwórz podsumowanie tej transktybcji:\n{text}"}
        ]
    )
    else:
        raise ValueError(f"Language '{lang}' is not supported.")
    
        
    summary_text = summary.choices[0].message.content
    with open(summary_file_path, "w", encoding="utf-8") as su:
        su.write(summary_text)