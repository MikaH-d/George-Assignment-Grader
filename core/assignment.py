"""
Assignment class - Core domain model representing an assignment

This class manages the list of student submissions and provides methods
to access and manipulate them.
"""

import os
import pandas as pd

from models.student_submission import StudentSubmission
from core.file_processor import FileProcessor
from utils.file_utils import get_last_downloaded


class Assignment:
    """Class representing an assignment with multiple student submissions."""

    def __init__(self):
        """Initialize a new Assignment instance."""
        self.assignment_name = None
        self.names_of_students_submit = []
        self.reference_solution = ''
        self.submissions_list = []

        # File paths
        self.gradebook_csv_file_path = get_last_downloaded(".csv")
        self.submissions_zip_path = get_last_downloaded(".zip")

        # Initialize file processor
        self.file_processor = FileProcessor()

        # DataFrame for analysis
        self.data_frame = None

    def set_assignment_name(self, name=None):
        """
        Set the assignment name.

        Args:
            name: Optional name to set. If None, extracts from zip filename.

        Returns:
            str: The set assignment name
        """
        if name:
            self.assignment_name = name
        else:
            # Extract from zip filename
            zip_filename = os.path.basename(self.submissions_zip_path)
            self.assignment_name = os.path.splitext(zip_filename)[0]

        return self.assignment_name

    def set_reference_solution(self, solution_text):
        """
        Set the reference solution for the assignment.

        Args:
            solution_text: Reference solution text

        Returns:
            str: The reference solution
        """
        self.reference_solution = solution_text
        return self.reference_solution

    def get_reference_solution(self):
        """Get the reference solution text."""
        return self.reference_solution

    def load_submissions(self):
        """
        Load student submissions from files.

        Returns:
            tuple: (number_of_students_submitted, list_of_submissions)
        """
        # Make sure we have student names
        if not self.names_of_students_submit:
            self.load_student_names()

        # Number of students who submitted (from gradebook)
        num_students_submitted = len(self.names_of_students_submit)

        # Process the submissions
        self.submissions_list = self.file_processor.extract_submissions(
            self.gradebook_csv_file_path,
            self.submissions_zip_path,
            self.names_of_students_submit
        )

        # Update data_frame with submissions data
        self.update_dataframe()

        # Return the number of students who submitted (not the number of submissions processed)
        return num_students_submitted, self.submissions_list

    def load_student_names(self):
        """
        Load the list of students who submitted from the gradebook.

        Returns:
            list: Names of students who submitted
        """
        if not os.path.exists(self.gradebook_csv_file_path):
            raise FileNotFoundError(f"Gradebook CSV file not found: {self.gradebook_csv_file_path}")

        try:
            # Load the CSV file
            self.data_frame = pd.read_csv(self.gradebook_csv_file_path)

            # Extract students who submitted
            if 'Status' in self.data_frame.columns and 'Full name' in self.data_frame.columns:
                submitted_students = self.data_frame[
                    self.data_frame['Status'] == 'Submitted for grading'
                ]['Full name'].tolist()

                self.names_of_students_submit = submitted_students
                return self.names_of_students_submit
            else:
                raise ValueError("Could not find required columns in gradebook CSV")
        except Exception as e:
            print(f"Error processing gradebook CSV: {e}")
            return []

    def get_submission(self, index):
        """
        Get a submission by index.

        Args:
            index: Index of the submission

        Returns:
            StudentSubmission: The submission at the specified index
        """
        if 0 <= index < len(self.submissions_list):
            return self.submissions_list[index]
        return None

    def get_submissions(self):
        """Get all submissions."""
        return self.submissions_list

    def get_submission_count(self):
        """
        Get the number of students who submitted the assignment.
        This is different from the number of processed submissions.

        Returns:
            int: Number of students who submitted
        """
        return len(self.names_of_students_submit)

    def update_dataframe(self):
        """
        Update the data_frame with submission text, grades, and feedback.

        Returns:
            pandas.DataFrame: Updated DataFrame
        """
        if self.data_frame is None:
            if not os.path.exists(self.gradebook_csv_file_path):
                raise FileNotFoundError(f"Gradebook CSV file not found: {self.gradebook_csv_file_path}")
            self.data_frame = pd.read_csv(self.gradebook_csv_file_path)

        # Create columns if they don't exist
        if 'Solution Text' not in self.data_frame.columns:
            self.data_frame['Solution Text'] = ""

        # Add submission text, grades, and feedback to dataframe
        for submission in self.submissions_list:
            mask = self.data_frame['Full name'] == submission.get_student_name()
            if any(mask):
                self.data_frame.loc[mask, 'Solution Text'] = submission.get_solution()

                # Update grade
                if submission.get_grade() is not None:
                    self.data_frame.loc[mask, 'Grade'] = submission.get_grade()

                # Update feedback
                if submission.get_feedback():
                    self.data_frame.loc[mask, 'Feedback comments'] = submission.get_feedback()
            else:
                print(f"Warning: Student {submission.get_student_name()} not found in gradebook")

        # Add text length statistics
        self.data_frame['Solution Length'] = self.data_frame['Solution Text'].str.len()

        return self.data_frame

    def export_to_csv(self, output_path=None):
        """
        Export the submissions data to a CSV file.

        Args:
            output_path: Optional path for the output file

        Returns:
            str: Path to the exported file
        """
        if output_path is None:
            output_path = f"{self.assignment_name}_grades.csv"

        # Make sure dataframe is updated
        self.update_dataframe()

        # Create a cleaner export version with just the essential columns
        columns_to_export = [
            'Identifier', 'Full name', 'Email address',
            'Status', 'Grade', 'Maximum Grade','Grade can be changed','Last modified (submission)','Online text',
            'Last modified(grade)','Feedback comments'
        ]

        # Only include columns that exist in the dataframe
        export_columns = [col for col in columns_to_export if col in self.data_frame.columns]

        export_df = self.data_frame[export_columns].copy()

        export_df.to_csv(output_path, index=False)
        print(f"\nExported grades and feedback to: {output_path}")

        return output_path