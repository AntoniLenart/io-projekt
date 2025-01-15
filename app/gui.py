import customtkinter as ctk
from tkinter import messagebox
from app.recorder import Recorder, list_audio_devices
from app.file_manager import FileManager


class App:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root.title("Aplikacja do Nagrywania Spotkań Online")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.file_manager = FileManager()
        self.settings = {
            "fps": 30,
            "language": "Polski",
            "max_file_size": 100  # w MB
        }

        self.recorder = Recorder(self)

        self.start_button = ctk.CTkButton(root, text="Start Nagrywania", command=self.start_recording, state="normal")
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(root, text="Stop Nagrywania", command=self.stop_recording, state="disabled")
        self.stop_button.pack(pady=5)

        self.browse_button = ctk.CTkButton(root, text="Przeglądanie Plików", command=self.file_manager.browse_files)
        self.browse_button.pack(pady=10)

        self.selected_device_name = tk.StringVar()
        self.select_device_button = ctk.CTkButton(root, text="Wybierz Mikrofon", command=self.select_microphone)
        self.select_device_button.pack(pady=10)

        self.settings_button = ctk.CTkButton(root, text="Ustawienia", command=self.open_settings)
        self.settings_button.pack(pady=10)

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ustawienia")
        settings_window.geometry("400x300")

        # FPS ustawienia
        fps_label = tk.Label(settings_window, text="Ilość FPS:")
        fps_label.pack(pady=5)
        fps_entry = tk.Entry(settings_window)
        fps_entry.insert(0, str(self.settings["fps"]))
        fps_entry.pack(pady=5)

        # Język ustawienia
        language_label = tk.Label(settings_window, text="Język:")
        language_label.pack(pady=5)
        language_options = ["Polski", "Angielski"]
        language_var = tk.StringVar(value=self.settings["language"])
        language_menu = ctk.CTkOptionMenu(settings_window, variable=language_var, values=language_options)
        language_menu.pack(pady=5)

        # Maksymalny rozmiar pliku ustawienia
        max_size_label = tk.Label(settings_window, text="Maksymalny rozmiar pliku (MB):")
        max_size_label.pack(pady=5)
        max_size_entry = tk.Entry(settings_window)
        max_size_entry.insert(0, str(self.settings["max_file_size"]))
        max_size_entry.pack(pady=5)

        # Zapisz ustawienia
        def save_settings():
            try:
                self.settings["fps"] = int(fps_entry.get())
                self.settings["language"] = language_var.get()
                self.settings["max_file_size"] = int(max_size_entry.get())
                messagebox.showinfo("Sukces", "Ustawienia zapisane pomyślnie!")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Błąd", "Wprowadź poprawne wartości dla ustawień.")

        save_button = ctk.CTkButton(settings_window, text="Zapisz", command=save_settings)
        save_button.pack(pady=20)

    def select_microphone(self):
        device_window = tk.Toplevel(self.root)
        device_window.title("Wybierz Mikrofon")
        device_window.geometry("400x200")

        devices = list_audio_devices()
        device_names = [f"{i}: {device}" for i, device in devices]

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
        def save_with_name():
            custom_name = name_entry.get()
            if custom_name.strip():  # Jeśli podano nazwę, usuń niechciane spacje
                self.recorder.stop_recording(custom_name=custom_name)
            else:
                self.recorder.stop_recording()
            popup.destroy()
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

        popup = tk.Toplevel(self.root)
        popup.title("Zapisz nagranie")
        popup.geometry("300x150")

        label = tk.Label(popup, text="Wprowadź nazwę pliku (opcjonalne):")
        label.pack(pady=10)

        name_entry = tk.Entry(popup, width=30)
        name_entry.pack(pady=5)

        save_button = tk.Button(popup, text="Zapisz", command=save_with_name)
        save_button.pack(pady=10)

    def get_selected_microphone(self):
        return self.selected_device_name.get()


if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    app = App(root)
    root.mainloop()
