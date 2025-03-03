"""
Export utility functions for the Assignment Grader.

This module provides functions for exporting data to various formats.
"""

import csv
import os
import tempfile
from io import BytesIO


def export_statistics_to_csv(file_path, statistics):
    """
    Export statistics to a CSV file.

    Args:
        file_path: Path to save the CSV file
        statistics: List of (metric, value) tuples

    Returns:
        bool: True if export successful, False otherwise
        str: Success or error message
    """
    try:
        # Write to CSV
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Metric", "Value"])
            writer.writerows(statistics)

        return True, f"Statistics have been exported to:\n{file_path}"

    except Exception as e:
        return False, f"An error occurred while exporting statistics:\n{str(e)}"


def export_statistics_with_graphs(file_path, statistics, grade_figure=None, length_figure=None):
    """
    Export statistics report with graphs as HTML.

    Args:
        file_path: Path to save the HTML file
        statistics: List of (metric, value) tuples
        grade_figure: Matplotlib figure for grade distribution (optional)
        length_figure: Matplotlib figure for length distribution (optional)

    Returns:
        bool: True if export successful, False otherwise
        str: Success or error message
    """
    try:
        # Create base HTML
        html = "<html><head><title>Statistics Report</title>"
        html += "<style>"
        html += "body { font-family: Arial, sans-serif; margin: 40px; }"
        html += "h1, h2 { color: #2c3e50; }"
        html += "table { border-collapse: collapse; width: 100%; margin: 20px 0; }"
        html += "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }"
        html += "th { background-color: #f2f2f2; }"
        html += "tr:nth-child(even) { background-color: #f9f9f9; }"
        html += ".graphs { display: flex; justify-content: space-between; margin: 20px 0; }"
        html += ".graph { width: 48%; }"
        html += "</style></head><body>"

        # Add title
        html += "<h1>Statistics Report</h1>"

        # Add statistics table
        html += "<h2>Summary Statistics</h2>"
        html += "<table><tr><th>Metric</th><th>Value</th></tr>"
        for metric, value in statistics:
            html += f"<tr><td>{metric}</td><td>{value}</td></tr>"
        html += "</table>"

        # Add graphs if available
        if grade_figure or length_figure:
            graph_files = []
            html += "<h2>Visualizations</h2>"
            html += "<div class='graphs'>"

            # Add grade distribution graph
            if grade_figure:
                grade_img_path = f"{file_path}_grade_dist.png"
                grade_figure.savefig(grade_img_path, bbox_inches='tight')
                graph_files.append(grade_img_path)
                html += f"<div class='graph'><h3>Grade Distribution</h3>"
                html += f"<img src='{os.path.basename(grade_img_path)}' alt='Grade Distribution' width='100%'></div>"

            # Add length distribution graph
            if length_figure:
                length_img_path = f"{file_path}_length_dist.png"
                length_figure.savefig(length_img_path, bbox_inches='tight')
                graph_files.append(length_img_path)
                html += f"<div class='graph'><h3>Solution Length Distribution</h3>"
                html += f"<img src='{os.path.basename(length_img_path)}' alt='Solution Length Distribution' width='100%'></div>"

            html += "</div>"

        # Finish HTML
        html += "</body></html>"

        # Write HTML to file
        with open(file_path, 'w') as f:
            f.write(html)

        return True, f"Report with graphs has been exported to:\n{file_path}"

    except Exception as e:
        return False, f"An error occurred while exporting report with graphs:\n{str(e)}"


def create_statistics_report(assignment_name, statistics):
    """
    Create a formatted statistics report as a string.

    Args:
        assignment_name: Name of the assignment
        statistics: List of (metric, value) tuples

    Returns:
        str: Formatted report
    """
    report = f"Statistics Report for {assignment_name}\n"
    report += "=" * 50 + "\n\n"

    for metric, value in statistics:
        report += f"{metric}: {value}\n"

    report += "\n" + "=" * 50

    return report


def save_figure_to_bytes(figure):
    """
    Save a matplotlib figure to a bytes object.

    Args:
        figure: Matplotlib figure object

    Returns:
        bytes: Image data as bytes
    """
    buf = BytesIO()
    figure.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()


def get_graph_attachments(grade_figure=None, length_figure=None):
    """
    Get graph images as attachments for email.

    Args:
        grade_figure: Matplotlib figure for grade distribution (optional)
        length_figure: Matplotlib figure for length distribution (optional)

    Returns:
        list: List of (filename, image_data) tuples
    """
    attachments = []

    if grade_figure:
        grade_image = save_figure_to_bytes(grade_figure)
        attachments.append(("grade_distribution.png", grade_image))

    if length_figure:
        length_image = save_figure_to_bytes(length_figure)
        attachments.append(("length_distribution.png", length_image))

    return attachments