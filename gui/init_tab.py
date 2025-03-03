"""
Initialization tab for the Assignment Grader GUI using Tkinter.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


class InitializationTab:
    """Tab for initializing the assignment grading process."""

    def __init__(self, parent, assignment, on_complete_callback):
        """
        Initialize the initialization tab.

        Args:
            parent: Parent frame
            assignment: Assignment instance to work with
            on_complete_callback: Function to call when initialization is complete
        """
        self.parent = parent
        self.assignment = assignment
        self.on_complete_callback = on_complete_callback

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for this tab."""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # File selection group
        file_group = ttk.LabelFrame(main_frame, text="File Selection")
        file_group.pack(fill=tk.X, padx=5, pady=5)

        # CSV File selection
        csv_frame = ttk.Frame(file_group)
        csv_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(csv_frame, text="Gradebook CSV:").pack(side=tk.LEFT)
        self.csv_path_var = tk.StringVar()
        csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_path_var, width=50)
        csv_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        browse_csv_btn = ttk.Button(csv_frame, text="Browse...", command=self.browse_csv)
        browse_csv_btn.pack(side=tk.LEFT, padx=5)

        # ZIP File selection
        zip_frame = ttk.Frame(file_group)
        zip_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(zip_frame, text="Submissions ZIP:").pack(side=tk.LEFT)
        self.zip_path_var = tk.StringVar()
        zip_entry = ttk.Entry(zip_frame, textvariable=self.zip_path_var, width=50)
        zip_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        browse_zip_btn = ttk.Button(zip_frame, text="Browse...", command=self.browse_zip)
        browse_zip_btn.pack(side=tk.LEFT, padx=5)

        # Assignment details group
        details_group = ttk.LabelFrame(main_frame, text="Assignment Details")
        details_group.pack(fill=tk.X, padx=5, pady=5)

        # Assignment name
        name_frame = ttk.Frame(details_group)
        name_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(name_frame, text="Assignment Name:").pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=50)
        name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Reference solution group
        solution_group = ttk.LabelFrame(main_frame, text="Reference Solution")
        solution_group.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Instructions label
        ttk.Label(solution_group,
                 text="Enter the reference solution for this assignment. " +
                      "This will be used for future auto-grading features.").pack(padx=5, pady=5)

        # Solution text area
        self.solution_text = scrolledtext.ScrolledText(solution_group, wrap=tk.WORD, height=10)
        self.solution_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(progress_frame, text="Initialization Progress:").pack(anchor=tk.W)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, length=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.status_var = tk.StringVar(value="Ready to initialize.")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W)

        # Initialize button
        self.init_btn = ttk.Button(main_frame, text="Initialize Assignment", command=self.initialize_assignment)
        self.init_btn.pack(fill=tk.X, padx=5, pady=10)

        # Check if we have default paths
        try:
            if hasattr(self.assignment, 'gradebook_csv_file_path'):
                if os.path.exists(self.assignment.gradebook_csv_file_path):
                    self.csv_path_var.set(self.assignment.gradebook_csv_file_path)

            if hasattr(self.assignment, 'submissions_zip_path'):
                if os.path.exists(self.assignment.submissions_zip_path):
                    self.zip_path_var.set(self.assignment.submissions_zip_path)

                    # Try to extract assignment name from zip filename
                    zip_filename = os.path.basename(self.assignment.submissions_zip_path)
                    assignment_name = os.path.splitext(zip_filename)[0]
                    self.name_var.set(assignment_name)
        except Exception as e:
            print(f"Error setting default paths: {e}")

    def browse_csv(self):
        """Open file dialog to browse for CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select Gradebook CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            self.csv_path_var.set(file_path)
            self.assignment.gradebook_csv_file_path = file_path

    def browse_zip(self):
        """Open file dialog to browse for ZIP file."""
        file_path = filedialog.askopenfilename(
            title="Select Submissions ZIP File",
            filetypes=[("ZIP Files", "*.zip"), ("All Files", "*.*")]
        )

        if file_path:
            self.zip_path_var.set(file_path)
            self.assignment.submissions_zip_path = file_path

            # Try to extract assignment name from zip filename
            zip_filename = os.path.basename(file_path)
            assignment_name = os.path.splitext(zip_filename)[0]
            self.name_var.set(assignment_name)

    def initialize_assignment(self):
        """Initialize the assignment with the selected files."""
        # Validate inputs
        if not self.csv_path_var.get():
            messagebox.showwarning("Missing Input", "Please select a gradebook CSV file.")
            return

        if not self.zip_path_var.get():
            messagebox.showwarning("Missing Input", "Please select a submissions ZIP file.")
            return

        if not self.name_var.get():
            messagebox.showwarning("Missing Input", "Please enter an assignment name.")
            return

        # Update assignment properties
        self.assignment.gradebook_csv_file_path = self.csv_path_var.get()
        self.assignment.submissions_zip_path = self.zip_path_var.get()
        self.assignment.set_assignment_name(self.name_var.get())

        # Set reference solution
        reference_solution = self.solution_text.get("1.0", tk.END).strip()
        self.assignment.set_reference_solution(reference_solution)

        # Update UI
        self.init_btn.config(state=tk.DISABLED)
        self.status_var.set("Loading student names...")
        self.progress_var.set(10)
        self.parent.update()  # Force UI update

        try:
            # Load student names
            student_names = self.assignment.load_student_names()
            self.status_var.set(f"Found {len(student_names)} student submissions in the gradebook.")
            self.progress_var.set(40)
            self.parent.update()  # Force UI update

            # Load submissions
            num_students, submissions = self.assignment.load_submissions()
            self.status_var.set(f"Processed {len(submissions)} out of {num_students} submissions.")
            self.progress_var.set(90)
            self.parent.update()  # Force UI update

            # Check for issues
            if len(submissions) < num_students:
                missing = num_students - len(submissions)
                messagebox.showwarning(
                    "Processing Warning",
                    f"Could not process {missing} submissions. These students may have submitted "
                    "but their submissions were not found or could not be processed."
                )

            # Finalize
            self.progress_var.set(100)
            self.status_var.set("Initialization complete!")

            # Call the completion callback
            self.on_complete_callback()
        except Exception as e:
            # Handle errors
            messagebox.showerror(
                "Initialization Error",
                f"An error occurred during initialization:\n\n{str(e)}"
            )
            self.init_btn.config(state=tk.NORMAL)
            self.progress_var.set(0)
            self.status_var.set("Initialization failed. Please try again.")