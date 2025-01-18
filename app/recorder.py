import os
import threading
import pyautogui
from tkinter import messagebox
from datetime import datetime
import cv2
import pyaudio
from pydub import AudioSegment
import wave
import time
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image


class Recorder:
    """
    A class for recording screen and audio simultaneously, with options to save and manage recordings.

    Attributes:
        BASE_DIR (str): Base directory for saving recordings.
        app: Reference to the main application object, providing access to settings.
        recording (bool): Flag to indicate if recording is in progress.
        captured_video: VideoWriter object for saving screen recordings.
        audio_thread (threading.Thread): Thread for recording audio.
        video_thread (threading.Thread): Thread for recording screen.
        mic_audio_stream: PyAudio stream object for capturing microphone audio.
        mic_audio_frames (list): Buffer for storing microphone audio frames.
        mic_audio_path (str): File path for saving microphone audio.
        stereo_audio_stream: PyAudio stream object for capturing stereo audio.
        stereo_audio_frames (list): Buffer for storing stereo audio frames.
        stereo_audio_path (str): File path for saving stereo audio.
        combined_audio_path (str): File path for saving combined audio (microphone + stereo).
        settings (dict): Configuration settings from the app.
    """

    BASE_DIR = os.path.join(os.getcwd(), "assets", "recordings")

    def __init__(self, app):
        """
        Initializes the Recorder class.

        Args:
            app: Reference to the main application, providing settings and utilities.
        """
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.recording = False
        self.app = app
        self.captured_video = None
        self.audio_thread = None
        self.video_thread = None
        self.mic_audio_stream = None
        self.mic_audio_frames = []
        self.mic_audio_path = None
        self.stereo_audio_stream = None
        self.stereo_audio_frames = []
        self.stereo_audio_path = None
        self.combined_audio_path = None
        self.settings = app.settings

    def start_recording(self):
        """
        Starts recording screen and audio simultaneously.
        Creates necessary directories and initializes audio and video threads.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.record_dir = os.path.join(self.BASE_DIR, f"recording_{timestamp}")
        os.makedirs(self.record_dir, exist_ok=True)

        self.video_path = os.path.join(self.record_dir, "video.mp4")
        self.mic_audio_path = os.path.join(self.record_dir, "mic_audio.wav")
        self.stereo_audio_path = os.path.join(self.record_dir, "speaker_audio.wav")
        self.combined_audio_path = os.path.join(self.record_dir, "combined_audio.mp3")

        screen_size = pyautogui.size()
        self.fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        self.captured_video = cv2.VideoWriter(self.video_path, self.fourcc, 10.0, screen_size)

        self.recording = True

        self.video_thread = threading.Thread(target=self._record_screen, daemon=True)
        self.audio_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.video_thread.start()
        self.audio_thread.start()

    def _record_screen(self):
        """
        Records the screen, detects significant changes, and saves slides to a PDF.
        """
        previous_frame = None
        slides = []  # List to store unique slides as PIL Images

        while self.recording:
            screenshot = pyautogui.screenshot()
            current_frame = np.array(screenshot)

            # Convert screenshot to grayscale for comparison
            gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2GRAY)

            if previous_frame is not None:
                # Compare current frame with the previous one using SSIM
                score, _ = ssim(previous_frame, gray_frame, full=True)

                # If difference exceeds threshold, save this frame as a slide
                if score < 0.95:  # Threshold for detecting change
                    slides.append(screenshot)

            previous_frame = gray_frame
            frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)
            self.captured_video.write(frame)
            time.sleep(1 / self.settings['fps'])

        self.captured_video.release()

        # Save slides to PDF
        if slides:
            slides[0].save("slides.pdf", save_all=True, append_images=slides[1:])

    def _record_audio(self):
        """
        Records audio from both the microphone and the stereo mix (speaker output).
        Saves audio frames to buffers for later processing.
        """
        p = pyaudio.PyAudio()

        mic_index = None
        stereo_index = None

        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev["name"] == "Miks stereo (Realtek(R) Audio)" and dev["hostApi"] == 0:
                stereo_index = dev["index"]
            if dev["name"] == "Mikrofon (Realtek(R) Audio)":
                mic_index = dev["index"]

        self.mic_audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=48000,
            input=True,
            frames_per_buffer=1024,
            input_device_index=mic_index
        )

        self.stereo_audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            input_device_index=stereo_index
        )

        while self.recording:
            mic_audio_data = self.mic_audio_stream.read(1024)
            stereo_audio_data = self.stereo_audio_stream.read(1024)
            self.mic_audio_frames.append(mic_audio_data)
            self.stereo_audio_frames.append(stereo_audio_data)

        self.mic_audio_stream.stop_stream()
        self.mic_audio_stream.close()

        self.stereo_audio_stream.stop_stream()
        self.stereo_audio_stream.close()

        p.terminate()

        self._save_audio()

    def stop_recording(self, custom_name=None):
        """
        Stops recording and saves the recorded files. Optionally renames the recording directory.

        Args:
            custom_name (str, optional): Custom name for the recording directory.
        """
        if self.recording:
            self.recording = False
            if self.audio_thread:
                self.audio_thread.join()

            if custom_name:
                custom_dir = os.path.join(self.BASE_DIR, custom_name)
                os.rename(self.record_dir, custom_dir)
                self.record_dir = custom_dir

            messagebox.showinfo("Recording", f"Recording saved at: {self.record_dir}")
        else:
            messagebox.showerror("Error", "No active recording.")

    def _save_audio(self):
        """
        Saves microphone and stereo audio to separate WAV files and combines them into an MP3 file.
        """
        p = pyaudio.PyAudio()

        with wave.open(self.mic_audio_path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(self.mic_audio_frames))

        with wave.open(self.stereo_audio_path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(self.stereo_audio_frames))

        mic_sound = AudioSegment.from_file(self.mic_audio_path, format="wav")
        stereo_sound = AudioSegment.from_file(self.stereo_audio_path, format="wav")

        overlay = stereo_sound.overlay(mic_sound, position=0)
        overlay.export(self.combined_audio_path, format="mp3", bitrate="192k")

        p.terminate()


def list_audio_devices() -> list:
    """
    Lists available audio input devices.

    Returns:
        list: A list of tuples containing the index and name of each input device.
    """
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    devices = []
    seen_devices = set()

    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info.get("maxInputChannels") > 0:
            device_name = device_info.get("name")
            for encoding in ["utf-8", "latin1", "windows-1250"]:
                try:
                    device_name = device_name.encode("latin1").decode(encoding)
                    break
                except (UnicodeEncodeError, UnicodeDecodeError):
                    continue

            if device_name not in seen_devices and "mapowanie" not in device_name.lower():
                devices.append((i, device_name))
                seen_devices.add(device_name)

    p.terminate()
    return devices
