# c:\Users\johnw\OneDrive\Desktop\PC_Optimizer\src\gui\theme.py
import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

def apply_modern_theme(root: tk.Tk) -> ttk.Style:
    """
    Applies a refined modern theme to the application using ttk styles.

    Args:
        root: The root Tkinter window.

    Returns:
        The configured ttk.Style object.
    """
    logger.debug("Applying modern theme...")

    # --- Color Palette ---
    # Using a slightly adjusted palette for better contrast and modern feel
    COLOR_PRIMARY = "#007ACC"        # A standard, accessible blue
    COLOR_PRIMARY_ACTIVE = "#005F9E" # Darker blue for active/hover states
    COLOR_BG = "#F0F0F0"             # Light gray background (less stark than white)
    COLOR_CONTENT_BG = "#FFFFFF"     # White background for content areas like Text, Treeview
    COLOR_TEXT = "#212121"           # Dark gray for main text (good contrast)
    COLOR_TEXT_SECONDARY = "#757575" # Lighter gray for less important text
    COLOR_TEXT_ON_PRIMARY = "#FFFFFF" # White text for use on primary color backgrounds
    COLOR_SIDEBAR = "#E0E0E0"         # Slightly darker gray for sidebar differentiation
    COLOR_BORDER = "#BDBDBD"         # Subtle border color
    COLOR_DISABLED_FG = "#A0A0A0"    # Gray for disabled text
    COLOR_DISABLED_BG = "#D0D0D0"    # Lighter gray for disabled background elements
    COLOR_TREE_SELECT_BG = COLOR_PRIMARY # Use primary color for Treeview selection
    COLOR_TREE_SELECT_FG = COLOR_TEXT_ON_PRIMARY

    # --- Base Font ---
    # Using Segoe UI as primary, with fallbacks for other systems
    try:
        # Check if Segoe UI is available (simple check)
        root.tk.call('font', 'metrics', ('Segoe UI', 9))
        BASE_FONT = ('Segoe UI', 9)
        BOLD_FONT = ('Segoe UI', 9, 'bold')
        LARGE_BOLD_FONT = ('Segoe UI', 11, 'bold')
    except tk.TclError:
        logger.warning("Segoe UI font not found, using system default.")
        # Fallback fonts (consider adding more specific fallbacks if needed)
        BASE_FONT = ('Helvetica', 9) # Or ('Arial', 9) or system default
        BOLD_FONT = ('Helvetica', 9, 'bold')
        LARGE_BOLD_FONT = ('Helvetica', 11, 'bold')


    # --- Style Configuration ---
    style = ttk.Style(root)

    # Set a base theme for better customization ('clam' is often good)
    try:
        style.theme_use('clam')
        logger.debug("Using 'clam' theme as base.")
    except tk.TclError:
        logger.warning("Could not use 'clam' theme, using default.")
        # Fallback to default if 'clam' is not available

    # --- General Widget Styles ---
    style.configure('.',
                    background=COLOR_BG,
                    foreground=COLOR_TEXT,
                    font=BASE_FONT,
                    borderwidth=0, # Default to no border for a flatter look
                    focuscolor=COLOR_PRIMARY) # Default focus indicator color

    style.configure('TFrame', background=COLOR_BG)
    style.configure('TLabel', background=COLOR_BG, foreground=COLOR_TEXT)
    style.configure('TLabelframe', background=COLOR_BG, bordercolor=COLOR_BORDER, borderwidth=1)
    style.configure('TLabelframe.Label',
                    background=COLOR_BG,
                    foreground=COLOR_TEXT,
                    font=BOLD_FONT,
                    padding=(5, 2)) # Add some padding to labelframe titles

    # --- Header Style ---
    style.configure('Header.TFrame', background=COLOR_PRIMARY)
    style.configure('Header.TLabel',
                    background=COLOR_PRIMARY,
                    foreground=COLOR_TEXT_ON_PRIMARY,
                    font=LARGE_BOLD_FONT)

    # --- Sidebar Style ---
    style.configure('Sidebar.TFrame', background=COLOR_SIDEBAR)
    style.configure('Sidebar.TButton',
                    background=COLOR_SIDEBAR,
                    foreground=COLOR_TEXT,
                    font=BASE_FONT,
                    anchor='w', # Align text left
                    padding=(10, 8),
                    borderwidth=0)
    style.map('Sidebar.TButton',
              background=[('active', COLOR_BORDER), # Subtle gray on hover/press
                          ('!disabled', 'hover', COLOR_BORDER)], # Explicit hover
              foreground=[('active', COLOR_TEXT)])

    # --- Content Area Style ---
    style.configure('Content.TFrame', background=COLOR_CONTENT_BG) # White background for main content

    # --- Button Styles ---
    style.configure('TButton',
                    background=COLOR_PRIMARY,
                    foreground=COLOR_TEXT_ON_PRIMARY,
                    padding=(10, 6),
                    font=BOLD_FONT,
                    borderwidth=0,
                    relief=tk.FLAT) # Ensure flat look
    style.map('TButton',
              background=[('active', COLOR_PRIMARY_ACTIVE), # Darker when pressed
                          ('!disabled', 'hover', COLOR_PRIMARY_ACTIVE), # Explicit hover
                          ('disabled', COLOR_DISABLED_BG)],
              foreground=[('disabled', COLOR_DISABLED_FG)])

    # --- Entry and Text Widget Styles ---
    # Note: tk.Text is not a ttk widget, style its bg/fg directly where created
    style.configure('TEntry',
                    fieldbackground=COLOR_CONTENT_BG, # White background
                    foreground=COLOR_TEXT,
                    bordercolor=COLOR_BORDER,
                    borderwidth=1,
                    insertcolor=COLOR_TEXT, # Cursor color
                    padding=5)
    style.map('TEntry',
              bordercolor=[('focus', COLOR_PRIMARY)], # Highlight border on focus
              fieldbackground=[('disabled', COLOR_BG)], # Different bg when disabled
              foreground=[('disabled', COLOR_DISABLED_FG)])

    # --- Treeview Styles ---
    style.configure('Treeview',
                    background=COLOR_CONTENT_BG,
                    fieldbackground=COLOR_CONTENT_BG, # Background of the items area
                    foreground=COLOR_TEXT,
                    rowheight=28, # Slightly taller rows for readability
                    font=BASE_FONT)
    # Remove default borders
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    # Style selected items
    style.map('Treeview',
              background=[('selected', COLOR_TREE_SELECT_BG)],
              foreground=[('selected', COLOR_TREE_SELECT_FG)])

    # Style Treeview headings
    style.configure('Treeview.Heading',
                    background=COLOR_SIDEBAR,
                    foreground=COLOR_TEXT,
                    font=BOLD_FONT,
                    padding=(5, 5),
                    relief=tk.FLAT) # Flat headings
    style.map('Treeview.Heading',
              background=[('active', COLOR_BORDER), # Subtle feedback when clicking/hovering heading
                          ('hover', COLOR_BORDER)])

    # --- Scrollbar Style ---
    # Making scrollbars less obtrusive
    style.configure('Vertical.TScrollbar',
                    background=COLOR_SIDEBAR,
                    troughcolor=COLOR_BG,
                    borderwidth=0,
                    arrowsize=14,
                    relief=tk.FLAT)
    style.map('Vertical.TScrollbar',
              background=[('active', COLOR_BORDER)]) # When dragging

    style.configure('Horizontal.TScrollbar',
                    background=COLOR_SIDEBAR,
                    troughcolor=COLOR_BG,
                    borderwidth=0,
                    arrowsize=14,
                    relief=tk.FLAT)
    style.map('Horizontal.TScrollbar',
              background=[('active', COLOR_BORDER)])

    # --- Combobox Style ---
    # Inherits much from Entry/Button, but map specific states
    style.map('TCombobox',
              fieldbackground=[('readonly', COLOR_BG)], # Readonly background match main BG
              selectbackground=[('readonly', COLOR_BG)],
              selectforeground=[('readonly', COLOR_TEXT)],
              bordercolor=[('focus', COLOR_PRIMARY)],
              background=[('active', COLOR_PRIMARY_ACTIVE), # Button part hover
                          ('!disabled', 'hover', COLOR_PRIMARY_ACTIVE)])

    # --- Checkbutton Style ---
    style.configure('TCheckbutton',
                    background=COLOR_BG, # Match background
                    foreground=COLOR_TEXT,
                    indicatorcolor=COLOR_BORDER, # Default indicator color (box)
                    padding=(5, 5),
                    font=BASE_FONT)
    style.map('TCheckbutton',
              indicatorcolor=[('selected', COLOR_PRIMARY), # Color when checked
                              ('active', COLOR_PRIMARY)], # Color when hovered over
              background=[('active', COLOR_BG)]) # Keep background consistent on hover

    # --- Radiobutton Style (similar to Checkbutton) ---
    style.configure('TRadiobutton',
                    background=COLOR_BG,
                    foreground=COLOR_TEXT,
                    indicatorcolor=COLOR_BORDER,
                    padding=(5, 5),
                    font=BASE_FONT)
    style.map('TRadiobutton',
              indicatorcolor=[('selected', COLOR_PRIMARY),
                              ('active', COLOR_PRIMARY)],
              background=[('active', COLOR_BG)])

    # --- Configure Root Window Background ---
    # Set root background - useful for areas not covered by frames
    root.configure(bg=COLOR_BG)

    logger.debug("Modern theme applied successfully.")
    return style
