"""
Grading tab for the Assignment Grader GUI using Tkinter.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from .image_viewer import ImageViewer
from .styling import apply_custom_style


class GradingTab:
    """Tab for grading student submissions."""

    # Predefined feedback templates
    FEEDBACK_TEMPLATES = {
        "Perfect": "Excellent work! All requirements met perfectly.",
        "Minor Issues": "Good work overall. Some minor issues:\n- ",
        "Major Issues": "Several issues need attention:\n- ",
        "Incorrect Solution": "The solution is incorrect:\n- ",
        "Missing Elements": "The following elements are missing:\n- ",
        "Code Style": """Please improve code style:
- Need better variable names
- Add more comments
- Improve formatting""",
        "Custom": ""
    }

    def __init__(self, parent, assignment, on_complete_callback):
        """
        Initialize the grading tab.

        Args:
            parent: Parent frame
            assignment: Assignment instance to work with
            on_complete_callback: Function to call when grading is complete
        """
        self.parent = parent
        self.assignment = assignment
        self.on_complete_callback = on_complete_callback
        self.submissions = []
        self.current_index = -1
        self.current_template = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for this tab."""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Progress section
        progress_group = ttk.LabelFrame(main_frame, text="Progress")
        progress_group.pack(fill=tk.X, padx=5, pady=5)

        progress_frame = ttk.Frame(progress_group)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)

        self.progress_label = ttk.Label(progress_frame, text="Submission 0 of 0")
        self.progress_label.pack(side=tk.LEFT, padx=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            length=100, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Student info section
        student_group = ttk.LabelFrame(main_frame, text="Student Information")
        student_group.pack(fill=tk.X, padx=5, pady=5)

        self.student_name_var = tk.StringVar(value="Student: Not selected")
        student_name_label = ttk.Label(student_group, textvariable=self.student_name_var)
        student_name_label.pack(padx=5, pady=5)

        # Create a paned window
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Solution section
        solution_group = ttk.LabelFrame(paned_window, text="Student Solution")
        paned_window.add(solution_group, weight=2)

        self.solution_text = scrolledtext.ScrolledText(solution_group, wrap=tk.WORD, height=10)
        self.solution_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        self.solution_text.config(state=tk.DISABLED)

        # Image viewer
        image_group = ttk.LabelFrame(paned_window, text="Images")
        paned_window.add(image_group, weight=1)

        self.image_viewer = ImageViewer(image_group)
        self.image_viewer.pack(fill=tk.BOTH, expand=True)

        # Add a test image button for debugging (can be hidden/removed in production)
        self.test_image_btn = ttk.Button(
            image_group,
            text="Test Image Display",
            command=self.test_image_display
        )
        self.test_image_btn.pack(side=tk.BOTTOM, padx=5, pady=5)

        # Feedback section
        feedback_group = ttk.LabelFrame(main_frame, text="Feedback")
        feedback_group.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Template selector
        template_frame = ttk.Frame(feedback_group)
        template_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(template_frame, text="Template:").pack(side=tk.LEFT, padx=5)

        self.template_combo = ttk.Combobox(
            template_frame,
            textvariable=self.current_template,
            values=list(self.FEEDBACK_TEMPLATES.keys()),
            state="readonly",
            width=20
        )
        self.template_combo.pack(side=tk.LEFT, padx=5)
        self.template_combo.set("Perfect")
        self.template_combo.bind('<<ComboboxSelected>>', self.apply_template)

        # Feedback text area
        self.feedback_text = scrolledtext.ScrolledText(feedback_group, wrap=tk.WORD, height=5)
        self.feedback_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Grade section
        grade_group = ttk.LabelFrame(main_frame, text="Grade")
        grade_group.pack(fill=tk.X, padx=5, pady=5)

        grade_frame = ttk.Frame(grade_group)
        grade_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(grade_frame, text="Grade (0-100):").pack(side=tk.LEFT, padx=5)

        self.grade_var = tk.DoubleVar(value=100.0)
        self.grade_spin = ttk.Spinbox(
            grade_frame,
            from_=0,
            to=100,
            increment=1.0,
            textvariable=self.grade_var,
            width=5
        )
        self.grade_spin.pack(side=tk.LEFT, padx=5)

        # Quick grade buttons
        quick_grade_frame = ttk.Frame(grade_group)
        quick_grade_frame.pack(fill=tk.X, padx=5, pady=5)

        quick_grades = [100, 90, 80, 70, 60, 50, 0]
        for grade in quick_grades:
            ttk.Button(
                quick_grade_frame,
                text=str(grade),
                width=3,
                command=lambda g=grade: self.grade_var.set(g)
            ).pack(side=tk.LEFT, padx=2)

        # Navigation buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        self.prev_btn = ttk.Button(button_frame, text="Previous",
                                   command=self.previous_submission, style='Nav.TButton')
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(button_frame, text="Save",
                                   command=self.save_current_submission)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(button_frame, text="Next",
                                   command=self.next_submission, style='Nav.TButton')
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.finish_btn = ttk.Button(button_frame, text="Finish Grading",
                                     command=self.finish_grading, style='Finish.TButton')
        self.finish_btn.pack(side=tk.RIGHT, padx=5)

        # Disable UI until submissions are loaded
        self.set_ui_enabled(False)

    def apply_template(self, event=None):
        """Apply the selected feedback template."""
        template_key = self.current_template.get()
        template_text = self.FEEDBACK_TEMPLATES[template_key]

        if template_key != "Custom":
            self.feedback_text.delete("1.0", tk.END)
            self.feedback_text.insert("1.0", template_text)

    def set_ui_enabled(self, enabled):
        """Enable or disable UI components."""
        state = tk.NORMAL if enabled else tk.DISABLED

        self.feedback_text.config(state=state)
        self.grade_spin.config(state=state)
        self.prev_btn.config(state=state if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=state if self.current_index < len(self.submissions) - 1 else tk.DISABLED)
        self.save_btn.config(state=state)
        self.finish_btn.config(
            state=tk.NORMAL if enabled and self.current_index == len(self.submissions) - 1 else tk.DISABLED)

    def initialize_grading(self, submissions):
        """
        Initialize the grading tab with submissions.

        Args:
            submissions: List of StudentSubmission objects
        """
        self.submissions = submissions
        self.current_index = -1

        if self.submissions:
            self.progress_label.config(text=f"Submission 0 of {len(self.submissions)}")
            self.progress_var.set(0)

            # Load the first submission
            self.next_submission()
        else:
            messagebox.showwarning(
                "No Submissions",
                "No submissions were found or processed successfully. Check the initialization step."
            )

    def load_submission(self, index):
        """
        Load a submission at the given index.

        Args:
            index: Index of the submission to load
        """
        if 0 <= index < len(self.submissions):
            # Save current submission before loading the new one
            if self.current_index != -1:
                self.save_current_submission()

            # Set the current index
            self.current_index = index

            # Get the submission
            submission = self.submissions[index]

            # Update UI
            self.student_name_var.set(f"Student: {submission.get_student_name()}")

            # Update solution text (read-only)
            self.solution_text.config(state=tk.NORMAL)
            self.solution_text.delete("1.0", tk.END)
            self.solution_text.insert("1.0", submission.get_solution())
            self.solution_text.config(state=tk.DISABLED)

            # Update image viewer with any images in the submission
            self.image_viewer.set_images(submission)

            # Update feedback text
            self.feedback_text.delete("1.0", tk.END)
            if submission.get_feedback():
                self.feedback_text.insert("1.0", submission.get_feedback())

            # Set grade if available
            if submission.get_grade() is not None:
                self.grade_var.set(submission.get_grade())
            else:
                self.grade_var.set(100.0)  # Default to 100.0 as per your code

            # Update progress
            self.progress_label.config(text=f"Submission {index + 1} of {len(self.submissions)}")
            self.progress_var.set((index + 1) / len(self.submissions) * 100)

            # Update button states
            self.prev_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if index < len(self.submissions) - 1 else tk.DISABLED)
            self.finish_btn.config(state=tk.NORMAL if index == len(self.submissions) - 1 else tk.DISABLED)

            # Enable UI
            self.set_ui_enabled(True)

    def save_current_submission(self):
        """Save the current submission's feedback and grade."""
        if 0 <= self.current_index < len(self.submissions):
            submission = self.submissions[self.current_index]

            # Save feedback
            feedback = self.feedback_text.get("1.0", tk.END).strip()
            submission.set_feedback(feedback)

            # Save grade
            try:
                grade = float(self.grade_var.get())
                if 0 <= grade <= 100:
                    submission.set_grade(grade)
                else:
                    messagebox.showwarning("Invalid Grade", "Grade must be between 0 and 100.")
            except ValueError:
                messagebox.showwarning("Invalid Grade", "Please enter a valid number for the grade.")

    def previous_submission(self):
        """Load the previous submission."""
        if self.current_index > 0:
            self.load_submission(self.current_index - 1)

    def next_submission(self):
        """Load the next submission."""
        if self.current_index < len(self.submissions) - 1:
            self.load_submission(self.current_index + 1)

    def finish_grading(self):
        """Finish the grading process."""
        # Save the current submission
        self.save_current_submission()

        # Update the dataframe
        self.assignment.update_dataframe()

        # Call the completion callback
        self.on_complete_callback()

    def test_image_display(self):
        """Test image display functionality."""
        print("Testing image display...")
        self.image_viewer.test_image()

        # Create a separate window with a test image for debugging
        test_window = tk.Toplevel(self.parent)
        test_window.title("Image Test Window")
        test_window.geometry("300x300")

        from utils.image_utils import create_test_image, create_tk_image

        # Create a test image
        test_img = create_test_image(width=200, height=200, color='green', text='Debug Test')

        # Convert to PhotoImage
        photo = create_tk_image(test_img)

        # Important: Keep a reference to prevent garbage collection
        test_window.photo = photo

        # Display it
        label = ttk.Label(test_window, image=photo)
        label.pack(padx=20, pady=20)

        info_label = ttk.Label(test_window,
                               text="If you can see this image, Tkinter image display is working correctly.")
        info_label.pack(padx=10, pady=10)