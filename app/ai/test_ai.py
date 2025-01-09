import unittest
from app.ai.ai import transcribe_audio, summarize_transcript
import os

class TestAiMethods(unittest.TestCase):
    def test_transcribe_audio(self):
        record_dir = os.path.join(os.getcwd(), "app", "ai")
        transcribe_audio(record_dir)
        unittest.assertTrue(os.path.exists(os.path.join(record_dir, "transcription.txt")))
    
    def test_summarize_transcript(self):
        record_dir = os.path.join(os.getcwd(), "app", "ai")
        summarize_transcript(record_dir)
        unittest.assertTrue(os.path.exists(os.path.join(record_dir, "summary.txt")))

if __name__ == "__main__":
    unittest.main()