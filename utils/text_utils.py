"""
Utility functions for text processing.
"""

import re


def clean_html(html_text):
    """
    Remove HTML tags from text.

    Args:
        html_text: Text containing HTML tags

    Returns:
        str: Clean text with HTML tags removed
    """
    if not isinstance(html_text, str) or not html_text:
        return ""

    if '<' in html_text and '>' in html_text:
        # Replace <br> with newlines
        text = re.sub(r'<br\s*/?>', '\n', html_text)
        # Remove all other tags
        text = re.sub(r'<[^>]+>', '', text)
        # Replace HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&gt;', '>')
        text = text.replace('&lt;', '<')
        text = text.replace('&amp;', '&')
        return text
    return html_text


def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length] + suffix


def normalize_student_name(name):
    """
    Normalize a student name for comparison.

    Args:
        name: Student name

    Returns:
        str: Normalized name
    """
    if not name:
        return ""

    # Remove non-alphanumeric characters and convert to lowercase
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())