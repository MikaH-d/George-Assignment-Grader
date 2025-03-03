"""
Styling module for the Assignment Grader GUI.

This module provides custom styling for the Tkinter interface.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont

from PyQt5.QtGui import QHoverEvent


def apply_custom_style(root):
    """
    Apply custom styling to the entire application.

    Args:
        root: The root Tkinter window
    """
    # Define color scheme
    colors = {
        'butter': '#F5F5DC',  # Light yellow/cream
        'light_blue': '#e5f5ff',
        'nude' : '#f2f2f2',
        'medium_blue': '#4682B4',
        'dark_blue': '#1E3F66',
        'light_red': '#FFB6C1',
        'medium_red': '#CD5C5C',
        'dark_red': '#8B0000',
        'text_dark': '#333333',
        'text_light': '#eecd8f'

    }

    # Create a ttk style
    style = ttk.Style(root)

    # Set default font size
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=12)

    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=13)

    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(size=12)

    # Apply the style to different widgets


    # TFrame
    style.configure('TFrame', background=colors['butter'])

    # TLabel
    style.configure('TLabel', background=colors['butter'], foreground=colors['text_dark'], font=('TkDefaultFont', 12))

    # TButton
    style.configure('TButton',
                   background=colors['medium_blue'],
                   foreground=colors['dark_blue'],
                   font=('TkDefaultFont', 12, 'bold'))

    style.map('TButton',
             background=[('active', colors['dark_blue']), ('disabled', 'light_blue')],
             foreground=[('disabled', 'dark_blue')])

    # # Navigation buttons
    # style.configure('Nav.TButton',
    #                background=colors['medium_blue'],
    #                foreground=colors['dark_blue'],
    #                padding=(10, 5),
    #                font=('TkDefaultFont', 12, 'bold'))

    # Finish button
    style.configure('Finish.TButton',
                   background=colors['medium_red'],
                   foreground=colors['text_light'],
                   padding=(10, 5),
                   font=('TkDefaultFont', 12, 'bold'))

    style.map('Finish.TButton',
             background=[('active', colors['dark_red']), ('disabled', '#cccccc')])

    # TProgressbar
    style.configure('TProgressbar',
                   background=colors['medium_blue'],
                   troughcolor=colors['light_blue'])

    # TNotebook (tabs)
    style.configure('TNotebook', background=colors['butter'])
    style.configure('TNotebook.Tab',
                   background=colors['light_blue'],
                   foreground=colors['text_dark'],
                   padding=(10, 5),
                   font=('TkDefaultFont', 12))

    style.map('TNotebook.Tab',
             background=[('selected', colors['medium_blue']), ('active', colors['medium_blue'])],
             foreground=[('selected', colors['text_dark']), ('active', colors['text_dark'])])

    # TLabelframe (groups)
    style.configure('TLabelframe', background=colors['butter'])
    style.configure('TLabelframe.Label',
                   background=colors['butter'],
                   foreground=colors['dark_blue'],
                   font=('TkDefaultFont', 12, 'bold'))

    # TPanedWindow
    style.configure('TPanedwindow', background=colors['butter'])

    # TSpinbox
    style.configure('TSpinbox',
                   font=('TkDefaultFont', 12),
                   fieldbackground=colors['light_blue'])

    # TEntry
    style.configure('TEntry',
                   font=('TkDefaultFont', 12),
                   fieldbackground=colors['light_blue'])

    # Configure the root window
    root.configure(background=colors['butter'])

    # Custom buttons for ImageViewer
    style.configure(
        "TButton",
        background="light blue",
        foreground="dark red",
        padding=(10, 5),
        QHoverEvent=lambda e: e.widget.config(background="red"),
        QLeaveEvent=lambda e: e.widget.config(background="light blue"),
        # font=("Helvetica", 10, "italic")
    )
    style.map(
        "TButton",
        background=[('active', "light red"), ('disabled', "light blue")],
        foreground=[('active', "dark red"), ('disabled', "dark blue")]
    )

    # Custom function to configure Text and ScrolledText widgets
    def configure_text_widgets(widget):
        if isinstance(widget, (tk.Text, tk.scrolledtext.ScrolledText)):
            widget.configure(
                font=('TkTextFont', 12),
                background=colors['light_blue'],
                foreground=colors['text_dark'],
                selectbackground=colors['medium_blue'],
                selectforeground=colors['text_light'],
                padx=5,
                pady=5,
                wrap=tk.WORD
            )

        # Recursively apply to all children
        for child in widget.winfo_children():
            configure_text_widgets(child)

    # Apply text widget styling after a short delay to ensure all widgets are created
    root.after(100, lambda: configure_text_widgets(root))

    return colors