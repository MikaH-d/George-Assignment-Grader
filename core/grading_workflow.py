"""
GradingWorkflow - Manages the interactive grading process

This module handles the user interaction for grading student submissions.
"""

from core.statistics import StatisticsCalculator


class GradingWorkflow:
    """
    Component for managing the interactive grading workflow.
    """

    def __init__(self, assignment):
        """
        Initialize with an assignment instance.

        Args:
            assignment: Assignment object to grade
        """
        self.assignment = assignment
        self.stats_calculator = StatisticsCalculator()

    def run(self):
        """
        Run the complete grading workflow.

        This implements the three-part workflow:
        1. Initialization (process files, get reference solution)
        2. Grading each submission
        3. Displaying statistics
        """
        # PART 1: Initialize from files
        self._initialize_assignment()

        # Ask for reference solution
        self._get_reference_solution()

        # PART 2: Grade each submission
        print("\nPress Enter to begin grading submissions...")
        input()
        self._grade_submissions()

        # PART 3: Display statistics
        self._display_statistics()

        # Export the grades
        self.assignment.export_to_csv()

    def _initialize_assignment(self):
        """
        Initialize the assignment from files.
        """
        print("Initializing assignment from files...")

        # Set assignment name
        assignment_name = self.assignment.set_assignment_name()
        print(f"Assignment name: {assignment_name}")

        # Load student names
        student_names = self.assignment.load_student_names()
        num_students_submitted = len(student_names)
        print(f"Found {num_students_submitted} student submissions in the gradebook.")

        # Load submissions
        _, submissions = self.assignment.load_submissions()
        num_processed = len(submissions)

        print(f"Successfully processed {num_processed} out of {num_students_submitted} submissions.")
        print(f"\nReady to grade submissions for '{assignment_name}'")

        # Print a warning if there's a mismatch between submitted and processed
        if num_processed < num_students_submitted:
            missing = num_students_submitted - num_processed
            print(f"\nWARNING: Could not process {missing} submissions. These students may have submitted",
                  "but their submissions were not found or could not be processed.")

    def _get_reference_solution(self):
        """
        Get the reference solution from the user.
        """
        print("\n--- REFERENCE SOLUTION ---")
        print("Please enter the reference solution for this assignment.")
        print("This will be used for future features such as auto-grading.")
        print("Type your solution below (type 'END' on a new line when finished):")

        solution_text = ""
        while True:
            line = input()
            if line.strip() == 'END':
                break
            solution_text += line + "\n"

        self.assignment.set_reference_solution(solution_text.strip())
        print("Reference solution has been saved.")

    def _grade_submissions(self):
        """
        Interactive grading process for each submission.
        """
        submissions = self.assignment.get_submissions()

        if not submissions:
            print("\nNo submissions to grade. Exiting grading process.")
            return

        print("\n--- GRADING SUBMISSIONS ---")
        print(f"There are {len(submissions)} submissions to grade.")

        for i, submission in enumerate(submissions):
            print(f"\n[Submission {i+1}/{len(submissions)}]")
            print(f"Student: {submission.get_student_name()}")
            print("-" * 50)
            print("SOLUTION:")
            print(submission.get_solution())
            print("-" * 50)

            # Ask for feedback
            print("Enter your feedback for this submission (type 'END' on a new line when finished):")
            feedback = ""
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                feedback += line + "\n"

            submission.set_feedback(feedback.strip())

            # Ask for grade
            while True:
                try:
                    grade_input = input("Enter grade (0-100): ")
                    grade = float(grade_input)
                    if 0 <= grade <= 100:
                        submission.set_grade(grade)
                        break
                    else:
                        print("Grade must be between 0 and 100.")
                except ValueError:
                    print("Please enter a valid number.")

        # Update the dataframe with the new grades and feedback
        self.assignment.update_dataframe()

        print("\nAll submissions have been graded!")

    def _display_statistics(self):
        """
        Display statistics about the assignment submissions.
        """
        submissions = self.assignment.get_submissions()
        data_frame = self.assignment.data_frame

        if not submissions:
            print("\n--- ASSIGNMENT STATISTICS ---")
            print(f"Assignment: {self.assignment.assignment_name}")
            print(f"Total students who submitted: {self.assignment.get_submission_count()}")
            print("No submissions were processed successfully.")
            return

        # Calculate statistics
        stats = self.stats_calculator.calculate_statistics(submissions, data_frame)

        # Display statistics
        print("\n--- ASSIGNMENT STATISTICS ---")
        print(f"Assignment: {self.assignment.assignment_name}")
        print(f"Total students who submitted: {self.assignment.get_submission_count()}")
        print(f"Submissions processed: {len(submissions)}")

        # Grade statistics
        if stats['grades']:
            print(f"Average grade: {stats['average_grade']:.2f}")
            print(f"Highest grade: {stats['max_grade']:.2f}")
            print(f"Lowest grade: {stats['min_grade']:.2f}")

        # Submission length statistics
        print(f"Average solution length: {stats['mean_length']:.2f} characters")
        print(f"Median solution length: {stats['median_length']:.2f} characters")
        print(f"Longest solution: {stats['max_length']} characters")
        print(f"Shortest solution: {stats['min_length']} characters")