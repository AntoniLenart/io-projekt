from openai import OpenAI
from pathlib import Path
import os

# Initialize OpenAI client
client = OpenAI()


def transcribe_audio(record_dir: str):
    """
    Transcribes the combined audio file from a recording directory using OpenAI's Whisper API.

    Args:
        record_dir (str): Path to the directory containing the audio file.

    Raises:
        FileNotFoundError: If the combined audio file does not exist.
    """
    audio_file_path = os.path.join(record_dir, "combined_audio.mp3")

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    # Transcribe audio using Whisper model
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=Path(audio_file_path),
        language="en"
    )

    # Save the transcript to a text file
    transcript_file_path = os.path.join(record_dir, "transcription.txt")
    with open(transcript_file_path, "w", encoding="utf-8") as tr:
        tr.write(transcript.text)


def summarize_transcript(record_dir: str):
    """
    Summarizes the transcript of an audio recording using OpenAI's ChatGPT model.

    Args:
        record_dir (str): Path to the directory containing the transcript file.

    Raises:
        FileNotFoundError: If the transcript file does not exist.
    """
    transcript_file_path = os.path.join(record_dir, "transcription.txt")
    summary_file_path = os.path.join(record_dir, "summary.txt")

    if not os.path.exists(transcript_file_path):
        raise FileNotFoundError(f"Transcript file not found: {transcript_file_path}")

    # Read the transcript content
    with open(transcript_file_path, "r", encoding="utf-8") as tr:
        text = tr.read()

    # Generate a summary using GPT
    summary = client.chat.completions.create(
        model="gpt-4o",  # Assuming "gpt-4o" is the correct model name; otherwise, use "gpt-4"
        messages=[
            {"role": "system",
             "content": "Your task is to summarize audio transcripts to capture the main ideas and crucial points."},
            {"role": "user", "content": f"Summarize this transcript:\n{text}"}
        ]
    )

    # Extract and save the summary
    summary_text = summary.choices[0].message.content
    with open(summary_file_path, "w", encoding="utf-8") as su:
        su.write(summary_text)
