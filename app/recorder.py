import os
import threading
import pyautogui
from tkinter import messagebox
from datetime import datetime
import cv2
import pyaudio
from pydub import AudioSegment
import time
import numpy as np
import subprocess
from PIL import ImageGrab
from app.ai.ai import summarize_transcript, transcribe_audio
import mss
from skimage.metrics import structural_similarity as ssim
from app.ai.convert_to_pdf import PDFGenerator


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

    def __init__(self, settings):
        """
        Initializes the Recorder class.
        """
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.recording = False
        self.settings = settings
        self.record_dir = None
        
        self.combined_audio_path = None
        self.video_path = None
        self.full_recording_path = None
        self.transcription_path = None
        self.summary_path = None
        self.pdf_notes_path = None
        
        self.mic_index = None
        self.stereo_index = None
        
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.captured_video = None
        
        self.mic_audio_stream = None
        self.mic_audio_frames = []
        self.stereo_audio_stream = None
        self.stereo_audio_frames = []
        
    def start_recording(self):
        """
        Starts recording screen and audio simultaneously.
        Creates necessary directories and initializes audio and video threads.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.record_dir = os.path.join(self.BASE_DIR, f"recording_{timestamp}")
        os.makedirs(self.record_dir, exist_ok=True)
        
        self.combined_audio_path = os.path.join(self.record_dir, "combined_audio.mp3")
        self.video_path = os.path.join(self.record_dir, "video.mp4")
        self.full_recording_path = os.path.join(self.record_dir, "full_recording.mp4")
        
        p = pyaudio.PyAudio()
        
        if not self.mic_index:
            self.mic_index = p.get_default_input_device_info().get("index")
        
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev["name"] == "Miks stereo (Realtek(R) Audio)" and dev["hostApi"] == 0:
                self.stereo_index = dev["index"]
                break
                
        if not self.stereo_index:
            print("No stereo mix device detected. Switching do default.")
            self.stereo_index = p.get_default_output_device_info().get("index")
        
        p.terminate()
        
        self.audio_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.video_thread = threading.Thread(target=self._record_screen, daemon=True)

        self.recording = True
        
        self.video_thread.start()
        self.audio_thread.start()

    def stop_recording(self, custom_name=None):
        """
        Stops recording and saves the recorded files. Optionally renames the recording directory.

        Args:
            custom_name (str, optional): Custom name for the recording directory.
        """
        if self.recording:
            self.recording = False
            if self.video_thread:
                self.video_thread.join()
                self.captured_video.release()
            if self.audio_thread:
                self.audio_thread.join()
            if custom_name:
                custom_dir = os.path.join(self.BASE_DIR, custom_name)
                os.rename(self.record_dir, custom_dir)
                self.record_dir = custom_dir
                self.combined_audio_path = os.path.join(self.record_dir, "combined_audio.mp3")
                self.video_path = os.path.join(self.record_dir, "video.mp4")
                self.full_recording_path = os.path.join(self.record_dir, "full_recording.mp4")
            
            self.merge_audio_video()
            self.transcription_path = transcribe_audio(self.record_dir, self.settings["language"])
            self.summary_path = summarize_transcript(self.record_dir, self.settings["language"])
            
            self.pdf_notes_path = os.path.join(self.record_dir, "notes.pdf")
            
            pdf_generator = PDFGenerator(self.summary_path, self.transcription_path, self.pdf_notes_path)
            pdf_generator.generate_pdf()

            messagebox.showinfo("Recording", f"Recording saved at: {self.record_dir}")
        else:
            messagebox.showerror("Error", "No active recording.")
    
    def _record_screen(self):
        """
        Records the screen, detects significant changes, and saves slides to a PDF.
        """         
        start_time = time.time()
        
        frames = []
        frame_ctr = 0
        
        sct = mss.mss()
        screen_size = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        
        while self.recording:
            img = sct.grab(screen_size)
            img_data = np.array(img)
            bgr_img = img_data[:, :, :3]
            frames.append(bgr_img)
            frame_ctr += 1
            
        stop_time = time.time()
        duration = stop_time - start_time
        obtained_fps = frame_ctr / duration 
        
        self.captured_video = cv2.VideoWriter(self.video_path, self.fourcc, obtained_fps*1.01, pyautogui.size())
        [self.captured_video.write(frame) for frame in frames]
        

    def _record_audio(self):
        """
        Records audio from both the microphone and the stereo mix (speaker output).
        Saves audio frames to buffers for later processing.
        """
        p = pyaudio.PyAudio()
                
        self.mic_audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=int(p.get_device_info_by_index(self.mic_index).get("maxInputChannels")),
            rate=int(p.get_device_info_by_index(self.mic_index).get("defaultSampleRate")),
            input=True,
            frames_per_buffer=1024,
            input_device_index=self.mic_index
        )

        self.stereo_audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=int(p.get_device_info_by_index(self.stereo_index).get("maxInputChannels")),
            rate=int(p.get_device_info_by_index(self.stereo_index).get("defaultSampleRate")),
            input=True,
            frames_per_buffer=1024,
            input_device_index=self.stereo_index
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


    def _save_audio(self):
        """
        Saves microphone and stereo audio to separate WAV files and combines them into an MP3 file.
        """
        p = pyaudio.PyAudio()
        
        mic_sound = AudioSegment(
            data=b"".join(self.mic_audio_frames),
            sample_width=p.get_sample_size(pyaudio.paInt16),
            frame_rate=44100,
            channels=2
        )
        
        stereo_sound = AudioSegment(
            data=b"".join(self.stereo_audio_frames),
            sample_width=p.get_sample_size(pyaudio.paInt16),
            frame_rate=44100,
            channels=2
        )
        
        mic_sound = mic_sound.apply_gain(10)
        
        overlay = stereo_sound.overlay(mic_sound, position=0)
        overlay.export(self.combined_audio_path, format="mp3", bitrate="192k")

        p.terminate()
    
    def merge_audio_video(self):
        try:
            mp3_recodec = [
                "ffmpeg",
                "-i", self.combined_audio_path,
                "-c:a", "libmp3lame",
                "-qscale:a", "2",
                os.path.join(self.record_dir, "cleaned_audio.mp3")
            ]
            command = [
                "ffmpeg",
                "-i", os.path.join(self.record_dir, "cleaned_audio.mp3"),
                "-i", self.video_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-ar", "48000",
                "-strict", "experimental",
                self.full_recording_path
            ]
            
            subprocess.run(mp3_recodec, check=True)
            subprocess.run(command, check=True)
            print(f"Successfully merged {self.combined_audio_path} and {self.video_path} into {self.full_recording_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to merge audio and video: {e}")
            
        except FileNotFoundError:
            print("FFmpeg is not installed or not in PATH enviromental variables.")


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
