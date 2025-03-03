"""
ImageViewer component for displaying images in the Assignment Grader GUI.
"""

import tkinter as tk
from tkinter import ttk

from utils.image_utils import create_tk_image


class ImageViewer(tk.Frame):
    """
    A component to display and browse images in a submission.
    """

    def __init__(self, parent, images=None):
        """
        Initialize the image viewer.

        Args:
            parent: Parent widget
            images: List of Tkinter PhotoImage objects
        """
        super().__init__(parent)

        self.images = images or []
        self.current_index = 0
        self.photo_references = []  # Keep references to prevent garbage collection

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        # Top controls
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)

        self.prev_btn = ttk.Button(controls_frame, text="Previous", command=self.previous_image, style='Nav.TButton')
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = ttk.Button(controls_frame, text="Next", command=self.next_image, style='Nav.TButton')
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.counter_label = ttk.Label(controls_frame, text="Image 0 of 0")
        self.counter_label.pack(side=tk.RIGHT, padx=5)

        # Image display area
        self.image_frame = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.image_label = ttk.Label(self.image_frame, text="No images available")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # Image description
        self.description_var = tk.StringVar()
        description_label = ttk.Label(self, textvariable=self.description_var)
        description_label.pack(fill=tk.X, padx=5, pady=5)

    def set_images(self, submission):
        """
        Set the images to display from a submission.

        Args:
            submission: StudentSubmission object containing images
        """
        # Clear existing images and references
        self.images = []
        self.photo_references = []
        self.current_index = 0

        if submission and submission.has_images():
            print(f"Loading {len(submission.get_images())} images from submission")

            # Get Tkinter-compatible images from the submission
            for i in range(len(submission.get_images())):
                image_data, image_format, description = submission.get_images()[i]

                # Create a Tkinter-compatible image
                photo = create_tk_image(image_data)

                if photo:
                    self.photo_references.append(photo)  # Keep reference to prevent garbage collection
                    self.images.append({
                        'image': photo,
                        'description': description
                    })
                    print(f"Loaded image {i+1}: {description}")
                else:
                    print(f"Failed to load image {i+1}")

            # If we have images, show the viewer and update display
            if self.images:
                print(f"Showing image viewer with {len(self.images)} images")
                self.update_image()
                self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            else:
                print("No valid images to display")
                self.pack_forget()
        else:
            print("No images in submission")
            self.pack_forget()

    def update_image(self):
        """Update the displayed image based on the current index."""
        if not self.images:
            self.counter_label.config(text="Image 0 of 0")
            self.image_label.config(text="No images available", image=None)
            self.description_var.set("")
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            return

        # Update the image
        current_image = self.images[self.current_index]
        print(f"Displaying image {self.current_index + 1} of {len(self.images)}")

        # Use the photo reference we've kept
        photo = current_image['image']

        # Force using the image from our references list to prevent garbage collection
        image_ref = self.photo_references[self.current_index]
        self.image_label.config(image=image_ref, text="")

        # Update counter and description
        self.counter_label.config(text=f"Image {self.current_index + 1} of {len(self.images)}")
        self.description_var.set(current_image['description'])

        # Update button states
        self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.images) - 1 else tk.DISABLED)

    def previous_image(self):
        """Display the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def next_image(self):
        """Display the next image."""
        if self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.update_image()

    def test_image(self):
        """Create and display a test image for debugging."""
        from utils.image_utils import create_test_image

        # Create a test image
        test_img = create_test_image()

        # Convert to PhotoImage
        photo = create_tk_image(test_img)

        # Keep reference
        self.photo_references = [photo]

        # Add to images list
        self.images = [{
            'image': photo,
            'description': 'Test image for debugging'
        }]

        # Update display
        self.current_index = 0
        self.update_image()

        # Show the viewer
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)