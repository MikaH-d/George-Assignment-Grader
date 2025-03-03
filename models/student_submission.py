"""
StudentSubmission class - Model for a student's submission.
"""

import re
import io
import tempfile
import html2text
import docx2txt
from PyPDF2 import PdfReader
import filetype
import os
from PIL import Image

from utils.image_utils import is_image_file, extract_images_from_docx


class StudentSubmission:
    """Class representing a single student's submission."""

    def __init__(self, submission_id, student_name):
        """Initialize a new StudentSubmission instance."""
        self.submission_id = submission_id
        self.student_name = student_name
        self.identifier = ""
        self.email = ""
        self.solution = ""
        self.grade = None
        self.feedback = ""
        # List to store images found in the submission
        # Each entry is a tuple of (image_data, image_format, description)
        self.images = []

    def set_solution(self, solution_text):
        """Set the solution text for this student submission"""
        self.solution = solution_text
        return self.solution

    def get_solution(self):
        """Get the solution text for this student submission"""
        return self.solution

    def add_image(self, image_data, image_format="", description=""):
        """
        Add an image to this submission.

        Args:
            image_data: Raw image data or PIL Image object
            image_format: Format of the image (e.g., 'png', 'jpeg')
            description: Description or context of the image

        Returns:
            int: Index of the added image
        """
        self.images.append((image_data, image_format, description))
        return len(self.images) - 1

    def get_images(self):
        """
        Get all images in this submission.

        Returns:
            list: List of tuples (image_data, image_format, description)
        """
        return self.images

    def has_images(self):
        """
        Check if this submission has any images.

        Returns:
            bool: True if there are images, False otherwise
        """
        return len(self.images) > 0

    def get_image_tk(self, index, max_width=400, max_height=300):
        """
        Get a Tkinter-compatible image object for the specified image.
        This is a placeholder that should be implemented by the image viewer, not here.

        Args:
            index: Index of the image to retrieve
            max_width: Maximum width for the displayed image
            max_height: Maximum height for the displayed image

        Returns:
            None - this should be handled by the GUI code
        """
        # This method should no longer be in StudentSubmission
        # It's now the responsibility of the GUI components
        from utils.image_utils import create_tk_image

        if 0 <= index < len(self.images):
            image_data, _, _ = self.images[index]
            return create_tk_image(image_data, max_width, max_height)
        return None

    def get_student_name(self):
        """Get the name of the student"""
        return self.student_name

    def set_grade(self, grade):
        """Set the grade for this submission"""
        self.grade = grade
        return self.grade

    def get_grade(self):
        """Get the grade for this submission"""
        return self.grade

    def set_feedback(self, feedback):
        """Set feedback for this submission"""
        self.feedback = feedback
        return self.feedback

    def get_feedback(self):
        """Get feedback for this submission"""
        return self.feedback

    def set_identifier(self, identifier):
        """Set the student identifier"""
        self.identifier = identifier
        return self.identifier

    def get_identifier(self):
        """Get the student identifier"""
        return self.identifier

    def set_email(self, email):
        """Set the student email"""
        self.email = email
        return self.email

    def get_email(self):
        """Get the student email"""
        return self.email

    def process_solution_file(self, file_obj, filename):
        """
        Process a solution file and set the solution text.
        Also extracts any images found in the file.

        Args:
            file_obj: File-like object with the solution
            filename: Name of the file

        Returns:
            str: The extracted solution text
        """
        # Check if this is an image file
        if is_image_file(filename):
            file_data = file_obj.read()
            try:
                # Add the image to our list
                img = Image.open(io.BytesIO(file_data))
                self.add_image(
                    img,
                    os.path.splitext(filename)[1][1:],  # Format without the dot
                    f"Image from file: {os.path.basename(filename)}"
                )
                solution_text = f"[Image file: {os.path.basename(filename)}]"
                self.set_solution(solution_text)
                return solution_text
            except Exception as e:
                print(f"Error processing image file {filename}: {e}")
                solution_text = f"[Error processing image file: {os.path.basename(filename)}]"
                self.set_solution(solution_text)
                return solution_text

        # Process regular document files
        solution_text = self.parse_file_to_text(file_obj, filename)
        self.set_solution(solution_text)
        return solution_text

    def process_online_text(self, online_text):
        """
        Process online text submission and set the solution text.
        Extracts embedded images if present.

        Args:
            online_text: HTML text from online submission

        Returns:
            str: The cleaned solution text
        """
        # Check for embedded images in HTML
        img_tags = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>', online_text)

        for img_src in img_tags:
            # Note: For embedded images, we would need to fetch them from the LMS
            # Here we just make a note in the solution text
            online_text = online_text.replace(
                f'src="{img_src}"',
                f'src="{img_src}" alt="[Embedded image - not displayed]"'
            )

        cleaned_text = self.clean_html_text(online_text)
        self.set_solution(cleaned_text)
        return cleaned_text

    def parse_file_to_text(self, file_obj, filename):
        """
        Parse a file object to extract text content and images.

        Args:
            file_obj: File-like object to parse
            filename: Name of the file (used to determine type)

        Returns:
            str: Extracted text content
        """
        file_data = file_obj.read()
        file_obj.seek(0)  # Reset file pointer

        # Determine parsing method based on file extension
        if filename.lower().endswith('.txt'):
            return self._parse_text_file(file_data)
        elif filename.lower().endswith('.docx'):
            return self._parse_docx_file(file_data, filename)
        elif filename.lower().endswith('.pdf'):
            return self._parse_pdf_file(file_data, filename)
        elif filename.lower().endswith('.html'):
            return self._parse_html_file(file_data)
        elif filename.lower().endswith('.reg'):
            return file_data.decode("utf-16").strip()
        elif is_image_file(filename):
            # Add image to the images list
            try:
                img = Image.open(io.BytesIO(file_data))
                self.add_image(
                    img,
                    os.path.splitext(filename)[1][1:],
                    f"Image from file: {os.path.basename(filename)}"
                )
                return f"[Image file: {os.path.basename(filename)}]"
            except Exception as e:
                print(f"Error processing image file {filename}: {e}")
                return f"[Error processing image file: {os.path.basename(filename)}]"

        # Use filetype detection for other formats
        return self._parse_by_file_type(file_data, filename)

    def _parse_text_file(self, file_data):
        """Parse a text file with various encodings."""
        try:
            return file_data.decode('utf-8').strip()
        except UnicodeDecodeError:
            try:
                return file_data.decode('utf-16').strip()
            except UnicodeDecodeError:
                return file_data.decode('latin-1', errors='ignore').strip()

    def _parse_docx_file(self, file_data, filename):
        """
        Parse a docx file using a temporary file.
        Also extracts images if available.
        """
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        try:
            # Create a temp directory for images
            with tempfile.TemporaryDirectory() as img_dir:
                # Extract text using docx2txt
                text = docx2txt.process(temp_path, img_dir)

                # Extract images directly from the docx file
                extract_images_from_docx(temp_path, img_dir)

                # Check for images and add them to our list
                for img_filename in os.listdir(img_dir):
                    if os.path.isdir(os.path.join(img_dir, img_filename)):
                        continue  # Skip directories

                    if is_image_file(img_filename):
                        img_path = os.path.join(img_dir, img_filename)
                        try:
                            with open(img_path, 'rb') as img_file:
                                img_data = img_file.read()

                            # Load and add the image
                            img = Image.open(io.BytesIO(img_data))
                            self.add_image(
                                img,
                                os.path.splitext(img_filename)[1][1:],
                                f"Image from document: {os.path.basename(filename)}"
                            )
                        except Exception as e:
                            print(f"Error processing extracted image {img_filename}: {e}")

            os.unlink(temp_path)

            # Add a note about images if any were found
            if self.has_images():
                text += f"\n\n[This document contains {len(self.images)} image(s)]"

            return text.strip()
        except Exception as e:
            os.unlink(temp_path)
            print(f"Error processing .docx file {filename}: {e}")
            return ""

    def _parse_pdf_file(self, file_data, filename):
        """
        Parse a PDF file using PyPDF2.
        Note: This simple implementation doesn't extract images from PDFs.
        """
        try:
            content = ""
            for page in PdfReader(stream=io.BytesIO(file_data)).pages:
                content += f"{page.extract_text()}\n"

            # Note: For comprehensive PDF image extraction, you would need a more
            # sophisticated library like pdftoppm or a commercial PDF library
            content += "\n[Note: Images in PDF files are not automatically extracted]"

            return content.strip()
        except Exception as e:
            print(f"Error processing PDF file {filename}: {e}")
            return ""

    def _parse_html_file(self, file_data):
        """Parse an HTML file using html2text."""
        return html2text.html2text(file_data.decode(errors='ignore')).strip()

    def _parse_by_file_type(self, file_data, filename):
        """Parse files using filetype detection."""
        type_guess = filetype.guess(io.BytesIO(file_data))

        if type_guess:
            mime = type_guess.mime

            if mime.startswith('image/'):
                # It's an image
                try:
                    img = Image.open(io.BytesIO(file_data))
                    self.add_image(
                        img,
                        mime.split('/')[1],
                        f"Image from file: {os.path.basename(filename)}"
                    )
                    return f"[Image file: {os.path.basename(filename)}]"
                except Exception as e:
                    print(f"Error processing image {filename}: {e}")
                    return f"[Error processing image: {os.path.basename(filename)}]"

            elif mime == 'application/msword' or mime == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return self._parse_docx_file(file_data, filename)

            elif mime == 'application/pdf':
                return self._parse_pdf_file(file_data, filename)

            else:
                print(f"Unsupported file type for {filename}: {mime}")
                return f"[Unsupported file type: {mime}]"
        else:
            # If filetype can't determine the type, try to decode as text
            try:
                return file_data.decode().strip()
            except UnicodeDecodeError:
                return "Binary data of unsupported file type"

    def clean_html_text(self, html_text):
        """
        Clean HTML tags from text.

        Args:
            html_text: Text containing HTML tags

        Returns:
            str: Text with HTML tags removed
        """
        if not isinstance(html_text, str) or not html_text:
            return ""

        if '<' in html_text and '>' in html_text:
            # Simple HTML tag removal
            text = re.sub(r'<br\s*/?>', '\n', html_text)
            text = re.sub(r'<[^>]+>', '', text)
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&gt;', '>')
            text = text.replace('&lt;', '<')
            text = text.replace('&amp;', '&')
            return text
        return html_text

    def calculate_solution_length(self):
        """
        Calculate the length of the solution text.

        Returns:
            int: Length of the solution text
        """
        return len(self.solution) if self.solution else 0

    def __repr__(self):
        """String representation of the object"""
        solution_preview = self.solution[:50] + "..." if self.solution and len(self.solution) > 50 else self.solution or "No solution"
        grade_str = f", grade={self.grade}" if self.grade is not None else ""
        images_str = f", images={len(self.images)}" if self.images else ""
        return f"StudentSubmission(id={self.submission_id}, name='{self.student_name}'{grade_str}{images_str})"