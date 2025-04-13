# c:\Users\johnw\OneDrive\Desktop\PC_Optimizer\src\gui\sentinel_gui.py
"""SentinelPC GUI Interface

This module provides the graphical user interface for SentinelPC.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from typing import Dict, Any, Optional, Tuple, List

# Attempt to import PIL for image handling, provide fallback/warning if missing
try:
    from PIL import Image, ImageTk
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False
    Image = None
    ImageTk = None

from ..core.sentinel_core import SentinelCore
from .gui_worker import GUIWorker
from .scrollable_frame import ScrollableFrame
from . import theme # Assuming theme.py exists and apply_modern_theme is defined

logger = logging.getLogger(__name__)

class SentinelGUI:
    """Graphical user interface for SentinelPC."""

    # Interval for updating system metrics (in milliseconds)
    METRICS_UPDATE_INTERVAL = 2000 # Update every 2 seconds

    def __init__(self, core: SentinelCore):
        """Initialize GUI interface.

        Args:
            core: Initialized SentinelCore instance
        """
        logger.info("Initializing SentinelGUI...")
        self.core = core
        self.root = tk.Tk()
        self.root.title(f"SentinelPC v{self.core.version}")
        self.root.geometry("850x650") # Slightly larger default size

        # Initialize worker thread
        self.worker = GUIWorker()
        self.worker.start()

        self._setup_styles_and_grid()
        self._create_widgets()

        # Start processing results from the worker queue
        self.worker.process_results(self.root)

        # Schedule initial data loading and periodic updates
        self._schedule_initial_updates()
        self._schedule_metrics_update() # Start periodic metric updates

        logger.info("SentinelGUI initialized successfully.")

    def _setup_styles_and_grid(self) -> None:
        """Apply theme and configure root window grid."""
        self.style = theme.apply_modern_theme(self.root)

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)    # Main content area row
        self.root.grid_columnconfigure(1, weight=1) # Main content area column

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        self._create_header()
        self._create_sidebar()
        self._create_content_area()
        self._create_status_bar() # Moved status bar creation here

    def _create_header(self) -> None:
        """Create the header section with title and metrics."""
        header_frame = ttk.Frame(self.root, style='Header.TFrame')
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        header_frame.grid_columnconfigure(1, weight=1) # Allow content to expand

        # --- Icon ---
        icon_label = ttk.Label(header_frame, style='Header.TLabel')
        icon_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5, sticky=tk.W)
        if _PIL_AVAILABLE:
            try:
                # Construct path relative to this file
                base_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(base_dir, 'assets', 'shield_icon_small.png') # Example: using a PNG
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    # Resize if needed, e.g., img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    self.shield_icon = ImageTk.PhotoImage(img)
                    icon_label.configure(image=self.shield_icon)
                else:
                    logger.warning(f"Icon file not found: {icon_path}")
                    icon_label.configure(text="🛡️") # Fallback text/emoji
            except Exception as e:
                logger.error(f"Failed to load icon: {e}")
                icon_label.configure(text="🛡️") # Fallback text/emoji
        else:
            logger.warning("Pillow (PIL) library not found. Icon display disabled.")
            icon_label.configure(text="🛡️") # Fallback text/emoji

        # --- Title ---
        title_label = ttk.Label(header_frame, text="SENTINEL PC Optimizer", style='Header.TLabel', font=('Segoe UI', 14, 'bold'))
        title_label.grid(row=0, column=1, padx=5, pady=(5,0), sticky=tk.W)

        # --- Metrics Display ---
        metrics_frame = ttk.Frame(header_frame, style='Header.TFrame')
        metrics_frame.grid(row=1, column=1, padx=5, pady=(0,5), sticky=tk.W)

        self.cpu_label = ttk.Label(metrics_frame, text="CPU: --.-%", style='Header.TLabel', width=12)
        self.cpu_label.pack(side=tk.LEFT, padx=(0, 15))

        self.memory_label = ttk.Label(metrics_frame, text="Memory: --.-%", style='Header.TLabel', width=15)
        self.memory_label.pack(side=tk.LEFT)

    def _create_sidebar(self) -> None:
        """Create the sidebar navigation."""
        sidebar_frame = ttk.Frame(self.root, style='Sidebar.TFrame', width=180)
        sidebar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sidebar_frame.grid_propagate(False) # Prevent resizing based on content
        sidebar_frame.grid_rowconfigure(4, weight=1) # Push exit button down

        # Add navigation buttons with commands
        ttk.Button(sidebar_frame, text="System Info", style='Sidebar.TButton', command=self.update_system_info).grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(sidebar_frame, text="Disk Usage", style='Sidebar.TButton', command=self.update_disk_usage).grid(row=1, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(sidebar_frame, text="Startup Programs", style='Sidebar.TButton', command=self.update_startup_list).grid(row=2, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(sidebar_frame, text="Optimization", style='Sidebar.TButton', command=self._focus_optimization_section).grid(row=3, column=0, padx=10, pady=5, sticky=tk.EW)

        # Exit Button
        ttk.Button(sidebar_frame, text="Exit", style='Sidebar.TButton', command=self.root.quit).grid(row=5, column=0, padx=10, pady=10, sticky=(tk.EW, tk.S))


    def _create_content_area(self) -> None:
        """Create the main scrollable content area and its sections."""
        main_scroll_frame = ScrollableFrame(self.root)
        main_scroll_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame = main_scroll_frame.frame # Get the inner frame
        self.content_frame.configure(style='Content.TFrame', padding="15")
        self.content_frame.grid_columnconfigure(0, weight=1) # Allow content to expand horizontally

        # --- System Info Section ---
        info_frame = ttk.LabelFrame(self.content_frame, text="System Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)
        self.info_text = tk.Text(info_frame, height=8, width=70, relief=tk.FLAT, bg=self.style.lookup('Content.TFrame', 'background'))
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        # Add scrollbar if needed, though ScrollableFrame handles the main scroll
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text['yscrollcommand'] = info_scrollbar.set

        # --- Disk Usage Section ---
        disk_frame = ttk.LabelFrame(self.content_frame, text="Disk Usage", padding="10")
        disk_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        disk_frame.grid_columnconfigure(0, weight=1)
        self.disk_text = tk.Text(disk_frame, height=5, width=70, relief=tk.FLAT, bg=self.style.lookup('Content.TFrame', 'background'))
        self.disk_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        disk_scrollbar = ttk.Scrollbar(disk_frame, orient=tk.VERTICAL, command=self.disk_text.yview)
        disk_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        self.disk_text['yscrollcommand'] = disk_scrollbar.set
        ttk.Button(disk_frame, text="Refresh", command=self.update_disk_usage).grid(row=1, column=0, columnspan=2, pady=(0,5))

        # --- Startup Programs Section ---
        startup_frame = ttk.LabelFrame(self.content_frame, text="Startup Programs", padding="10")
        startup_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        startup_frame.grid_columnconfigure(0, weight=1)
        self.startup_list = ttk.Treeview(startup_frame, columns=("Program", "Path", "Status"), show="headings", height=6)
        self.startup_list.heading("Program", text="Program")
        self.startup_list.heading("Path", text="Path/Command")
        self.startup_list.heading("Status", text="Status")
        self.startup_list.column("Program", width=200, anchor=tk.W)
        self.startup_list.column("Path", width=350, anchor=tk.W)
        self.startup_list.column("Status", width=100, anchor=tk.CENTER)
        self.startup_list.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        startup_scrollbar = ttk.Scrollbar(startup_frame, orient=tk.VERTICAL, command=self.startup_list.yview)
        startup_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        self.startup_list['yscrollcommand'] = startup_scrollbar.set

        startup_btn_frame = ttk.Frame(startup_frame, style='Content.TFrame')
        startup_btn_frame.grid(row=1, column=0, columnspan=2, pady=(0,5))
        ttk.Button(startup_btn_frame, text="Enable", command=lambda: self.manage_startup("enable")).pack(side=tk.LEFT, padx=5)
        ttk.Button(startup_btn_frame, text="Disable", command=lambda: self.manage_startup("disable")).pack(side=tk.LEFT, padx=5)
        ttk.Button(startup_btn_frame, text="Refresh List", command=self.update_startup_list).pack(side=tk.LEFT, padx=5)

        # --- Optimization Controls Section ---
        self.control_frame = ttk.LabelFrame(self.content_frame, text="Optimization Controls", padding="10") # Store reference
        self.control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(self.control_frame, text="Profile:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.profile_var = tk.StringVar(value="default")
        # TODO: Consider fetching profiles dynamically from core if they change
        profile_combo = ttk.Combobox(self.control_frame, textvariable=self.profile_var, state="readonly")
        profile_combo['values'] = ('default', 'performance', 'balanced', 'power-saver')
        profile_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.optimize_button = ttk.Button(
            self.control_frame,
            text="Start Optimization",
            command=self.run_optimization
        )
        self.optimize_button.grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)

        # --- Results Section ---
        results_frame = ttk.LabelFrame(self.content_frame, text="Optimization Results", padding="10")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        self.results_text = tk.Text(results_frame, height=10, width=70, relief=tk.FLAT, bg=self.style.lookup('Content.TFrame', 'background'), wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        self.results_text['yscrollcommand'] = results_scrollbar.set

    def _create_status_bar(self) -> None:
        """Create the status bar at the bottom."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def _schedule_initial_updates(self) -> None:
        """Schedule the initial loading of data after the UI is ready."""
        self.root.after(100, self.update_system_info)
        self.root.after(150, self.update_disk_usage)
        self.root.after(200, self.update_startup_list)

    # --- System Metrics Update ---

    def _schedule_metrics_update(self) -> None:
        """Schedules the next system metrics update."""
        # Check if root window still exists before scheduling next update
        try:
            if self.root.winfo_exists():
                self._update_system_metrics()
                self.root.after(self.METRICS_UPDATE_INTERVAL, self._schedule_metrics_update)
        except tk.TclError:
            logger.info("Metrics update loop stopped: Root window closed.")

    def _update_system_metrics(self) -> None:
        """Fetches system metrics using the worker."""
        def on_metrics_complete(result: Optional[Dict[str, float]], error: Optional[str] = None) -> None:
            if error:
                logger.error(f"Failed to get system metrics: {error}")
                # Optionally update labels to show error state
                # self.cpu_label.configure(text="CPU: Error")
                # self.memory_label.configure(text="Memory: Error")
            elif result:
                try:
                    # Check if root window still exists before updating labels
                    if self.root.winfo_exists():
                        cpu = result.get('cpu_percent', -1.0)
                        mem = result.get('memory_percent', -1.0)
                        self.cpu_label.configure(text=f"CPU: {cpu:.1f}%" if cpu >= 0 else "CPU: N/A")
                        self.memory_label.configure(text=f"Memory: {mem:.1f}%" if mem >= 0 else "Memory: N/A")
                except tk.TclError:
                    pass # Window closed, ignore update
                except Exception as e:
                    logger.error(f"Error updating metrics labels: {e}")
            else:
                 logger.warning("Received no data or error from get_system_metrics.")

        # Assuming core has a method like get_system_metrics that returns {'cpu_percent': x, 'memory_percent': y}
        if hasattr(self.core, 'get_system_metrics'):
             self.worker.add_task(self.core.get_system_metrics, on_metrics_complete)
        else:
             logger.warning("SentinelCore does not have 'get_system_metrics' method. Metrics update skipped.")
             # Update labels to indicate missing data if desired
             self.cpu_label.configure(text="CPU: N/A")
             self.memory_label.configure(text="Memory: N/A")


    # --- Data Update Methods ---

    def update_system_info(self) -> None:
        """Update system information display using the worker."""
        self.status_var.set("Fetching system info...")
        logger.debug("Requesting system info update.")
        def on_complete(result: Optional[Dict[str, Any]], error: Optional[str] = None) -> None:
            try:
                if not self.root.winfo_exists(): return # Check if window closed
                self.info_text.configure(state=tk.NORMAL) # Enable writing
                self.info_text.delete(1.0, tk.END)
                if error:
                    self.info_text.insert(tk.END, f"Error fetching system info: {error}")
                    logger.error(f"Error fetching system info: {error}")
                elif result:
                    for key, value in result.items():
                        self.info_text.insert(tk.END, f"{key.replace('_', ' ').title()}: {value}\n")
                    logger.debug("System info updated.")
                else:
                    self.info_text.insert(tk.END, "No system information available.")
                    logger.warning("Received no data or error from get_system_info.")
                self.info_text.configure(state=tk.DISABLED) # Make read-only
                self.status_var.set("Ready")
            except tk.TclError:
                 logger.warning("System info update aborted: Window closed.")
            except Exception as e:
                 logger.exception(f"Error updating system info text widget: {e}")
                 self.status_var.set("Error updating UI")

        self.worker.add_task(self.core.get_system_info, on_complete)

    def update_disk_usage(self) -> None:
        """Update disk usage information display using the worker."""
        self.status_var.set("Fetching disk usage...")
        logger.debug("Requesting disk usage update.")
        def on_complete(result: Optional[Dict[str, Any]], error: Optional[str] = None) -> None:
            try:
                if not self.root.winfo_exists(): return # Check if window closed
                self.disk_text.configure(state=tk.NORMAL)
                self.disk_text.delete(1.0, tk.END)
                if error:
                    self.disk_text.insert(tk.END, f"Error fetching disk usage: {error}")
                    logger.error(f"Error fetching disk usage: {error}")
                elif result and 'data' in result:
                    if not result['data']:
                         self.disk_text.insert(tk.END, "No disk partitions found or accessible.")
                    else:
                        for device, info in result['data'].items():
                            try:
                                total_gb = info['total'] / (1024**3)
                                # used_gb = info['used'] / (1024**3) # Not used in current format
                                free_gb = info['free'] / (1024**3)
                                percent = info.get('percent', 'N/A') # Handle missing percent key
                                self.disk_text.insert(tk.END,
                                    f"{device}: {free_gb:.1f} GB free of {total_gb:.1f} GB ({percent}% used)\n")
                            except (KeyError, TypeError, ZeroDivisionError) as e:
                                logger.warning(f"Could not parse disk info for {device}: {e} - Data: {info}")
                                self.disk_text.insert(tk.END, f"{device}: Error parsing data\n")
                    logger.debug("Disk usage updated.")
                else:
                    self.disk_text.insert(tk.END, "No disk usage information available.")
                    logger.warning("Received no data or error from get_disk_usage.")
                self.disk_text.configure(state=tk.DISABLED)
                self.status_var.set("Ready")
            except tk.TclError:
                 logger.warning("Disk usage update aborted: Window closed.")
            except Exception as e:
                 logger.exception(f"Error updating disk usage text widget: {e}")
                 self.status_var.set("Error updating UI")

        # Assuming core.get_disk_usage returns {'data': {'C:': {...}, ...}} or {'error': '...'}
        self.worker.add_task(self.core.get_disk_usage, on_complete)

    def update_startup_list(self) -> None:
        """Update the startup programs list using the worker."""
        self.status_var.set("Fetching startup programs...")
        logger.debug("Requesting startup list update.")
        def on_complete(result: Optional[List[Dict[str, Any]]], error: Optional[str] = None) -> None:
            try:
                if not self.root.winfo_exists(): return # Check if window closed
                # Clear existing items
                for item in self.startup_list.get_children():
                    self.startup_list.delete(item)

                if error:
                    logger.error(f"Failed to get startup programs: {error}")
                    # Optionally display error in the list or a message box
                    messagebox.showerror("Startup Programs Error", f"Could not load startup programs:\n{error}")
                elif result:
                    if not result:
                        # Insert a placeholder if the list is empty
                         self.startup_list.insert("", tk.END, values=("(No startup programs found)", "", ""))
                    else:
                        for item in result:
                            # Ensure keys exist, provide defaults if not
                            name = item.get('name', 'Unknown Program')
                            path = item.get('path', 'N/A')
                            status = item.get('status', 'Unknown')
                            self.startup_list.insert("", tk.END, values=(name, path, status))
                    logger.debug(f"Startup list updated with {len(result or [])} items.")
                else:
                     logger.warning("Received no data or error from get_startup_programs.")
                     self.startup_list.insert("", tk.END, values=("(Could not load data)", "", ""))

                self.status_var.set("Ready")
            except tk.TclError:
                 logger.warning("Startup list update aborted: Window closed.")
            except Exception as e:
                 logger.exception(f"Error updating startup list treeview: {e}")
                 self.status_var.set("Error updating UI")

        # Assuming core has get_startup_programs returning List[Dict[str, Any]]
        # where each dict has 'name', 'path', 'status' keys
        if hasattr(self.core, 'get_startup_programs'):
            self.worker.add_task(self.core.get_startup_programs, on_complete)
        else:
            logger.error("SentinelCore does not have 'get_startup_programs' method.")
            messagebox.showerror("Error", "Core function to get startup programs is missing.")
            self.status_var.set("Error: Core function missing")


    # --- Actions ---

    def manage_startup(self, action: str) -> None:
        """Manage startup programs (enable/disable) using the worker.

        Args:
            action: Either 'enable' or 'disable'.
        """
        selection = self.startup_list.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a program from the list first.")
            return

        item_id = selection[0]
        item_values = self.startup_list.item(item_id)['values']

        if not item_values or len(item_values) < 1:
             messagebox.showerror("Error", "Invalid item selected.")
             return

        program_name = item_values[0] # Assuming name is the first column
        # program_path = item_values[1] # Path might also be needed by core function

        # Optional: Add confirmation dialog
        if not messagebox.askyesno("Confirm Action", f"Are you sure you want to {action} '{program_name}'?"):
            return

        self.status_var.set(f"{action.capitalize()}ing '{program_name}'...")
        logger.info(f"Requesting to {action} startup program: {program_name}")

        def on_complete(result: Optional[Dict[str, bool]], error: Optional[str] = None) -> None:
            try:
                if not self.root.winfo_exists(): return # Check if window closed
                if error:
                    messagebox.showerror("Error", f"Failed to {action} '{program_name}':\n{error}")
                    logger.error(f"Failed to {action} '{program_name}': {error}")
                elif result and result.get('success'):
                    messagebox.showinfo("Success", f"'{program_name}' {action}d successfully.")
                    logger.info(f"Successfully {action}d startup program: {program_name}")
                    # Refresh the list to show the updated status
                    self.update_startup_list()
                else:
                    # Handle cases where core returns success=False or unexpected result
                    err_msg = result.get('message', 'Unknown reason') if isinstance(result, dict) else 'Unknown reason'
                    messagebox.showerror("Failed", f"Could not {action} '{program_name}':\n{err_msg}")
                    logger.error(f"Core reported failure to {action} '{program_name}': {err_msg}")

                self.status_var.set("Ready")
            except tk.TclError:
                 logger.warning(f"Startup management ({action}) update aborted: Window closed.")
            except Exception as e:
                 logger.exception(f"Error processing startup management result: {e}")
                 self.status_var.set("Error updating UI")


        # Assuming core.manage_startup_program takes action and program identifier (e.g., name or path)
        # And returns {'success': True/False, 'message': 'Optional details'}
        if hasattr(self.core, 'manage_startup_program'):
             # Pass necessary identifiers, e.g., name and maybe path if needed for uniqueness
             self.worker.add_task(
                 lambda: self.core.manage_startup_program(action=action, program_name=program_name), # Adjust args as needed by core
                 on_complete
             )
        else:
             logger.error("SentinelCore does not have 'manage_startup_program' method.")
             messagebox.showerror("Error", "Core function to manage startup programs is missing.")
             self.status_var.set("Error: Core function missing")


    def run_optimization(self) -> None:
        """Run system optimization with selected profile using the worker."""
        selected_profile = self.profile_var.get()
        logger.info(f"Starting optimization with profile: {selected_profile}")
        self.status_var.set(f"Optimizing ({selected_profile})...")
        self.optimize_button.state(['disabled'])
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Starting optimization using '{selected_profile}' profile...\n\n")
        self.results_text.configure(state=tk.DISABLED)


        def on_optimization_complete(results: Optional[Dict[str, Any]], error: Optional[str] = None) -> None:
            try:
                if not self.root.winfo_exists(): return # Check if window closed
                self.results_text.configure(state=tk.NORMAL) # Enable writing
                if error:
                    messagebox.showerror("Optimization Error", f"Failed to optimize system:\n{error}")
                    self.results_text.insert(tk.END, f"\n--- Optimization Failed ---\nError: {error}")
                    logger.error(f"Optimization failed: {error}")
                elif results:
                    self.display_optimization_results(results)
                    logger.info(f"Optimization completed. Success: {results.get('success')}")
                    if results.get('success'):
                         messagebox.showinfo("Optimization Complete", "System optimization finished successfully.")
                    else:
                         messagebox.showwarning("Optimization Issues", f"Optimization finished, but reported issues:\n{results.get('error', 'Unknown issue')}")

                else:
                     messagebox.showerror("Optimization Error", "Optimization process did not return any results.")
                     self.results_text.insert(tk.END, "\n--- Optimization Failed ---\nError: No results returned.")
                     logger.error("Optimization failed: No results returned from core.")

                self.results_text.configure(state=tk.DISABLED) # Make read-only again
                self.status_var.set("Ready")
                self.optimize_button.state(['!disabled']) # Re-enable button
            except tk.TclError:
                 logger.warning("Optimization result display aborted: Window closed.")
            except Exception as e:
                 logger.exception(f"Error displaying optimization results: {e}")
                 self.status_var.set("Error updating UI")
                 self.optimize_button.state(['!disabled']) # Ensure button is re-enabled on error


        self.worker.add_task(
            lambda: self.core.optimize_system(selected_profile),
            on_optimization_complete
        )

    def display_optimization_results(self, results: Dict[str, Any]) -> None:
        """Formats and displays optimization results in the text widget.

        Args:
            results: Dictionary containing optimization results from the core.
        """
        # Assumes results_text is already in NORMAL state
        if not results:
            self.results_text.insert(tk.END, "Received empty results.\n")
            return

        if not results.get("success", False):
            self.results_text.insert(tk.END, f"\n--- Optimization Reported Failure ---\n")
            self.results_text.insert(tk.END, f"Error: {results.get('error', 'No specific error message provided.')}\n")
            return # Stop displaying further details if overall success is false

        self.results_text.insert(tk.END, "\n--- Optimization Summary ---\n")

        # Display Initial State (Optional - can be verbose)
        if "initial_state" in results and isinstance(results["initial_state"], dict):
            self.results_text.insert(tk.END, "\nInitial State:\n")
            if not results["initial_state"]:
                 self.results_text.insert(tk.END, "  (No initial state data provided)\n")
            else:
                for key, value in results["initial_state"].items():
                    self.results_text.insert(tk.END, f"  {key.replace('_', ' ').title()}: {value}\n")

        # Display Optimizations Performed
        if "optimizations" in results and isinstance(results["optimizations"], list):
            self.results_text.insert(tk.END, "\nOptimizations Performed:\n")
            if not results["optimizations"]:
                 self.results_text.insert(tk.END", "  (No specific optimizations listed)\n")
            else:
                for opt in results["optimizations"]:
                     # Check if opt is a dict with details or just a string
                     if isinstance(opt, dict):
                         name = opt.get('name', 'Unnamed Task')
                         status = opt.get('status', 'Unknown')
                         details = opt.get('details', '')
                         self.results_text.insert(tk.END, f"  - {name}: {status}")
                         if details:
                              self.results_text.insert(tk.END, f" ({details})\n")
                         else:
                              self.results_text.insert(tk.END, "\n")
                     else:
                          self.results_text.insert(tk.END, f"  - {opt}\n") # Assume it's just a string name

        # Display Final State (Optional)
        if "final_state" in results and isinstance(results["final_state"], dict):
            self.results_text.insert(tk.END, "\nFinal State:\n")
            if not results["final_state"]:
                 self.results_text.insert(tk.END", "  (No final state data provided)\n")
            else:
                for key, value in results["final_state"].items():
                    self.results_text.insert(tk.END, f"  {key.replace('_', ' ').title()}: {value}\n")

        self.results_text.insert(tk.END, "\n--- Optimization Complete ---\n")
        self.results_text.see(tk.END) # Scroll to the end


    def _focus_optimization_section(self) -> None:
        """Scrolls the view to make the optimization section visible."""
        # This is a basic implementation. More complex UIs might switch frames.
        try:
            # Ensure layout is updated before calculating position
            self.content_frame.update_idletasks()
            # Focus the control frame itself or the optimize button
            self.optimize_button.focus_set()
            # Scroll the parent ScrollableFrame's canvas to show the control frame
            # Note: This might require access to the canvas in ScrollableFrame or a dedicated method there.
            # For simplicity, we'll just focus the button for now.
            logger.debug("Focus set to optimization section.")
        except tk.TclError:
             logger.warning("Could not focus optimization section: Window closed?")
        except Exception as e:
             logger.error(f"Error focusing optimization section: {e}")


    # --- Application Lifecycle ---

    def run(self) -> None:
        """Start the GUI application main loop."""
        logger.info("Starting SentinelGUI main loop...")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("GUI main loop interrupted by user (KeyboardInterrupt).")
        finally:
            logger.info("GUI main loop finished. Stopping worker thread...")
            self.worker.stop() # Ensure worker is stopped cleanly
            logger.info("Worker thread stopped.")

# Example usage (if running this file directly for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # Create a mock SentinelCore for testing
    class MockSentinelCore:
        version = "0.1-mock"
        def get_system_info(self):
            import time, platform
            time.sleep(0.5) # Simulate delay
            return {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        def get_disk_usage(self):
            import time, psutil, shutil
            time.sleep(0.8) # Simulate delay
            data = {}
            try:
                for part in psutil.disk_partitions(all=False):
                     if os.path.exists(part.mountpoint):
                        usage = shutil.disk_usage(part.mountpoint)
                        data[part.device] = {
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'percent': (usage.used / usage.total * 100) if usage.total > 0 else 0
                        }
            except Exception as e:
                 return {'error': str(e)}
            return {'data': data}

        def get_startup_programs(self):
            import time
            time.sleep(1.0) # Simulate delay
            # Mock data - replace with actual logic if possible
            return [
                {'name': 'Mock Program A', 'path': 'C:\\Path\\To\\A.exe', 'status': 'Enabled'},
                {'name': 'Mock Service B', 'path': 'C:\\Windows\\System32\\b.dll', 'status': 'Disabled'},
                {'name': 'Another Tool', 'path': '/usr/bin/tool', 'status': 'Enabled'},
            ]

        def manage_startup_program(self, action, program_name):
            import time
            time.sleep(0.5)
            logger.info(f"Mock: Received request to {action} {program_name}")
            # Simulate success/failure
            if "fail" in program_name.lower():
                 return {'success': False, 'message': 'Simulated failure for this program.'}
            return {'success': True}

        def optimize_system(self, profile):
            import time
            time.sleep(2.5) # Simulate delay
            logger.info(f"Mock: Optimizing with profile {profile}")
            return {
                'success': True,
                'profile': profile,
                'initial_state': {'cpu_governor': 'performance', 'swap_usage_percent': 15.2},
                'optimizations': [
                    {'name': 'Clean Temp Files', 'status': 'Success', 'details': 'Removed 150 MB'},
                    {'name': 'Defragment Drive C:', 'status': 'Skipped', 'details': 'SSD Drive'},
                    f'Set Power Profile to {profile}',
                    {'name': 'Disable Unused Service X', 'status': 'Success'}
                ],
                'final_state': {'cpu_governor': profile, 'swap_usage_percent': 10.1},
                'error': None
            }
        def get_system_metrics(self):
             import psutil, time
             # time.sleep(0.1) # Keep this fast
             return {
                  'cpu_percent': psutil.cpu_percent(),
                  'memory_percent': psutil.virtual_memory().percent
             }


    mock_core = MockSentinelCore()
    app = SentinelGUI(mock_core)
    app.run()
