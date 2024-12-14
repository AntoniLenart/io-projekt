import os
import threading
import subprocess
import pygetwindow as gw
from tkinter import messagebox, Toplevel, Listbox, Button, END
from datetime import datetime


class Recorder:
    BASE_DIR = os.path.join(os.getcwd(), "assets", "recordings")

    def __init__(self, main_gui):
        os.makedirs(self.BASE_DIR, exist_ok=True)
        self.recording = False
        self.process = None
        self.selected_app = None
        self.on_app_selected_callback = None  # Callback for app selection
        self.main_gui = main_gui

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
        self.recording = True

        threading.Thread(target=self._record, daemon=True).start()
        return True

    def _record(self):
        # Placeholder for recording logic
        pass

    def stop_recording(self):
        self.main_gui.stop_recording()
        #if self.recording and self.process:
        #    self.recording = False
        #    self.process.terminate()
        #    messagebox.showinfo("Nagrywanie", "Nagrywanie zakończone.")
        #    return True
