"""
Email client utility functions for the Assignment Grader.

This module provides functions for composing emails using the system's default email client.
"""

import os
import webbrowser
import tempfile
import urllib.parse


def open_email_client(recipient, subject, body, attachments=None):
    """
    Open the system's default email client with a pre-composed message.

    Args:
        recipient: Recipient email address
        subject: Email subject
        body: Email body text
        attachments: List of file paths to attach (optional)

    Returns:
        bool: True if successful, False otherwise
        str: Success or error message
    """
    try:
        # URL encode the parameters
        subject_encoded = urllib.parse.quote(subject)
        body_encoded = urllib.parse.quote(body)

        # Create the mailto URL
        mailto_url = f"mailto:{recipient}?subject={subject_encoded}&body={body_encoded}"

        # Open the default email client
        webbrowser.open(mailto_url)

        # Note about attachments
        if attachments:
            attachment_list = "\n".join([f"- {os.path.basename(a)}" for a in attachments])
            return True, f"Email client opened with pre-filled message.\n\nPlease manually attach the following files:\n{attachment_list}"
        else:
            return True, "Email client opened with pre-filled message."

    except Exception as e:
        return False, f"An error occurred while opening the email client:\n{str(e)}"


def prepare_email_with_report(recipient, assignment_name, stats_csv_path, grades_csv_path, report_html_path=None):
    """
    Prepare an email with assignment report and attachments.

    Args:
        recipient: Recipient email address
        assignment_name: Name of the assignment
        stats_csv_path: Path to statistics CSV file
        grades_csv_path: Path to grades CSV file
        report_html_path: Path to HTML report (optional)

    Returns:
        bool: True if successful, False otherwise
        str: Success or error message
    """
    # Create the subject
    subject = f"Assignment Results: {assignment_name}"

    # Create the body
    body = f"""Assignment: {assignment_name}

I've attached the grading results for {assignment_name}.

The attachments include:
1. Complete grades (CSV)
2. Statistics summary (CSV)
"""

    if report_html_path:
        body += "3. Complete report with visualizations (HTML)\n"

    body += "\nPlease let me know if you have any questions.\n"

    # List of attachments
    attachments = [grades_csv_path, stats_csv_path]
    if report_html_path:
        attachments.append(report_html_path)

    # Open the email client
    return open_email_client(recipient, subject, body, attachments)