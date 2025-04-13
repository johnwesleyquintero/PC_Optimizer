import tkinter as tk
from tkinter import ttk

def apply_modern_theme(root):
    """Apply a modern theme to the application."""
    # Configure colors
    primary_color = "#00BCD4"  # Turquoise blue for header and accents
    bg_color = "#FFFFFF"       # White background
    text_color = "#333333"     # Dark gray text
    sidebar_color = "#F5F5F5"  # Light gray sidebar
    
    # Configure styles
    style = ttk.Style(root)
    style.configure('TFrame', background=bg_color)
    style.configure('TLabelframe', background=bg_color)
    style.configure('TLabelframe.Label', background=bg_color, foreground=text_color)
    
    # Header style
    style.configure('Header.TFrame', background=primary_color)
    style.configure('Header.TLabel', 
                    background=primary_color,
                    foreground='white',
                    font=('Segoe UI', 12, 'bold'))
    
    # Sidebar style
    style.configure('Sidebar.TFrame', background=sidebar_color)
    style.configure('Sidebar.TButton',
                    background=sidebar_color,
                    foreground=text_color,
                    font=('Segoe UI', 10),
                    padding=10)
    
    # Content area style
    style.configure('Content.TFrame', background=bg_color)
    
    # Button styles
    style.configure('TButton',
                    background=primary_color,
                    foreground=text_color,
                    padding=(10, 5),
                    font=('Segoe UI', 9))
    style.map('TButton',
              background=[('active', primary_color)],
              foreground=[('active', 'white')])
    
    # Entry and Text widget styles
    style.configure('TEntry',
                    fieldbackground=bg_color,
                    foreground=text_color,
                    padding=5)
    
    # Treeview styles
    style.configure('Treeview',
                    background=bg_color,
                    foreground=text_color,
                    rowheight=25,
                    font=('Segoe UI', 9))
    style.configure('Treeview.Heading',
                    background=sidebar_color,
                    foreground=text_color,
                    font=('Segoe UI', 9, 'bold'))
    
    # Configure root window
    root.configure(bg=bg_color)
    
    return style