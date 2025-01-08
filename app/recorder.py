import os
import threading
import pygetwindow as gw
import pyautogui
from tkinter import messagebox, Toplevel, Listbox, Button, END
from datetime import datetime
import cv2
import pyaudio
import wave
import time
import numpy as np


class Recorder:
    BASE_DIR = os.path.join(os.getcwd(), "assets", "recordings")

    def __init__(self, main_gui):
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.recording = False
        self.selected_app = None
        self.on_app_selected_callback = None  # Callback for app selection
        self.main_gui = main_gui
        self.captured_video = None
        self.audio_thread = None
        self.audio_frames = []
        self.audio_stream = None

    def set_app_selected_callback(self, callback):
        """Set a callback to notify when an app is selected."""
        self.on_app_selected_callback = callback

    def select_application(self):
        apps = gw.getAllTitles()

        from misc.forbidden_apps import forbidden_apps
        apps = [app for app in apps if app.strip() and app not in forbidden_apps]  # Filter empty titles

        if not apps:
            messagebox.showerror("Błąd", "Nie znaleziono otwartych aplikacji.")
            return

        # Dialog to select the application
        def on_select():
            selected_index = listbox.curselection()
            if selected_index:
                self.selected_app = apps[selected_index[0]]
                app_window.destroy()
                messagebox.showinfo("Aplikacja", f"Wybrano: {self.selected_app}")
                if self.on_app_selected_callback:  # Notify the callback
                    self.on_app_selected_callback(self.selected_app)
            else:
                messagebox.showerror("Błąd", "Nie wybrano aplikacji.")

        app_window = Toplevel()
        app_window.title("Wybierz aplikację")

        listbox = Listbox(app_window, selectmode="single", width=50, height=15)
        for app in apps:
            listbox.insert(END, app)
        listbox.pack(pady=10)

        select_button = Button(app_window, text="Wybierz", command=on_select)
        select_button.pack(pady=5)

        app_window.mainloop()

    def start_recording(self):
        if not self.selected_app:
            messagebox.showerror("Błąd", "Nie wybrano aplikacji do nagrywania.")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.record_dir = os.path.join(self.BASE_DIR, f"recording_{timestamp}")
        os.makedirs(self.record_dir, exist_ok=True)
        self.video_path = os.path.join(self.record_dir, "recording.mp4")
        self.audio_path = os.path.join(self.record_dir, "recording.wav")

        screen_size = pyautogui.size()  # Get screen resolution
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.captured_video = cv2.VideoWriter(self.video_path, self.fourcc, 10.0, screen_size)

        self.recording = True

        # Start recording threads
        video_thread = threading.Thread(target=self._record_screen, daemon=True)
        self.audio_thread = threading.Thread(target=self._record_audio, daemon=True)

        video_thread.start()
        self.audio_thread.start()
        return True

    def _record_screen(self):
        while self.recording:
            # Capture the screen using pyautogui
            screenshot = pyautogui.screenshot()

            # Convert the Pillow image to a NumPy array and directly write to OpenCV
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Write the frame to the video file
            self.captured_video.write(frame)

            # Sleep to control the frame rate
            time.sleep(0.1)  # Adjust frame rate if needed

        self.captured_video.release()

    def list_audio_devices(self):
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        devices = []
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            devices.append((i, device_info.get('name')))
        p.terminate()
        return devices

    def _record_audio(self):
        p = pyaudio.PyAudio()

        # Wybierz urządzenie do nagrywania (np. "Stereo Mix")
        device_index = None
        devices = self.list_audio_devices()
        print(devices)
        for i, name in devices:
            if "Stereo Mix" or "stereo mix" or "miks stereo" in name:  # Zmień nazwę na odpowiednią dla twojego systemu
                device_index = i
                break

        if device_index is None:
            print("Nie znaleziono urządzenia 'Stereo Mix'. Nagrywanie mikrofonu.")
            device_index = None  # Domyślnie nagrywanie mikrofonu

        self.audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
            input_device_index=device_index
        )

        while self.recording:
            data = self.audio_stream.read(1024)
            self.audio_frames.append(data)

        # Save audio when recording stops
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        p.terminate()

        with wave.open(self.audio_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.audio_frames))

    def stop_recording(self):
        if self.recording:
            self.recording = False
            if self.audio_thread:
                self.audio_thread.join()  # Wait for audio thread to finish

            messagebox.showinfo("Nagrywanie", f"Nagranie zapisano w: {self.record_dir}")
            return True
        else:
            messagebox.showerror("Błąd", "Nagrywanie nie jest aktywne.")
            return False
