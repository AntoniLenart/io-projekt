import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from app.recorder import Recorder, list_audio_devices
from app.file_manager import FileManager


class App:
    """
    Main application class for recording online meetings.

    Args:
        root (tk.Tk): The main application window.
    """

    def __init__(self, root):
        """
        Initializes the application, creates the user interface, and sets default settings.
        """
        self.root = root
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root.title("Online Meeting Recording Application")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.file_manager = FileManager()
        self.settings = {
            "fps": 30,
            "language": "Polish",
            "max_file_size": 100  # in MB
        }

        self.recorder = Recorder(self)

        self.start_button = ctk.CTkButton(root, text="Start Recording", command=self.start_recording, state="normal")
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(root, text="Stop Recording", command=self.stop_recording, state="disabled")
        self.stop_button.pack(pady=5)

        self.browse_button = ctk.CTkButton(root, text="Browse Files", command=self.file_manager.browse_files)
        self.browse_button.pack(pady=10)

        self.selected_device_name = ctk.StringVar()
        self.select_device_button = ctk.CTkButton(root, text="Wybierz Mikrofon", command=self.select_microphone)
        self.select_device_button.pack(pady=10)

        self.settings_button = ctk.CTkButton(root, text="Settings", command=self.open_settings)
        self.settings_button.pack(pady=10)

    def open_settings(self):
        """
        Opens the settings window where the user can adjust application settings
        such as FPS, language, and maximum file size.
        """
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")

        # FPS settings
        fps_label = tk.Label(settings_window, text="FPS:")
        fps_label.pack(pady=5)
        fps_entry = tk.Entry(settings_window)
        fps_entry.insert(0, str(self.settings["fps"]))
        fps_entry.pack(pady=5)

        # Language settings
        language_label = tk.Label(settings_window, text="Language:")
        language_label.pack(pady=5)
        language_options = ["Polish", "English"]
        language_var = tk.StringVar(value=self.settings["language"])
        language_menu = ctk.CTkOptionMenu(settings_window, variable=language_var, values=language_options)
        language_menu.pack(pady=5)

        # Maximum file size settings
        max_size_label = tk.Label(settings_window, text="Max File Size (MB):")
        max_size_label.pack(pady=5)
        max_size_entry = tk.Entry(settings_window)
        max_size_entry.insert(0, str(self.settings["max_file_size"]))
        max_size_entry.pack(pady=5)

        # Save settings
        def save_settings():
            """
            Saves the updated settings and closes the settings window.
            """
            try:
                self.settings["fps"] = int(fps_entry.get())
                self.settings["language"] = language_var.get()
                self.settings["max_file_size"] = int(max_size_entry.get())
                messagebox.showinfo("Success", "Settings saved successfully!")
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values for the settings.")

        save_button = ctk.CTkButton(settings_window, text="Save", command=save_settings)
        save_button.pack(pady=20)

    def select_microphone(self):
        """
        Opens a window for selecting a microphone device from the available list.
        """
        device_window = tk.Toplevel(self.root)
        device_window.title("Select Microphone")
        device_window.geometry("400x200")

        devices = list_audio_devices()
        device_names = [f"{i}: {device}" for i, device in devices]

        self.selected_device_name.set(device_names[0])  # Set default selection
        device_menu = ctk.CTkOptionMenu(device_window, variable=self.selected_device_name, values=device_names)
        device_menu.pack(padx=10, pady=20)

        def set_device():
            """
            Sets the selected microphone device for the recorder.
            """
            selected = self.selected_device_name.get()
            device_index = int(selected.split(":")[0])
            self.recorder.selected_mic_index = device_index
            messagebox.showinfo("Success", f"Selected microphone: {selected.split(': ')[1]}")
            device_window.destroy()

        select_button = ctk.CTkButton(device_window, text="Select", command=set_device)
        select_button.pack(pady=10)

    def start_recording(self):
        """
        Starts the recording process using the recorder.
        """
        self.recorder.start_recording()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_recording(self):
        """
        Stops the recording process and allows the user to save the file with a custom name.
        """
        def save_with_name():
            """
            Saves the recording with the provided custom name or a default name if not specified.
            """
            custom_name = name_entry.get()
            if custom_name.strip():  # Check if a name is provided and remove unwanted spaces
                self.recorder.stop_recording(custom_name=custom_name)
            else:
                self.recorder.stop_recording()
            popup.destroy()
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

        popup = tk.Toplevel(self.root)
        popup.title("Save Recording")
        popup.geometry("300x150")

        label = tk.Label(popup, text="Enter file name (optional):")
        label.pack(pady=10)

        name_entry = tk.Entry(popup, width=30)
        name_entry.pack(pady=5)

        save_button = tk.Button(popup, text="Save", command=save_with_name)
        save_button.pack(pady=10)

    def get_selected_microphone(self):
        """
        Retrieves the name of the currently selected microphone.

        Returns:
            str: The name of the selected microphone.
        """
        return self.selected_device_name.get()


if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    app = App(root)
    root.mainloop()
