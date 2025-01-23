import os


class FileManager:
    """
    A class to manage file operations for recordings, including creating the base directory
    and opening it for browsing.

    Attributes:
        BASE_DIR (str): The base directory path where recordings are stored.
    """

    BASE_DIR = os.path.join(os.getcwd(), "assets", "recordings")

    def __init__(self):
        """
        Initializes the FileManager by ensuring the base directory exists.
        If the directory does not exist, it will be created.
        """
        os.makedirs(self.BASE_DIR, exist_ok=True)

    def browse_files(self):
        """
        Opens the base directory in the system's file explorer for browsing.
        """
        os.startfile(self.BASE_DIR)
