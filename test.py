# test_tkinter.py
import tkinter as tk


def main():
    root = tk.Tk()
    root.title("Test Window")

    label = tk.Label(root, text="Hello, Tkinter is working!")
    label.pack(padx=20, pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()