"""SentinelPC GUI Interface

This module provides the graphical user interface for SentinelPC.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
from ..core.sentinel_core import SentinelCore

class SentinelGUI:
    """Graphical user interface for SentinelPC."""
    
    def __init__(self, core: SentinelCore):
        """Initialize GUI interface.
        
        Args:
            core: Initialized SentinelCore instance
        """
        self.core = core
        self.root = tk.Tk()
        self.root.title(f"SentinelPC v{self.core.version}")
        self.root.geometry("800x600")
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the main GUI components."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # System Info Section
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.info_text = tk.Text(info_frame, height=8, width=70)
        self.info_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Optimization Controls
        control_frame = ttk.LabelFrame(main_frame, text="Optimization Controls", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Profile selection
        ttk.Label(control_frame, text="Profile:").grid(row=0, column=0, padx=5, pady=5)
        self.profile_var = tk.StringVar(value="default")
        profile_combo = ttk.Combobox(control_frame, textvariable=self.profile_var)
        profile_combo['values'] = ('default', 'performance', 'balanced', 'power-saver')
        profile_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Optimize button
        self.optimize_button = ttk.Button(
            control_frame,
            text="Start Optimization",
            command=self.run_optimization
        )
        self.optimize_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Optimization Results", padding="5")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.results_text = tk.Text(results_frame, height=12, width=70)
        self.results_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def update_system_info(self) -> None:
        """Update system information display."""
        info = self.core.get_system_info()
        self.info_text.delete(1.0, tk.END)
        if "error" in info:
            self.info_text.insert(tk.END, f"Error: {info['error']}")
            return
        
        for key, value in info.items():
            self.info_text.insert(tk.END, f"{key}: {value}\n")
    
    def display_optimization_results(self, results: Dict[str, Any]) -> None:
        """Display optimization results.
        
        Args:
            results: Dictionary containing optimization results
        """
        self.results_text.delete(1.0, tk.END)
        if not results["success"]:
            self.results_text.insert(tk.END, f"Optimization failed: {results.get('error')}")
            return
        
        self.results_text.insert(tk.END, "Initial State:\n")
        for key, value in results["initial_state"].items():
            self.results_text.insert(tk.END, f"  {key}: {value}\n")
        
        self.results_text.insert(tk.END, "\nOptimizations Performed:\n")
        for opt in results["optimizations"]:
            self.results_text.insert(tk.END, f"  - {opt}\n")
        
        self.results_text.insert(tk.END, "\nFinal State:\n")
        for key, value in results["final_state"].items():
            self.results_text.insert(tk.END, f"  {key}: {value}\n")
    
    def run_optimization(self) -> None:
        """Run optimization with selected profile."""
        self.optimize_button.state(['disabled'])
        self.status_var.set("Running optimization...")
        self.root.update()
        
        try:
            results = self.core.run_optimization(self.profile_var.get())
            self.display_optimization_results(results)
            self.status_var.set("Optimization complete")
        except Exception as e:
            messagebox.showerror("Error", f"Optimization failed: {str(e)}")
            self.status_var.set("Error during optimization")
        finally:
            self.optimize_button.state(['!disabled'])
    
    def run(self) -> None:
        """Start the GUI application."""
        self.update_system_info()
        self.root.mainloop()