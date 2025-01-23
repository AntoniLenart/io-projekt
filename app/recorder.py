import os
import threading
import pyautogui
from tkinter import messagebox, Toplevel, Listbox, Button, END
from datetime import datetime
import cv2
import pyaudio
from pydub import AudioSegment
import wave
import time
import numpy as np


class Recorder:
    BASE_DIR = os.path.join(os.getcwd(), "assets", "recordings")

    def __init__(self, app):
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.recording = False
        self.app = app
        self.selected_mic_index = None
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

    def start_recording(self):
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
        while self.recording:
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            self.captured_video.write(frame)
            time.sleep(0.1) # TODO change this so that it updates with framerate

        self.captured_video.release()

    def _record_audio(self):
        p = pyaudio.PyAudio()

        mic_index = self.selected_mic_index
        if not mic_index:
            mic_index = p.get_default_input_device_info().get("index")
        
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if (dev["name"] == "Miks stereo (Realtek(R) Audio)" and dev["hostApi"] == 0):
                stereo_index = dev["index"]
        if not stereo_index:
            print("No stereo mix device detected. Switching do default.")
            stereo_index = p.get_default_output_device_info().get("index")
        
        print(p.get_device_info_by_index(mic_index).items())
                
        self.mic_audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=int(p.get_device_info_by_index(mic_index).get("maxInputChannels")),
            rate=int(p.get_device_info_by_index(mic_index).get("defaultSampleRate")),
            input=True,
            frames_per_buffer=1024,
            input_device_index=mic_index
        )
        
        self.stereo_audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=int(p.get_device_info_by_index(stereo_index).get("maxInputChannels")),
            rate=int(p.get_device_info_by_index(stereo_index).get("defaultSampleRate")),
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
        if self.recording:
            self.recording = False
            if self.audio_thread:
                self.audio_thread.join()

            if custom_name:
                custom_dir = os.path.join(self.BASE_DIR, custom_name)
                os.rename(self.record_dir, custom_dir)
                self.record_dir = custom_dir

            messagebox.showinfo("Nagrywanie", f"Nagranie zapisano w: {self.record_dir}")
            
        else:
            messagebox.showerror("Błąd", "Nagrywanie nie jest aktywne.")
    
    def _save_audio(self):
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
