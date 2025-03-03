"""
Core module for assignment grading functionality.
"""

from .assignment import Assignment
from .file_processor import FileProcessor
from .grading_workflow import GradingWorkflow
from .statistics import StatisticsCalculator

__all__ = ['Assignment', 'FileProcessor', 'GradingWorkflow', 'StatisticsCalculator']