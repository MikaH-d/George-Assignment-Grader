"""
Statistics tab for the Assignment Grader GUI using Tkinter.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import tempfile
import csv

from utils.export_utils import export_statistics_to_csv, export_statistics_with_graphs
from utils.email_utils import prepare_email_with_report

# For plotting with matplotlib in Tkinter
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class StatsTab:
    """Tab for displaying assignment statistics."""

    def __init__(self, parent, assignment, stats_calculator):
        """
        Initialize the statistics tab.

        Args:
            parent: Parent frame
            assignment: Assignment instance to work with
            stats_calculator: StatisticsCalculator instance
        """
        self.parent = parent
        self.assignment = assignment
        self.stats_calculator = stats_calculator
        self.stats = None

        # For storing figures
        self.grade_figure = None
        self.length_figure = None

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for this tab."""
        # Main frame with padding
        main_frame = ttk.Frame(self.parent, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        self.assignment_name_var = tk.StringVar(value="Assignment: Not loaded")
        assignment_label = ttk.Label(header_frame, textvariable=self.assignment_name_var, font=("TkDefaultFont", 12, "bold"))
        assignment_label.pack(side=tk.LEFT, padx=5)

        # Action buttons
        action_frame = ttk.Frame(header_frame)
        action_frame.pack(side=tk.RIGHT)

        self.export_btn = ttk.Button(action_frame, text="Export Grades", command=self.export_grades)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        self.export_stats_btn = ttk.Button(action_frame, text="Export Stats (CSV)", command=self.export_statistics)
        self.export_stats_btn.pack(side=tk.LEFT, padx=5)

        self.export_report_btn = ttk.Button(action_frame, text="Export Report (HTML)", command=self.export_report)
        self.export_report_btn.pack(side=tk.LEFT, padx=5)

        self.email_btn = ttk.Button(action_frame, text="Email Results", command=self.email_results)
        self.email_btn.pack(side=tk.LEFT, padx=5)

        # Summary statistics
        summary_group = ttk.LabelFrame(main_frame, text="Summary Statistics")
        summary_group.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Create a frame for the table
        table_frame = ttk.Frame(summary_group)
        table_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Create a treeview for the summary table
        columns = ("metric", "value")
        self.summary_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.summary_table.heading("metric", text="Metric")
        self.summary_table.heading("value", text="Value")
        self.summary_table.column("metric", width=200)
        self.summary_table.column("value", width=100)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.summary_table.yview)
        self.summary_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # If matplotlib is available, add visualizations
        if HAS_MATPLOTLIB:
            self._setup_charts(main_frame)
        else:
            # Display message if matplotlib is not available
            self._setup_matplotlib_message(main_frame)

    def _setup_charts(self, parent_frame):
        """Set up the charts if matplotlib is available."""
        # Create a frame for the plots
        plots_frame = ttk.Frame(parent_frame)
        plots_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Grade distribution
        grade_group = ttk.LabelFrame(plots_frame, text="Grade Distribution")
        grade_group.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Create figure for grade distribution
        self.grade_figure = Figure(figsize=(4, 3), dpi=100)
        self.grade_canvas = FigureCanvasTkAgg(self.grade_figure, master=grade_group)
        self.grade_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Solution length distribution
        length_group = ttk.LabelFrame(plots_frame, text="Solution Length Distribution")
        length_group.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Create figure for solution length distribution
        self.length_figure = Figure(figsize=(4, 3), dpi=100)
        self.length_canvas = FigureCanvasTkAgg(self.length_figure, master=length_group)
        self.length_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _setup_matplotlib_message(self, parent_frame):
        """Set up a message about missing matplotlib."""
        plots_frame = ttk.Frame(parent_frame)
        plots_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        ttk.Label(
            plots_frame,
            text="Matplotlib is not installed. Install it to view visualizations:\n" +
                 "pip install matplotlib",
            justify=tk.CENTER
        ).pack(padx=10, pady=10)

    def export_grades(self):
        """Export grades to a CSV file."""
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            title="Save Grades CSV",
            initialfile=f"{self.assignment.assignment_name}_grades.csv" if self.assignment.assignment_name else "grades.csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                # Export grades using the assignment's export method
                self.assignment.export_to_csv(file_path)

                # Show success message
                messagebox.showinfo(
                    "Export Successful",
                    f"Grades have been exported to:\n{file_path}"
                )
            except Exception as e:
                # Show error message
                messagebox.showerror(
                    "Export Error",
                    f"An error occurred while exporting grades:\n{str(e)}"
                )

    def export_statistics(self):
        """Export statistics to a CSV file."""
        if not self.stats:
            messagebox.showwarning("No Data", "No statistics available to export.")
            return

        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            title="Save Statistics CSV",
            initialfile=f"{self.assignment.assignment_name}_statistics.csv" if self.assignment.assignment_name else "statistics.csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            # Get the statistics from the table
            metrics = []
            for item_id in self.summary_table.get_children():
                metric, value = self.summary_table.item(item_id, 'values')
                metrics.append((metric, value))

            # Use the utility function to export
            success, message = export_statistics_to_csv(file_path, metrics)

            if success:
                messagebox.showinfo("Export Successful", message)
            else:
                messagebox.showerror("Export Error", message)

    def export_report(self):
        """Export a complete HTML report with graphs."""
        if not self.stats:
            messagebox.showwarning("No Data", "No statistics available to export.")
            return

        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            title="Save Report HTML",
            initialfile=f"{self.assignment.assignment_name}_report.html" if self.assignment.assignment_name else "report.html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
        )

        if file_path:
            # Get the statistics from the table
            metrics = []
            for item_id in self.summary_table.get_children():
                metric, value = self.summary_table.item(item_id, 'values')
                metrics.append((metric, value))

            # Use the utility function to export with graphs
            success, message = export_statistics_with_graphs(
                file_path,
                metrics,
                self.grade_figure if HAS_MATPLOTLIB else None,
                self.length_figure if HAS_MATPLOTLIB else None
            )

            if success:
                messagebox.showinfo("Export Successful", message)
            else:
                messagebox.showerror("Export Error", message)

    def email_results(self):
        """Send results via email using system's default email client."""
        # Check if we have statistics
        if not self.stats:
            messagebox.showwarning("No Data", "No statistics available to email.")
            return

        # Ask for recipient email
        recipient_email = simpledialog.askstring(
            "Email Results",
            "Enter recipient email address:",
            parent=self.parent
        )

        if not recipient_email:
            return

        try:
            # Export grades to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_grades_file:
                grades_path = temp_grades_file.name
                self.assignment.export_to_csv(grades_path)

            # Export statistics to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_stats_file:
                stats_path = temp_stats_file.name

                # Get the statistics
                metrics = []
                for item_id in self.summary_table.get_children():
                    metric, value = self.summary_table.item(item_id, 'values')
                    metrics.append((metric, value))

                # Write to CSV
                with open(stats_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Metric", "Value"])
                    writer.writerows(metrics)

            # Export HTML report if matplotlib is available
            report_path = None
            if HAS_MATPLOTLIB:
                with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp_report_file:
                    report_path = temp_report_file.name
                    export_statistics_with_graphs(
                        report_path,
                        metrics,
                        self.grade_figure,
                        self.length_figure
                    )

            # Prepare and open email client
            success, message = prepare_email_with_report(
                recipient_email,
                self.assignment.assignment_name,
                stats_path,
                grades_path,
                report_path
            )

            if success:
                messagebox.showinfo("Email Client Opened", message)
            else:
                messagebox.showerror("Email Error", message)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            # Clean up temporary files
            for path in [grades_path, stats_path]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except:
                        pass

            if report_path and os.path.exists(report_path):
                try:
                    os.unlink(report_path)
                except:
                    pass

    def update_statistics(self):
        """Update the statistics display."""
        # Get the assignment name
        self.assignment_name_var.set(f"Assignment: {self.assignment.assignment_name}")

        # Calculate statistics
        submissions = self.assignment.get_submissions()
        if not submissions:
            messagebox.showwarning(
                "No Data",
                "No submissions to analyze. Please check the grading process."
            )
            return

        self.stats = self.stats_calculator.calculate_statistics(
            submissions,
            self.assignment.data_frame
        )

        # Update summary table
        self._update_summary_table()

        # Update plots if matplotlib is available
        if HAS_MATPLOTLIB:
            self._update_grade_distribution()
            self._update_length_distribution()

    def _update_summary_table(self):
        """Update the summary statistics table."""
        # Clear the table
        for item in self.summary_table.get_children():
            self.summary_table.delete(item)

        if not self.stats:
            return

        # Define metrics to display
        metrics = [
            ("Total students who submitted", self.assignment.get_submission_count()),
            ("Submissions processed", self.stats['submission_count']),
            ("Average grade", f"{self.stats['average_grade']:.2f}"),
            ("Highest grade", f"{self.stats['max_grade']:.1f}"),
            ("Lowest grade", f"{self.stats['min_grade']:.1f}"),
            ("Grade standard deviation", f"{self.stats['grade_stddev']:.2f}"),
            ("Average solution length", f"{self.stats['mean_length']:.0f} characters"),
            ("Median solution length", f"{self.stats['median_length']:.0f} characters"),
            ("Longest solution", f"{self.stats['max_length']} characters"),
            ("Shortest solution", f"{self.stats['min_length']} characters")
        ]

        # Add rows to the table
        for metric, value in metrics:
            self.summary_table.insert("", tk.END, values=(metric, value))

    def _update_grade_distribution(self):
        """Update the grade distribution plot."""
        if not self.stats or not self.stats['grades']:
            return

        # Clear the plot
        ax = self.grade_figure.gca()
        ax.clear()

        # Create histogram
        ax.hist(self.stats['grades'], bins=10, edgecolor='black', alpha=0.7)

        # Add labels and title
        ax.set_xlabel('Grade')
        ax.set_ylabel('Number of Submissions')
        ax.set_title('Grade Distribution')

        # Set x-axis range
        ax.set_xlim(0, 100)

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)

        # Redraw
        self.grade_figure.tight_layout()
        self.grade_canvas.draw()

    def _update_length_distribution(self):
        """Update the solution length distribution plot."""
        if not self.stats or self.stats['mean_length'] == 0:
            return

        # Clear the plot
        ax = self.length_figure.gca()
        ax.clear()

        # Get length distribution
        bin_edges, counts = self.stats_calculator.calculate_length_distribution(
            self.assignment.data_frame,
            bins=10
        )

        # Create bar chart
        x = range(len(counts))

        ax.bar(x, counts, width=0.8, edgecolor='black', alpha=0.7)

        # Add labels
        labels = [f"{int(bin_edges[i])} - {int(bin_edges[i+1])}" for i in range(len(bin_edges)-1)]
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')

        # Add title and labels
        ax.set_xlabel('Solution Length (characters)')
        ax.set_ylabel('Number of Submissions')
        ax.set_title('Solution Length Distribution')

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)

        # Redraw
        self.length_figure.tight_layout()
        self.length_canvas.draw()