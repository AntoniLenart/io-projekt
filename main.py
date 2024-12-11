from app.gui import RecorderApp
import customtkinter as ctk


def main():
    root = ctk.CTk()
    app = RecorderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
