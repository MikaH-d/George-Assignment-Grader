"""
StatisticsCalculator - Calculates statistics for student submissions

This module handles statistical analysis of submission data.
"""

import pandas as pd
import numpy as np


class StatisticsCalculator:
    """
    Component for calculating statistics on student submissions.
    """

    def calculate_statistics(self, submissions, data_frame):
        """
        Calculate comprehensive statistics for submissions.

        Args:
            submissions: List of StudentSubmission objects
            data_frame: Pandas DataFrame with submission data

        Returns:
            dict: Statistics dictionary with various metrics
        """
        # Basic counts
        stats = {
            'submission_count': len(submissions)
        }

        # Grade statistics
        grades = [sub.get_grade() for sub in submissions if sub.get_grade() is not None]
        stats['grades'] = grades

        if grades:
            stats['average_grade'] = sum(grades) / len(grades)
            stats['max_grade'] = max(grades)
            stats['min_grade'] = min(grades)
            stats['grade_stddev'] = np.std(grades) if len(grades) > 1 else 0
        else:
            stats['average_grade'] = 0
            stats['max_grade'] = 0
            stats['min_grade'] = 0
            stats['grade_stddev'] = 0

        # Solution length statistics - only include submissions that were actually processed
        if 'Solution Text' in data_frame.columns:
            solution_lengths = data_frame[data_frame['Solution Text'].notna() &
                                         (data_frame['Solution Text'] != '')]['Solution Length']

            if not solution_lengths.empty:
                stats['mean_length'] = solution_lengths.mean()
                stats['median_length'] = solution_lengths.median()
                stats['max_length'] = solution_lengths.max()
                stats['min_length'] = solution_lengths.min()
                stats['length_stddev'] = solution_lengths.std() if len(solution_lengths) > 1 else 0
            else:
                stats['mean_length'] = 0
                stats['median_length'] = 0
                stats['max_length'] = 0
                stats['min_length'] = 0
                stats['length_stddev'] = 0
        else:
            # If Solution Text column doesn't exist
            stats['mean_length'] = 0
            stats['median_length'] = 0
            stats['max_length'] = 0
            stats['min_length'] = 0
            stats['length_stddev'] = 0

        return stats

    def calculate_length_distribution(self, data_frame, bins=10):
        """
        Calculate the distribution of solution lengths.

        Args:
            data_frame: Pandas DataFrame with submission data
            bins: Number of bins for the distribution

        Returns:
            tuple: (bin_edges, counts) - numpy arrays for histogram data
        """
        if 'Solution Text' not in data_frame.columns:
            return np.array([0, 1]), np.array([0])

        solution_lengths = data_frame[data_frame['Solution Text'].notna() &
                                     (data_frame['Solution Text'] != '')]['Solution Length']

        if solution_lengths.empty:
            return np.array([0, 1]), np.array([0])

        hist, bin_edges = np.histogram(solution_lengths, bins=bins)
        return bin_edges, hist

    def calculate_grade_distribution(self, submissions, bins=10):
        """
        Calculate the distribution of grades.

        Args:
            submissions: List of StudentSubmission objects
            bins: Number of bins for the distribution

        Returns:
            tuple: (bin_edges, counts) - numpy arrays for histogram data
        """
        grades = [sub.get_grade() for sub in submissions if sub.get_grade() is not None]

        if not grades:
            return np.array([0, 100]), np.array([0])

        hist, bin_edges = np.histogram(grades, bins=bins, range=(0, 100))
        return bin_edges, hist