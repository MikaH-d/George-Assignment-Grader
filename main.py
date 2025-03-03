#!/usr/bin/env python3
"""
Assignment Grader - Main entry point
"""

import sys
import argparse
import tkinter as tk
import traceback


def run_gui():
    """Run the application in graphical user interface mode."""
    print("Starting GUI...")
    try:
        # Create root window
        print("Creating Tkinter root window...")
        root = tk.Tk()
        root.title("George Assignment Grader")
        root.geometry("900x700")

        # Just display a simple label to verify window is showing
        # print("Creating test label...")
        # label = tk.Label(root, text="Assignment Grader is loading...")
        # label.pack(padx=20, pady=20)


        print("Attempting to import MainWindow...")
        try:
            from gui.main_window import MainWindow
            print("MainWindow imported successfully")

            # Create main window
            print("Creating MainWindow...")
            app = MainWindow(root)
            print("MainWindow created")
        except Exception as e:
            print(f"Error importing or creating MainWindow: {e}")
            traceback.print_exc()

        # Start the application
        print("Starting mainloop...")
        root.mainloop()
        print("Mainloop ended")
    except Exception as e:
        print(f"Error starting GUI: {e}")
        traceback.print_exc()


def main():
    """Main entry point function."""
    print("Starting application...")

    parser = argparse.ArgumentParser(description='Assignment Grader Tool')
    parser.add_argument('--cli', action='store_true', help='Run in command line mode')
    args = parser.parse_args()

    if args.cli:
        print("Running in CLI mode")
        # run_cli()
    else:
        print("Running in GUI mode")
        run_gui()

    print("Application finished")


if __name__ == "__main__":
    main()