import os
import threading
import subprocess
import pygetwindow as gw
from tkinter import messagebox
from datetime import datetime


class Recorder:
    BASE_DIR = os.path.join(os.getcwd(), "assets", "recordings")

    def __init__(self):
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.recording = False
        self.process = None
        self.selected_app = None

    def select_application(self):
        apps = gw.getAllTitles()
        apps = [app for app in apps if app.strip()]
        if not apps:
            messagebox.showerror("Błąd", "Nie znaleziono otwartych aplikacji.")
            return

        # (Pseudokod do wybrania aplikacji w GUI)
        # np. messagebox.showinfo("Wybrano aplikację", "Zoom")
        self.selected_app = apps[0]  # Placeholder
        messagebox.showinfo("Aplikacja", f"Wybrano: {self.selected_app}")

    def start_recording(self):
        if not self.selected_app:
            messagebox.showerror("Błąd", "Nie wybrano aplikacji do nagrywania.")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.record_dir = os.path.join(self.BASE_DIR, f"recording_{timestamp}")
        os.makedirs(self.record_dir, exist_ok=True)
        self.video_path = os.path.join(self.record_dir, "recording.mp4")
        self.recording = True

        threading.Thread(target=self._record, daemon=True).start()
        return True

    def _record(self):
        # Konfiguracja i uruchomienie nagrywania
        pass

    def stop_recording(self):
        if self.recording and self.process:
            self.recording = False
            self.process.terminate()
            messagebox.showinfo("Nagrywanie", "Nagrywanie zakończone.")
            return True
        return False
