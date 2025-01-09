from app.gui import App
import customtkinter as ctk


def main():
    root = ctk.CTk()
    print(type(root))
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
