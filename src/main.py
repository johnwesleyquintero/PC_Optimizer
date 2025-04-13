import argparse
import sys
import tkinter as tk
from tkinter import ttk
import logging
from src.core.sentinel_pc import SentinelPC
from .core.sentinel_core import SentinelCore

class SentinelPCApp:
    def __init__(self, root, core):
        self.root = root
        self.core = core
        self.sentinel = SentinelPC()
        self.root.title(f"SentinelPC v{SentinelPC.VERSION}")
        self.setup_ui()

    def setup_ui(self):
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Header
        header = ttk.Label(
            self.root,
            text="SentinelPC System Optimizer",
            font=("Helvetica", 16)
        )
        header.grid(row=0, column=0, pady=10, sticky="ew")

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Optimize button
        optimize_btn = ttk.Button(
            main_frame,
            text="Optimize System",
            command=self.optimize_system
        )
        optimize_btn.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack(pady=5)

    def optimize_system(self):
        try:
            self.status_label.config(text="Optimizing...")
            self.root.update()
            
            if self.sentinel.optimize_system():
                self.status_label.config(text="Optimization completed successfully!")
            else:
                self.status_label.config(text="Optimization completed with some issues.")
        except Exception as e:
            logging.error(f"Optimization failed: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='SentinelPC - System Optimization Tool')
    parser.add_argument('--version', action='version', version=f'SentinelPC {SentinelPC.VERSION}')
    
    args = parser.parse_args()
    
    core = SentinelCore()
    root = tk.Tk()
    app = SentinelPCApp(root, core)
    try:
        root.mainloop()
    finally:
        core.shutdown()

if __name__ == "__main__":
    main()