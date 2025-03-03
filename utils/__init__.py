"""
Utilities module for common functions.
"""

from .file_utils import get_last_downloaded, ensure_dir_exists, get_file_extension
from .text_utils import clean_html, truncate_text, normalize_student_name

__all__ = [
    'get_last_downloaded', 'ensure_dir_exists', 'get_file_extension',
    'clean_html', 'truncate_text', 'normalize_student_name'
]