# c:\Users\johnw\OneDrive\Desktop\SentinelPC\src\gui\scrollable_frame.py
"""Custom scrollable frame widget for enhanced UI navigation.

This module provides a scrollable frame widget that can be used to add scrolling
capabilities (vertical and optionally horizontal) to any content that exceeds
the visible area.
"""

import tkinter as tk
from tkinter import ttk
import platform
from typing import Optional, Any


class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame widget using ttk that automatically adds scrollbars
    when needed. Supports vertical and optional horizontal scrolling via
    mouse wheel and scrollbars.
    """

    def __init__(
        self,
        container: tk.Misc,
        v_scroll: bool = True,
        h_scroll: bool = False,
        *args: Any,
        **kwargs: Any,
    ):
        """Initialize the scrollable frame.

        Args:
            container: The parent widget.
            v_scroll: If True, include a vertical scrollbar. Defaults to True.
            h_scroll: If True, include a horizontal scrollbar. Defaults to False.
            *args: Additional positional arguments for the ttk.Frame.
            **kwargs: Additional keyword arguments for the ttk.Frame.
        """
        super().__init__(container, *args, **kwargs)

        self.v_scroll = v_scroll
        self.h_scroll = h_scroll

        # --- Canvas ---
        # highlightthickness=0 removes the border around the canvas
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)

        # --- Scrollbars ---
        self.vsb: Optional[ttk.Scrollbar] = None
        self.hsb: Optional[ttk.Scrollbar] = None

        if self.v_scroll:
            self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vsb.set)

        if self.h_scroll:
            self.hsb = ttk.Scrollbar(
                self, orient="horizontal", command=self.canvas.xview
            )
            self.canvas.configure(xscrollcommand=self.hsb.set)

        # --- Inner Frame ---
        # This frame will hold the actual content and is placed inside the canvas
        self.inner_frame = ttk.Frame(self.canvas)
        # Create a window in the canvas for the inner_frame
        self.inner_frame_window_id = self.canvas.create_window(
            (0, 0), window=self.inner_frame, anchor="nw"
        )

        # --- Layout ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        if self.vsb:
            self.vsb.grid(row=0, column=1, sticky="ns")
        if self.hsb:
            self.hsb.grid(row=1, column=0, sticky="ew")

        # --- Bindings ---
        # Update scrollregion when the size of the inner frame changes
        self.inner_frame.bind("<Configure>", self._on_inner_frame_configure)
        # Update the inner frame's width when the canvas size changes
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        # Bind mouse wheel scrolling
        self._bind_mouse_wheel()

    def _on_inner_frame_configure(self, event: Optional[tk.Event] = None) -> None:
        """
        Callback when the size of the inner frame changes.
        Updates the canvas scrollregion to encompass the inner frame.
        """
        # Update the scroll region to match the size of the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        """
        Callback when the size of the canvas itself changes.
        Adjusts the width of the inner frame within the canvas to match the canvas width.
        This prevents the inner frame from staying small when the window is resized.
        """
        if self.h_scroll:
            # If horizontal scrolling is enabled, don't force width
            # Let the inner frame determine its own width based on content
            # self.canvas.itemconfigure(self.inner_frame_window_id) # No width setting
            pass  # Or potentially set a minwidth? For now, let it be natural.
        else:
            # If only vertical scrolling, make the inner frame fill the canvas width
            new_width = event.width
            self.canvas.itemconfigure(self.inner_frame_window_id, width=new_width)

        # Note: Height adjustment is implicitly handled by the scrollregion

    def _bind_mouse_wheel(self) -> None:
        """Binds mouse wheel events for scrolling."""
        # Determine the correct mouse wheel binding based on the platform
        os_name = platform.system()
        if os_name == "Linux":
            # Linux uses Button-4 (scroll up) and Button-5 (scroll down)
            self.canvas.bind("<Button-4>", self._on_mouse_wheel, add="+")
            self.canvas.bind("<Button-5>", self._on_mouse_wheel, add="+")
            # Shift+Scroll for horizontal
            self.canvas.bind(
                "<Shift-Button-4>", self._on_mouse_wheel_horizontal, add="+"
            )
            self.canvas.bind(
                "<Shift-Button-5>", self._on_mouse_wheel_horizontal, add="+"
            )
        elif os_name == "Windows":
            # Windows uses <MouseWheel>
            self.canvas.bind("<MouseWheel>", self._on_mouse_wheel, add="+")
            # Shift+Scroll for horizontal
            self.canvas.bind(
                "<Shift-MouseWheel>", self._on_mouse_wheel_horizontal, add="+"
            )
        else:  # macOS and others
            # macOS also uses <MouseWheel> (or potentially <Scroll> event)
            # Bind <MouseWheel> as a common default
            self.canvas.bind("<MouseWheel>", self._on_mouse_wheel, add="+")
            # Shift+Scroll for horizontal (assuming <MouseWheel> carries shift state or use specific binding if needed)
            # This might need refinement for macOS horizontal scrolling specifics if <Shift-MouseWheel> doesn't work directly
            self.canvas.bind(
                "<Shift-MouseWheel>", self._on_mouse_wheel_horizontal, add="+"
            )

        # Bind enter/leave to the *canvas* to ensure wheel events are captured when over content
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)

    def _on_enter(self, event: Optional[tk.Event] = None) -> None:
        """Focus the canvas when the mouse enters to ensure wheel events are captured."""
        # Optional: Set focus if needed, but binding directly often suffices
        # self.canvas.focus_set()
        pass

    def _on_leave(self, event: Optional[tk.Event] = None) -> None:
        """Optional actions when the mouse leaves the canvas."""
        pass

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        """Handle vertical mouse wheel scrolling."""
        if not self.v_scroll:
            return  # Do nothing if vertical scrolling is disabled

        delta = 0
        os_name = platform.system()

        if os_name == "Linux":
            if event.num == 4:  # Scroll up
                delta = -1
            elif event.num == 5:  # Scroll down
                delta = 1
        elif os_name == "Windows":
            # Windows delta is usually +/- 120
            delta = -1 * int(event.delta / 120)
        else:  # macOS and others (assuming delta attribute)
            # macOS delta can be smaller and variable, use sign
            if hasattr(event, "delta"):
                delta = -1 if event.delta > 0 else 1
            # Fallback if delta attribute isn't standard
            # This might need platform-specific adjustments

        if self.canvas.yview() != (0.0, 1.0):  # Check if scrollable
            self.canvas.yview_scroll(delta, "units")

    def _on_mouse_wheel_horizontal(self, event: tk.Event) -> None:
        """Handle horizontal mouse wheel scrolling (e.g., Shift+Wheel)."""
        if not self.h_scroll:
            return  # Do nothing if horizontal scrolling is disabled

        delta = 0
        os_name = platform.system()

        if os_name == "Linux":
            if event.num == 4:  # Shift+Scroll up (usually maps to scroll left)
                delta = -1
            elif event.num == 5:  # Shift+Scroll down (usually maps to scroll right)
                delta = 1
        elif os_name == "Windows":
            delta = -1 * int(event.delta / 120)
        else:  # macOS and others
            if hasattr(event, "delta"):
                delta = -1 if event.delta > 0 else 1

        if self.canvas.xview() != (0.0, 1.0):  # Check if scrollable
            self.canvas.xview_scroll(delta, "units")

    @property
    def frame(self) -> ttk.Frame:
        """
        Get the inner frame where content should be placed.

        Returns:
            ttk.Frame: The scrollable inner frame.
        """
        return self.inner_frame


# --- Example Usage (Optional) ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scrollable Frame Test")
    root.geometry("400x300")

    # Create a scrollable frame (vertical only)
    # scroll_frame = ScrollableFrame(root, v_scroll=True, h_scroll=False, relief=tk.SUNKEN, borderwidth=2)
    # scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create a scrollable frame (both vertical and horizontal)
    scroll_frame_both = ScrollableFrame(
        root, v_scroll=True, h_scroll=True, relief=tk.GROOVE, borderwidth=1
    )
    scroll_frame_both.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add content to the inner frame
    content_frame = scroll_frame_both.frame  # Get the inner frame

    for i in range(30):
        # Make some items wider to test horizontal scrolling
        width = 60 if i % 5 == 0 else 40
        ttk.Label(
            content_frame, text=f"Label {i+1}", width=width, relief=tk.RIDGE
        ).grid(row=i, column=0, padx=5, pady=2, sticky="ew")
        ttk.Button(content_frame, text=f"Button {i+1}").grid(
            row=i, column=1, padx=5, pady=2
        )

    # Example of adding a large widget to test horizontal scroll
    long_text = (
        "This is a very long piece of text designed to force horizontal scrolling if enabled. "
        * 5
    )
    ttk.Label(content_frame, text=long_text, anchor="w").grid(
        row=30, column=0, columnspan=2, padx=5, pady=10, sticky="ew"
    )

    root.mainloop()
