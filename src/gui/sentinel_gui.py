"""SentinelPC GUI Interface

This module provides the graphical user interface for SentinelPC.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from ..core.sentinel_core import SentinelCore
from .gui_worker import GUIWorker

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
        
        # Initialize worker thread
        self.worker = GUIWorker()
        self.worker.start()
        
        self.setup_ui()
        
        # Start processing results
        self.worker.process_results(self.root)
    
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
        
        # Disk Usage Section
        disk_frame = ttk.LabelFrame(main_frame, text="Disk Usage", padding="5")
        disk_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.disk_text = tk.Text(disk_frame, height=4, width=70)
        self.disk_text.grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(disk_frame, text="Refresh", command=self.update_disk_usage).grid(row=0, column=1, padx=5, pady=5)
        
        # Startup Programs Section
        startup_frame = ttk.LabelFrame(main_frame, text="Startup Programs", padding="5")
        startup_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.startup_list = ttk.Treeview(startup_frame, columns=("Program", "Status"), show="headings")
        self.startup_list.heading("Program", text="Program")
        self.startup_list.heading("Status", text="Status")
        self.startup_list.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        startup_btn_frame = ttk.Frame(startup_frame)
        startup_btn_frame.grid(row=1, column=0, columnspan=2)
        ttk.Button(startup_btn_frame, text="Enable", command=lambda: self.manage_startup("enable")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(startup_btn_frame, text="Disable", command=lambda: self.manage_startup("disable")).grid(row=0, column=1, padx=5, pady=5)
        
        # Optimization Controls
        control_frame = ttk.LabelFrame(main_frame, text="Optimization Controls", padding="5")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
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
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.results_text = tk.Text(results_frame, height=12, width=70)
        self.results_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
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
        """Run system optimization with selected profile."""
        def on_optimization_complete(results: Optional[Dict[str, Any]], error: str = None) -> None:
            if error:
                messagebox.showerror("Error", f"Failed to optimize system: {error}")
            else:
                self.display_optimization_results(results)
            self.status_var.set("Ready")
            self.optimize_button.state(['!disabled'])
        
        self.status_var.set("Optimizing...")
        self.optimize_button.state(['disabled'])
        
        self.worker.add_task(
            lambda: self.core.optimize_system(self.profile_var.get()),
            on_optimization_complete
        )
    
    def update_disk_usage(self) -> None:
        """Update disk usage information display."""
        def on_complete(result: Optional[Dict[str, Any]], error: str = None) -> None:
            self.disk_text.delete(1.0, tk.END)
            if error:
                self.disk_text.insert(tk.END, f"Error: {error}")
                return
            
            for device, info in result['data'].items():
                total_gb = info['total'] / (1024**3)
                used_gb = info['used'] / (1024**3)
                free_gb = info['free'] / (1024**3)
                self.disk_text.insert(tk.END, 
                    f"{device}: {free_gb:.1f}GB free of {total_gb:.1f}GB ({info['percent']}% used)\n")
        
        self.worker.add_task(self.core.get_disk_usage, on_complete)
    
    def manage_startup(self, action: str) -> None:
        """Manage startup programs.
        
        Args:
            action: Either 'enable' or 'disable'
        """
        selection = self.startup_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a program first")
            return
        
        program = self.startup_list.item(selection[0])['values'][0]
        
        def on_complete(result: Optional[Dict[str, bool]], error: str = None) -> None:
            if error:
                messagebox.showerror("Error", f"Failed to {action} program: {error}")
            else:
                self.update_startup_list()
        
        self.worker.add_task(
            lambda: self.core.manage_startup_programs(action, program),
            on_complete
        )
    
    def update_startup_list(self) -> None:
        """Update the startup programs list."""
        # Implementation depends on the core functionality
        pass
    
    def run(self) -> None:
        """Start the GUI application."""
        self.update_system_info()
        self.update_disk_usage()
        try:
            self.root.mainloop()
        finally:
            self.worker.stop()