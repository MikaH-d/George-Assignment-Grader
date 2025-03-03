"""
Image utilities for the Assignment Grader.

This module handles loading, processing, and converting images
for display in the Tkinter GUI.
"""

import io
import os
import tempfile
import zipfile
from PIL import Image, ImageTk


def create_tk_image(image_data, max_width=400, max_height=300):
    """
    Convert image data to a Tkinter-compatible PhotoImage.

    Args:
        image_data: PIL Image object or raw image data
        max_width: Maximum width for the displayed image
        max_height: Maximum height for the displayed image

    Returns:
        ImageTk.PhotoImage or None if conversion fails
    """
    try:
        # If image_data is already a PIL Image
        if isinstance(image_data, Image.Image):
            img = image_data
        else:
            # Otherwise, open it from raw data
            img = Image.open(io.BytesIO(image_data))

        # Resize image to fit within maximum dimensions while preserving aspect ratio
        img.thumbnail((max_width, max_height), Image.LANCZOS)

        # Convert to Tkinter-compatible format
        photo = ImageTk.PhotoImage(img)
        return photo
    except Exception as e:
        print(f"Error creating Tkinter image: {e}")
        return None


def is_image_file(filename):
    """
    Check if a file is an image based on its extension.

    Args:
        filename: Name of the file to check

    Returns:
        bool: True if the file is likely an image, False otherwise
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    return any(filename.lower().endswith(ext) for ext in image_extensions)


def extract_images_from_docx(docx_path, output_dir):
    """
    Extract all images from a Word document.

    Args:
        docx_path: Path to the docx file
        output_dir: Directory to save extracted images

    Returns:
        list: Paths to extracted images
    """
    extracted_files = []

    try:
        # Word documents are zip files containing media
        with zipfile.ZipFile(docx_path) as zf:
            # List all files in the zip
            file_list = zf.namelist()

            # Extract all files that appear to be images
            for file_path in file_list:
                if file_path.startswith('word/media/'):
                    # Extract to the output directory
                    zf.extract(file_path, output_dir)

                    # Get the extracted file path
                    extracted_path = os.path.join(output_dir, file_path)

                    # Move to a simpler location
                    simple_name = os.path.basename(file_path)
                    new_path = os.path.join(output_dir, simple_name)

                    if os.path.exists(extracted_path):
                        # Ensure the destination directory exists
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)

                        # Move the file
                        os.rename(extracted_path, new_path)
                        extracted_files.append(new_path)
    except Exception as e:
        print(f"Error extracting docx images: {e}")

    return extracted_files


def create_test_image(width=200, height=200, color='red', text='Test'):
    """
    Create a test image for debugging purposes.

    Args:
        width: Width of the test image
        height: Height of the test image
        color: Background color
        text: Text to display

    Returns:
        PIL.Image: A test image
    """
    from PIL import ImageDraw

    # Create a new image with a solid color
    img = Image.new('RGB', (width, height), color=color)

    # Draw something on it
    draw = ImageDraw.Draw(img)
    draw.rectangle([width//4, height//4, width*3//4, height*3//4], fill='blue')
    draw.text((width//4 + 10, height//4 + 10), text, fill='white')

    return img