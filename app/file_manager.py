import os


class FileManager:
    BASE_DIR = os.path.join(os.getcwd(), "assets", "recordings")

    def __init__(self):
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def browse_files(self):
        os.startfile(self.BASE_DIR)
