import customtkinter as ctk
from tkinter import messagebox
from app.recorder import Recorder, list_audio_devices
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

        self.selected_device_name = tk.StringVar()
        self.select_device_button = ctk.CTkButton(root, text="Wybierz Mikrofon", command=self.select_microphone)
        self.select_device_button.pack(pady=10)

    def select_microphone(self):
        device_window = tk.Toplevel(self.root)
        device_window.title("Wybierz Mikrofon")
        device_window.geometry("400x200")

        devices = list_audio_devices()
        device_names = [f"{i}: {device}" for i, device in devices]

        # Dropdown (OptionMenu)
        self.selected_device_name.set(device_names[0])  # Ustawienie domyślnego wyboru
        device_menu = ctk.CTkOptionMenu(device_window, variable=self.selected_device_name, values=device_names)
        device_menu.pack(padx=10, pady=20)

        def set_device():
            selected = self.selected_device_name.get()
            device_index = int(selected.split(":")[0])
            self.recorder.selected_mic_index = device_index
            messagebox.showinfo("Sukces", f"Wybrano mikrofon: {selected.split(': ')[1]}")
            device_window.destroy()

        select_button = ctk.CTkButton(device_window, text="Wybierz", command=set_device)
        select_button.pack(pady=10)

    def start_recording(self):
        self.recorder.start_recording()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_recording(self):
        self.recorder.stop_recording()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def get_selected_microphone(self):
        # print(self.selected_device_name.get())
        return self.selected_device_name.get()


if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    app = App(root)
    root.mainloop()
