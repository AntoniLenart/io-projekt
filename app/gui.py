import customtkinter as ctk
from tkinter import messagebox
from app.recorder import Recorder
from app.file_manager import FileManager


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikacja do Nagrywania Spotkań Online")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.recorder = Recorder(self)
        self.file_manager = FileManager()

        self.start_button = ctk.CTkButton(root, text="Start Nagrywania", command=self.start_recording, state="normal")
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(root, text="Stop Nagrywania", command=self.stop_recording, state="disabled")
        self.stop_button.pack(pady=5)

        self.browse_button = ctk.CTkButton(root, text="Przeglądanie Plików", command=self.file_manager.browse_files)
        self.browse_button.pack(pady=10)

    def start_recording(self):
        self.recorder.start_recording()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_recording(self):
        self.recorder.stop_recording()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")


if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    app = App(root)
    root.mainloop()
