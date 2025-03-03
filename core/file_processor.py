"""
FileProcessor - Component for processing submission files

This module handles extracting submissions from ZIP and CSV files.
"""

import os
import re
import zipfile
import pandas as pd

from models.student_submission import StudentSubmission


class FileProcessor:
    """
    Component for extracting submissions from various file sources.
    """

    def extract_submissions(self, gradebook_path, zip_path, student_names):
        """
        Extract student submissions from gradebook and zip files.

        Args:
            gradebook_path: Path to the gradebook CSV file
            zip_path: Path to the submissions ZIP file
            student_names: List of student names who submitted

        Returns:
            list: List of StudentSubmission objects
        """
        # Use a dictionary to store submissions by student name
        # This ensures each student only has one submission (with all files merged)
        submissions_dict = {}

        # Load gradebook data
        data_frame = pd.read_csv(gradebook_path)

        # First extract submissions from online text
        online_submissions = self._extract_online_submissions(data_frame)

        # Add online submissions to the dictionary
        for submission in online_submissions:
            student_name = submission.get_student_name()
            submissions_dict[student_name] = submission

        # Then extract submissions from the zip file
        if os.path.exists(zip_path):
            zip_submissions = self._extract_zip_submissions(
                zip_path, student_names, set(submissions_dict.keys()), data_frame
            )

            # For each zip submission, check if we already have a submission for this student
            for submission in zip_submissions:
                student_name = submission.get_student_name()

                if student_name in submissions_dict:
                    # If we already have a submission for this student, merge the solutions
                    existing_submission = submissions_dict[student_name]

                    # Merge the solutions with a clear separator
                    combined_solution = (
                        existing_submission.get_solution() +
                        "\n\n--- ADDITIONAL SUBMISSION ---\n\n" +
                        submission.get_solution()
                    )

                    existing_submission.set_solution(combined_solution)
                    print(f"Merged multiple submissions for {student_name}")
                else:
                    # If this is the first submission for this student, add it
                    submissions_dict[student_name] = submission

        # Convert the dictionary back to a list
        submissions = list(submissions_dict.values())

        # Sort by student name for consistent ordering
        submissions.sort(key=lambda sub: sub.get_student_name())

        return submissions

    def _extract_online_submissions(self, data_frame):
        """
        Extract submissions from the online text field in the gradebook.

        Args:
            data_frame: Pandas DataFrame with gradebook data

        Returns:
            list: List of StudentSubmission objects
        """
        submissions = []

        for idx, row in data_frame.iterrows():
            if row['Status'] == 'Submitted for grading':
                student_name = row['Full name']

                # Check if there's online text
                if pd.notna(row.get('Online text')) and row['Online text'].strip():
                    # Create submission and set the online text
                    submission = StudentSubmission(idx, student_name)

                    # Let the StudentSubmission process the online text
                    submission.process_online_text(row['Online text'])

                    # Set metadata
                    self._set_submission_metadata(submission, row, idx)

                    submissions.append(submission)

        return submissions

    def _extract_zip_submissions(self, zip_path, student_names, processed_students, data_frame):
        """
        Extract submissions from a zip file, merging multiple files for the same student.

        Args:
            zip_path: Path to the zip file
            student_names: List of student names from the gradebook
            processed_students: Set of students already processed from online text
            data_frame: Pandas DataFrame with gradebook data

        Returns:
            list: List of StudentSubmission objects
        """
        # Dictionary to store submissions by folder (to collect all files)
        folder_submissions = {}

        folder_contents = self._group_files_by_folder(zip_path)

        with zipfile.ZipFile(zip_path, mode='r') as zip_file:
            # Process each folder
            for folder, files in folder_contents.items():
                # Find solution files in this folder
                solution_files = [f for f in files if self._is_solution_file(f)]

                if not solution_files:
                    continue

                # Extract student name from the folder
                student_name = self._extract_student_name_from_path(folder, student_names)

                # Skip if we already have this student's submission from online text
                if student_name in processed_students:
                    print(f"Skipping zip folder for {student_name}, already processed from online text")
                    continue

                # If this is the first file for this folder, create a new submission
                if folder not in folder_submissions:
                    idx = len(folder_submissions)
                    submission = StudentSubmission(idx, student_name)
                    folder_submissions[folder] = submission

                    # Set metadata from gradebook if available
                    student_row = data_frame[data_frame['Full name'] == student_name]
                    if not student_row.empty:
                        row = student_row.iloc[0]
                        self._set_submission_metadata(submission, row, idx)
                else:
                    submission = folder_submissions[folder]

                # Process all solution files and merge them
                for i, solution_file in enumerate(solution_files):
                    with zip_file.open(solution_file, mode='r') as f:
                        file_content = self._parse_file_to_text(f, solution_file)

                        # First file or adding to existing content
                        if i == 0 and not submission.get_solution():
                            submission.set_solution(file_content)
                        else:
                            # Add a separator with the filename to make it clear this is a different file
                            filename = os.path.basename(solution_file)
                            merged_content = (
                                submission.get_solution() +
                                f"\n\n--- FILE: {filename} ---\n\n" +
                                file_content
                            )
                            submission.set_solution(merged_content)

        # Convert the dictionary to a list
        return list(folder_submissions.values())

    def _group_files_by_folder(self, zip_path):
        """
        Group files in a zip file by their parent folder.

        Args:
            zip_path: Path to the zip file

        Returns:
            dict: Dictionary mapping folder paths to lists of file paths
        """
        folder_contents = {}

        with zipfile.ZipFile(zip_path, mode='r') as zip_file:
            for file_info in zip_file.infolist():
                if file_info.is_dir():
                    continue

                # Extract the folder path (student identifier)
                folder_path = os.path.dirname(file_info.filename)
                if not folder_path:
                    continue  # Skip files in the root of the zip

                if folder_path not in folder_contents:
                    folder_contents[folder_path] = []

                folder_contents[folder_path].append(file_info.filename)

        return folder_contents

    def _extract_student_name_from_path(self, file_path, student_names):
        """
        Extract student name from a file path by matching against known names.

        Args:
            file_path: Path to match against
            student_names: List of known student names

        Returns:
            str: Matched student name or the folder name
        """
        # Get the folder name
        folder_name = os.path.basename(file_path)

        # Try to match against known student names
        for student_name in student_names:
            # Create simplified versions for comparison
            simplified_folder = re.sub(r'[^a-zA-Z0-9]', '', folder_name.lower())
            simplified_student = re.sub(r'[^a-zA-Z0-9]', '', student_name.lower())

            # Check if the student name is contained in the folder name
            if simplified_student in simplified_folder or simplified_folder in simplified_student:
                return student_name

        # Try to extract a name using patterns
        matches = re.findall(r'[A-Z]+\s*[A-Z]+', folder_name)
        if matches:
            return matches[0]

        # Last resort: return the folder name
        return folder_name

    def _is_solution_file(self, filename):
        """
        Determine if a file is likely to be a student solution based on name and extension.

        Args:
            filename: Name of the file to check

        Returns:
            bool: True if the file is likely a solution, False otherwise
        """
        valid_extensions = ['.txt', '.docx', '.pdf', '.html']
        if any(filename.lower().endswith(ext) for ext in valid_extensions):
            # Exclude files that are likely not solutions
            excluded_keywords = ['readme', 'instruction', 'guide', 'syllabus']
            base_name = os.path.basename(filename).lower()
            if not any(keyword in base_name for keyword in excluded_keywords):
                return True
        return False

    def _parse_file_to_text(self, file_obj, filename):
        """
        Parse a file to extract its text content.
        This is a simplified version - in production, use StudentSubmission.parse_file_to_text
        """
        from models.student_submission import StudentSubmission
        dummy_submission = StudentSubmission(0, "temp")
        return dummy_submission.parse_file_to_text(file_obj, filename)

    def _set_submission_metadata(self, submission, row, idx):
        """
        Set metadata for a submission from a gradebook row.

        Args:
            submission: StudentSubmission object to update
            row: Pandas Series with gradebook data
            idx: Index for default ID generation
        """
        submission.set_identifier(row.get('Identifier', f"ID_{idx}"))
        if 'Email address' in row:
            submission.set_email(row.get('Email address', ''))

        # Set grade if available
        if pd.notna(row.get('Grade')):
            submission.set_grade(row.get('Grade'))

        # Set feedback if available
        if pd.notna(row.get('Feedback comments')):
            submission.set_feedback(row.get('Feedback comments'))