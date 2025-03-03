"""
Main window for the Assignment Grader GUI application using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from core.assignment import Assignment
from core.statistics import StatisticsCalculator

from .init_tab import InitializationTab
from .grading_tab import GradingTab
from .stats_tab import StatsTab
from .styling import apply_custom_style


class MainWindow:
    """Main window for the Assignment Grader application using Tkinter."""

    def __init__(self, root):
        """
        Initialize the main window.

        Args:
            root: The root Tkinter window
        """
        # Initialize root first
        self.root = root
        self.root.title("George Assignment Grader")

        # Initialize other attributes
        self.stats_tab = None
        self.grading_tab = None
        self.init_tab = None
        self.status_var = None


        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth() // 2 # half of the screen width
        screen_height = self.root.winfo_screenheight()  # Full screen height

        # Set the geometry to maximize height
        self.root.geometry(f"{screen_width}x{screen_height - 100}")  # Slight padding at the bottom
        self.root.configure(bg="white")


        # Create the tab control after root is assigned
        self.tab_control = ttk.Notebook(self.root, padding=5)

        # Apply custom styling
        self.colors = apply_custom_style(root)

        # Create model objects
        self.assignment = Assignment()
        self.stats_calculator = StatisticsCalculator()

        # Set up the user interface
        self.setup_ui()

        # Set up close event handling
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def setup_ui(self):
        """Set up the user interface."""
        # Create tab control with larger padding and font

        # Create frames for tabs
        init_frame = ttk.Frame(self.tab_control, padding=10)
        grading_frame = ttk.Frame(self.tab_control, padding=10)
        stats_frame = ttk.Frame(self.tab_control, padding=10)

        # Initialize tab contents
        self.init_tab = InitializationTab(init_frame, self.assignment, self.on_initialization_complete)
        self.grading_tab = GradingTab(grading_frame, self.assignment, self.on_grading_complete)
        self.stats_tab = StatsTab(stats_frame, self.assignment, self.stats_calculator)

        # Add tabs to the notebook
        self.tab_control.add(init_frame, text="Initialize")
        self.tab_control.add(grading_frame, text="Grade Submissions")
        self.tab_control.add(stats_frame, text="Statistics")

        # Disable grading and stats tabs until initialization is complete
        self.tab_control.tab(1, state="disabled")
        self.tab_control.tab(2, state="disabled")

        # Pack the tab control to fill the window
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        # Add a status bar at the bottom
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_initialization_complete(self):
        """Handle completion of the initialization step."""
        # Enable the grading tab and switch to it
        self.tab_control.tab(1, state="normal")
        self.tab_control.select(1)

        # Initialize the grading tab with the submissions
        self.grading_tab.initialize_grading(self.assignment.get_submissions())

        # Update status
        self.status_var.set(f"Initialized {len(self.assignment.get_submissions())} submissions for grading")

    def on_grading_complete(self):
        """Handle completion of the grading step."""
        # Enable the stats tab and switch to it
        self.tab_control.tab(2, state="normal")
        self.tab_control.select(2)

        # Refresh the statistics
        self.stats_tab.update_statistics()

        # Update status
        self.status_var.set("Grading complete. View statistics and export grades.")

        # Show confirmation dialog
        messagebox.showinfo(
            "Grading Complete",
            "All submissions have been graded!\n\nYou can now view the statistics and export the grades."
        )

    def on_close(self):
        """Handle window close event."""
        # Ask for confirmation
        if messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to exit?\nAny unsaved changes will be lost."
        ):
            self.root.destroy()