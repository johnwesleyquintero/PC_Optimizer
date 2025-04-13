"""Custom scrollable frame widget for enhanced UI navigation.

This module provides a scrollable frame widget that can be used to add scrolling
capabilities to any content that exceeds the visible area.
"""

import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    """A scrollable frame widget that automatically adds scrollbars when needed."""
    
    def __init__(self, container, *args, **kwargs):
        """Initialize the scrollable frame.
        
        Args:
            container: The parent widget
            *args: Additional positional arguments for the Frame
            **kwargs: Additional keyword arguments for the Frame
        """
        super().__init__(container, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Create the scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Add the frame to the canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scroll
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mouse wheel
        self.scrollable_frame.bind('<Enter>', self._bind_mouse_wheel)
        self.scrollable_frame.bind('<Leave>', self._unbind_mouse_wheel)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Bind canvas resize
        self.bind('<Configure>', self._on_frame_configure)
        
    def _on_frame_configure(self, event=None):
        """Handle frame resize events.
        
        Args:
            event: The event object (optional)
        """
        # Update the canvas's width to fit the inner frame
        self.canvas.configure(width=self.winfo_width())
    
    def _bind_mouse_wheel(self, event=None):
        """Bind mouse wheel to scroll.
        
        Args:
            event: The event object (optional)
        """
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
    
    def _unbind_mouse_wheel(self, event=None):
        """Unbind mouse wheel from scroll.
        
        Args:
            event: The event object (optional)
        """
        self.canvas.unbind_all("<MouseWheel>")
    
    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling.
        
        Args:
            event: The event object
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    @property
    def frame(self):
        """Get the inner frame.
        
        Returns:
            ttk.Frame: The scrollable inner frame
        """
        return self.scrollable_frame