"""
Utility functions for file handling.
"""

import os
import glob


def get_last_downloaded(extension):
    """
    Gets the most recently downloaded file with the given extension.

    Args:
        extension (str): File extension to search for (e.g., '.zip', '.csv')

    Returns:
        str: Path to the most recently downloaded file
    """
    # Adjust this path to your downloads directory
    downloads_dir = os.path.expanduser("~/Downloads")

    # Find all files with the specified extension
    files = glob.glob(os.path.join(downloads_dir, f"*{extension}"))

    if not files:
        raise FileNotFoundError(f"No files with extension {extension} found in {downloads_dir}")

    # Sort by modification time (most recent first)
    files.sort(key=os.path.getmtime, reverse=True)

    return files[0]


def ensure_dir_exists(path):
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        path: Path to directory

    Returns:
        str: Path to the directory
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_file_extension(filename):
    """
    Get the extension of a file.

    Args:
        filename: Name of the file

    Returns:
        str: Extension (with dot) or empty string if no extension
    """
    return os.path.splitext(filename)[1]