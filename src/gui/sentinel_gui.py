# c:\Users\johnw\OneDrive\Desktop\SentinelPC\src\gui\sentinel_gui.py
"""SentinelPC GUI Interface

This module provides the graphical user interface for SentinelPC.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from typing import Dict, Any, Optional
import time  # Added for time.sleep in mock class

# Attempt to import PIL for image handling, provide fallback/warning if missing
try:
    from PIL import Image, ImageTk

    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False
    Image = None
    ImageTk = None

# Attempt to import core components, handle potential ImportError if structure differs
try:
    from ..core.sentinel_core import SentinelCore
    from .gui_worker import GUIWorker
    from .scrollable_frame import ScrollableFrame
    from . import theme
except ImportError as e:
    # Fallback for running standalone or if structure differs
    print(f"Warning: Could not import project modules. Using mock objects. Error: {e}")
    # Define mock classes or import alternatives if necessary for standalone testing
    SentinelCore = object # Placeholder
    GUIWorker = object # Placeholder
    ScrollableFrame = object # Placeholder
    theme = object # Placeholder
    class MockTheme:
        def apply_modern_theme(self, root):
            print("Mock theme applied")
            return ttk.Style()
    theme = MockTheme()


logger = logging.getLogger(__name__)


class SentinelGUI:
    """Graphical user interface for SentinelPC."""

    # Interval for updating system metrics (in milliseconds)
    METRICS_UPDATE_INTERVAL = 2000  # Update every 2 seconds

    def __init__(self, core: SentinelCore):
        """Initialize GUI interface.

        Args:
            core: Initialized SentinelCore instance
        """
        logger.info("Initializing SentinelGUI...")
        self.core = core
        self.root = tk.Tk()
        # Use core version if available, otherwise default
        core_version = getattr(core, 'version', 'N/A')
        self.root.title(f"SentinelPC v{core_version}")
        self.root.geometry("850x650")  # Slightly larger default size

        # Initialize worker thread
        self.worker = GUIWorker()
        self.worker.start()

        self._setup_styles_and_grid()
        self._create_widgets()

        # Start processing results from the worker queue
        self.worker.process_results(self.root)

        # Schedule initial data loading and periodic updates
        self._schedule_initial_updates()
        self._schedule_metrics_update()  # Start periodic metric updates

        logger.info("SentinelGUI initialized successfully.")

    def _setup_styles_and_grid(self) -> None:
        """Apply theme and configure root window grid."""
        self.style = theme.apply_modern_theme(self.root)

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)  # Main content area row
        self.root.grid_columnconfigure(1, weight=1)  # Main content area column

    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        self._create_header()
        self._create_sidebar()
        self._create_content_area()
        self._create_status_bar()  # Moved status bar creation here

    def _create_header(self) -> None:
        """Create the header section with title and metrics."""
        header_frame = ttk.Frame(self.root, style="Header.TFrame")
        header_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        header_frame.grid_columnconfigure(1, weight=1)  # Allow content to expand

        # --- Icon ---
        icon_label = ttk.Label(header_frame, style="Header.TLabel")
        icon_label.grid(
            row=0, column=0, rowspan=2, padx=10, pady=5, sticky=tk.W
        )
        if _PIL_AVAILABLE:
            try:
                # Construct path relative to this file
                base_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(
                    base_dir, "assets", "shield_icon_small.png"
                )  # Example: using a PNG
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    # Resize if needed, e.g.,
                    # img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    self.shield_icon = ImageTk.PhotoImage(img)
                    icon_label.configure(image=self.shield_icon)
                else:
                    logger.warning(f"Icon file not found: {icon_path}")
                    icon_label.configure(text="🛡️")  # Fallback text/emoji
            except Exception as e:
                logger.error(f"Failed to load icon: {e}")
                icon_label.configure(text="🛡️")  # Fallback text/emoji
        else:
            logger.warning("Pillow (PIL) library not found. Icon display disabled.")
            icon_label.configure(text="🛡️")  # Fallback text/emoji

        # --- Title ---
        title_label = ttk.Label(
            header_frame,
            text="SENTINEL PC Optimizer",
            style="Header.TLabel",
            font=("Segoe UI", 14, "bold"),
        )
        title_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky=tk.W)

        # --- Metrics Display ---
        metrics_frame = ttk.Frame(header_frame, style="Header.TFrame")
        metrics_frame.grid(row=1, column=1, padx=5, pady=(0, 5), sticky=tk.W)

        self.cpu_label = ttk.Label(
            metrics_frame, text="CPU: --.-%", style="Header.TLabel", width=12
        )
        self.cpu_label.pack(side=tk.LEFT, padx=(0, 15))

        self.memory_label = ttk.Label(
            metrics_frame, text="Memory: --.-%", style="Header.TLabel", width=15
        )
        self.memory_label.pack(side=tk.LEFT)

        try:
            # Get metrics in worker thread to avoid UI freezes
            def update_metrics():
                try:
                    # Check if core has the method before calling
                    if hasattr(self.core, "get_system_metrics"):
                        metrics = self.core.get_system_metrics()
                        if metrics and metrics.get("success"):
                            return metrics.get("current_metrics")
                    else:
                        logger.warning("Core object missing 'get_system_metrics'")
                    return None
                except Exception as e:
                    logger.error(f"Error fetching metrics: {e}")
                    return None

            def handle_metrics_update(result, error):
                if error:
                    logger.error(f"Metrics update failed: {error}")
                    return
                if result:
                    self.handle_metrics_update(result)

            # Schedule the next update
            self.worker.add_task(update_metrics, handle_metrics_update)
            self.root.after(
                self.METRICS_UPDATE_INTERVAL, self._schedule_metrics_update
            )
        except Exception as e:
            logger.error(f"Failed to schedule metrics update: {e}")
            # Retry scheduling after a delay
            self.root.after(5000, self._schedule_metrics_update)

    def handle_metrics_update(self, metrics: Dict[str, Any]) -> None:
        """Handle updated system metrics data.

        Args:
            metrics: Dictionary containing updated system metrics
                    including CPU usage, memory usage, etc.
        """
        try:
            if self.root.winfo_exists() and metrics:
                cpu = metrics.get("cpu_percent", -1.0)
                mem = metrics.get("memory_percent", -1.0)
                self.cpu_label.configure(
                    text=f"CPU: {cpu:.1f}%" if cpu >= 0 else "CPU: N/A"
                )
                self.memory_label.configure(
                    text=f"Memory: {mem:.1f}%" if mem >= 0 else "Memory: N/A"
                )
        except tk.TclError:
             pass # Window closed
        except Exception as e:
            logger.error(f"Error updating metrics labels: {e}")


    def show_about(self) -> None:
        """Display the about dialog with application information."""
        version = getattr(self.core, 'version', 'N/A')
        messagebox.showinfo(
            "About SentinelPC",
            f"SentinelPC Optimizer\nVersion: {version}\n\n"
            "Developed by WESCORE AI.\n"
            "System optimization and monitoring tool."
        )


    def toggle_theme(self) -> None:
        """Toggle between light and dark application themes."""
        # This requires more complex theme management in theme.py
        # For now, just log the action
        logger.info("Theme toggle requested (not fully implemented).")
        messagebox.showinfo("Theme", "Theme toggling is not yet implemented.")


    def _create_sidebar(self) -> None:
        """Create the sidebar navigation."""
        sidebar_frame = ttk.Frame(self.root, style="Sidebar.TFrame", width=180)
        sidebar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        sidebar_frame.grid_propagate(
            False
        )  # Prevent resizing based on content
        sidebar_frame.grid_rowconfigure(4, weight=1)  # Push exit button down

        # Add navigation buttons with commands
        ttk.Button(
            sidebar_frame,
            text="System Info",
            style="Sidebar.TButton",
            command=self.update_system_info,
        ).grid(row=0, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(
            sidebar_frame,
            text="Disk Usage",
            style="Sidebar.TButton",
            command=self.update_disk_usage,
        ).grid(row=1, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(
            sidebar_frame,
            text="Startup Programs",
            style="Sidebar.TButton",
            command=self.update_startup_list,
        ).grid(row=2, column=0, padx=10, pady=5, sticky=tk.EW)
        ttk.Button(
            sidebar_frame,
            text="Optimization",
            style="Sidebar.TButton",
            command=self._focus_optimization_section,
        ).grid(row=3, column=0, padx=10, pady=5, sticky=tk.EW)

        # Exit Button
        ttk.Button(
            sidebar_frame, text="Exit", style="Sidebar.TButton", command=self.root.quit
        ).grid(
            row=5, column=0, padx=10, pady=10, sticky=(tk.EW, tk.S)
        )

    def _create_content_area(self) -> None:
        """Create the main scrollable content area and its sections."""
        main_scroll_frame = ScrollableFrame(self.root)
        main_scroll_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame = main_scroll_frame.frame  # Get the inner frame
        self.content_frame.configure(style="Content.TFrame", padding="15")
        self.content_frame.grid_columnconfigure(
            0, weight=1
        )  # Allow content to expand horizontally

        # Create log text widget
        from tkinter import scrolledtext

        self.log_text = scrolledtext.ScrolledText(
            self.content_frame, height=10, wrap=tk.WORD
        )
        self.log_text.grid(
            row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5
        )
        self.log_text.configure(state="disabled")  # Make read-only

        # --- System Info Section ---
        info_frame = ttk.LabelFrame(
            self.content_frame, text="System Information", padding="10"
        )
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)
        self.info_text = tk.Text(
            info_frame,
            height=8,
            width=70,
            relief=tk.FLAT,
            # Use style lookup for background color
            bg=self.style.lookup("TFrame", "background"),
        )
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        # Add scrollbar if needed, though ScrollableFrame handles the main scroll
        info_scrollbar = ttk.Scrollbar(
            info_frame, orient=tk.VERTICAL, command=self.info_text.yview
        )
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text["yscrollcommand"] = info_scrollbar.set

        # --- Disk Usage Section ---
        disk_frame = ttk.LabelFrame(
            self.content_frame, text="Disk Usage", padding="10"
        )
        disk_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        disk_frame.grid_columnconfigure(0, weight=1)
        self.disk_text = tk.Text(
            disk_frame,
            height=5,
            width=70,
            relief=tk.FLAT,
            bg=self.style.lookup("TFrame", "background"),
        )
        self.disk_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        disk_scrollbar = ttk.Scrollbar(
            disk_frame, orient=tk.VERTICAL, command=self.disk_text.yview
        )
        disk_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        self.disk_text["yscrollcommand"] = disk_scrollbar.set
        ttk.Button(
            disk_frame, text="Refresh", command=self.update_disk_usage
        ).grid(
            row=1, column=0, columnspan=2, pady=(0, 5)
        )

        # --- Startup Programs Section ---
        startup_frame = ttk.LabelFrame(
            self.content_frame, text="Startup Programs", padding="10"
        )
        startup_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        startup_frame.grid_columnconfigure(0, weight=1)
        self.startup_list = ttk.Treeview(
            startup_frame,
            columns=("Program", "Path", "Status"),
            show="headings",
            height=6,
        )
        self.startup_list.heading("Program", text="Program")
        self.startup_list.heading("Path", text="Path/Command")
        self.startup_list.heading("Status", text="Status")
        self.startup_list.column("Program", width=200, anchor=tk.W)
        self.startup_list.column("Path", width=350, anchor=tk.W)
        self.startup_list.column("Status", width=100, anchor=tk.CENTER)
        self.startup_list.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        startup_scrollbar = ttk.Scrollbar(
            startup_frame, orient=tk.VERTICAL, command=self.startup_list.yview
        )
        startup_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        self.startup_list["yscrollcommand"] = startup_scrollbar.set

        startup_btn_frame = ttk.Frame(startup_frame, style="Content.TFrame")
        startup_btn_frame.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        ttk.Button(
            startup_btn_frame,
            text="Enable",
            command=lambda: self.manage_startup("enable"),
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            startup_btn_frame,
            text="Disable",
            command=lambda: self.manage_startup("disable"),
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            startup_btn_frame, text="Refresh List", command=self.update_startup_list
        ).pack(side=tk.LEFT, padx=5)

        # --- Optimization Controls Section ---
        self.control_frame = ttk.LabelFrame(
            self.content_frame, text="Optimization Controls", padding="10"
        )  # Store reference
        self.control_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(self.control_frame, text="Profile:").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W
        )
        self.profile_var = tk.StringVar(value="default")
        # TODO: Consider fetching profiles dynamically from core if they change
        profile_combo = ttk.Combobox(
            self.control_frame, textvariable=self.profile_var, state="readonly"
        )
        profile_combo["values"] = (
            "default",
            "performance",
            "balanced",
            "power-saver",
        )
        profile_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.optimize_button = ttk.Button(
            self.control_frame, text="Start Optimization", command=self.run_optimization
        )
        self.optimize_button.grid(
            row=0, column=2, padx=20, pady=5, sticky=tk.W
        )

        # --- Results Section ---
        results_frame = ttk.LabelFrame(
            self.content_frame, text="Optimization Results", padding="10"
        )
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        self.results_text = tk.Text(
            results_frame,
            height=10,
            width=70,
            relief=tk.FLAT,
            bg=self.style.lookup("TFrame", "background"),
            wrap=tk.WORD,
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        results_scrollbar = ttk.Scrollbar(
            results_frame, orient=tk.VERTICAL, command=self.results_text.yview
        )
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), pady=5)
        self.results_text["yscrollcommand"] = results_scrollbar.set

    def _create_status_bar(self) -> None:
        """Create the status bar at the bottom."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2),
        )
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
                self.root.after(
                    self.METRICS_UPDATE_INTERVAL,
                    self._schedule_metrics_update,
                )
        except tk.TclError:
            logger.info("Metrics update loop stopped: Root window closed.")

    def _update_system_metrics(self) -> None:
        """Fetches system metrics using the worker."""

        def on_metrics_complete(
            result: Optional[Dict[str, float]], error: Optional[str] = None
        ) -> None:
            if error:
                logger.error(f"Failed to get system metrics: {error}")
                # Optionally update labels to show error state
                # self.cpu_label.configure(text="CPU: Error")
                # self.memory_label.configure(text="Memory: Error")
            elif result:
                self.handle_metrics_update(result) # Call the handler method
            else:
                logger.warning("Received no data or error from get_system_metrics.")

        # Assuming core has a method like get_system_metrics
        if hasattr(self.core, "get_system_metrics"):
            self.worker.add_task(
                self.core.get_system_metrics, on_metrics_complete
            )
        else:
            logger.warning(
                "SentinelCore does not have 'get_system_metrics' method. "
                "Metrics update skipped."
            )
            # Update labels to indicate missing data if desired
            self.cpu_label.configure(text="CPU: N/A")
            self.memory_label.configure(text="Memory: N/A")

    # --- Data Update Methods ---

    def update_system_info(self) -> None:
        """Update system information display using the worker."""
        self.status_var.set("Fetching system info...")
        logger.debug("Requesting system info update.")

        def on_complete(
            result: Optional[Dict[str, Any]], error: Optional[str] = None
        ) -> None:
            try:
                if not self.root.winfo_exists():
                    return  # Check if window closed
                self.info_text.configure(state=tk.NORMAL)  # Enable writing
                self.info_text.delete(1.0, tk.END)
                if error:
                    self.info_text.insert(
                        tk.END, f"Error fetching system info: {error}"
                    )
                    logger.error(f"Error fetching system info: {error}")
                elif result:
                    for key, value in result.items():
                        self.info_text.insert(
                            tk.END,
                            f"{key.replace('_', ' ').title()}: {value}\n",
                        )
                    logger.debug("System info updated.")
                else:
                    self.info_text.insert(tk.END, "No system information available.")
                    logger.warning("Received no data or error from get_system_info.")
                self.info_text.configure(state=tk.DISABLED)  # Make read-only
                self.status_var.set("Ready")
            except tk.TclError:
                logger.warning("System info update aborted: Window closed.")
            except Exception as e:
                logger.exception(f"Error updating system info text widget: {e}")
                self.status_var.set("Error updating UI")

        if hasattr(self.core, "get_system_info"):
            self.worker.add_task(self.core.get_system_info, on_complete)
        else:
            logger.warning("Core object missing 'get_system_info'")
            self.status_var.set("Error: Core function missing")


    def update_disk_usage(self) -> None:
        """Update disk usage information display."""
        self.status_var.set("Fetching disk usage...")
        logger.debug("Requesting disk usage update.")

        def disk_usage_task():
            if hasattr(self.core, "get_disk_usage"):
                return self.core.get_disk_usage()
            else:
                logger.warning("Core object missing 'get_disk_usage'")
                return {"success": False, "error": "Core function missing"}


        def disk_usage_callback(result: Optional[Any], error: Optional[str]) -> None:
            try:
                if not self.root.winfo_exists(): return
                self.disk_text.configure(state=tk.NORMAL)
                self.disk_text.delete("1.0", tk.END)
                if error:
                    self.logger.error(f"Error updating disk usage: {error}")
                    self.disk_text.insert(tk.END, f"Error: {error}")
                    messagebox.showerror("Error", f"Failed to update disk usage: {error}")
                elif result and result.get("success"):
                    disk_info = result.get("data", {})
                    inaccessible = result.get("inaccessible", [])
                    if not disk_info and not inaccessible:
                         self.disk_text.insert(tk.END, "No disk partitions found or accessible.")
                    for disk, usage in disk_info.items():
                        used_percent = usage.get("percent", 0)
                        total = usage.get("total", 0)
                        free = usage.get("free", 0)
                        total_gb = total / (1024**3)
                        free_gb = free / (1024**3)
                        disk_line = f"Disk {disk} ({usage.get('mountpoint', '')}):\n"
                        disk_line += f"  Used: {used_percent:.1f}%\n"
                        disk_line += f"  Total: {total_gb:.1f} GB, Free: {free_gb:.1f} GB\n\n"
                        self.disk_text.insert(tk.END, disk_line)
                    if inaccessible:
                        self.disk_text.insert(tk.END, "\nInaccessible Partitions:\n")
                        for part in inaccessible:
                            self.disk_text.insert(tk.END, f"  - {part.get('device', 'N/A')}: {part.get('reason', 'Unknown')}\n")
                    logger.debug("Disk usage updated.")
                else:
                    err_msg = result.get("error", "Failed to get disk usage.") if result else "Failed to get disk usage."
                    self.disk_text.insert(tk.END, f"Error: {err_msg}")
                    logger.error(f"Failed to get disk usage: {err_msg}")

                self.disk_text.configure(state=tk.DISABLED)
                self.status_var.set("Ready")
            except tk.TclError:
                 logger.warning("Disk usage update aborted: Window closed.")
            except Exception as e:
                self.logger.error(f"Error displaying disk usage: {e}", exc_info=True)
                messagebox.showerror("Error", f"Failed to display disk usage: {str(e)}")
                self.status_var.set("Error updating UI")


        try:
            # Run disk usage check in worker thread
            self.worker.add_task(disk_usage_task, disk_usage_callback)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start disk usage check: {str(e)}")
            self.logger.error(f"Failed to start disk usage check: {e}", exc_info=True)
            self.status_var.set("Error starting task")

    def update_startup_list(self) -> None:
        """Update startup programs list."""
        self.status_var.set("Fetching startup programs...")
        logger.debug("Requesting startup list update.")

        def startup_list_task():
            if hasattr(self.core, "get_startup_programs"):
                return self.core.get_startup_programs()
            else:
                logger.warning("Core object missing 'get_startup_programs'")
                return {"success": False, "error": "Core function missing"}

        def startup_list_callback(
            result: Optional[Any], error: Optional[str]
        ) -> None:
            try:
                if not self.root.winfo_exists(): return
                # Clear existing items first
                for item in self.startup_list.get_children():
                    self.startup_list.delete(item)

                if error:
                    self.logger.error(f"Error updating startup list: {error}")
                    messagebox.showerror(
                        "Error", f"Failed to update startup programs: {error}"
                    )
                elif result and result.get("success"):
                    startup_items = result.get("programs", [])
                    if not startup_items:
                        # Insert a placeholder if the list is empty
                         self.startup_list.insert("", tk.END, values=("(No startup programs found)", "", ""))
                    else:
                        # Add items to treeview
                        for item in startup_items:
                            self.startup_list.insert(
                                "",
                                tk.END,
                                values=(
                                    item.get("name", "Unknown"),
                                    item.get("path", "Unknown"),
                                    item.get("status", "Unknown"),
                                ),
                            )
                    logger.debug("Startup list updated.")
                else:
                     err_msg = result.get("error", "Failed to get startup list.") if result else "Failed to get startup list."
                     messagebox.showerror("Error", f"Failed to get startup programs: {err_msg}")
                     logger.error(f"Failed to get startup programs: {err_msg}")
                     self.startup_list.insert("", tk.END, values=(f"(Error: {err_msg})", "", ""))


                self.status_var.set("Ready")
            except tk.TclError:
                 logger.warning("Startup list update aborted: Window closed.")
            except Exception as e:
                self.logger.error(f"Error displaying startup list: {e}", exc_info=True)
                messagebox.showerror(
                    "Error", f"Failed to display startup programs: {str(e)}"
                )
                self.status_var.set("Error updating UI")


        try:
            # Run startup list check in worker thread
            self.worker.add_task(startup_list_task, startup_list_callback)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to start startup list check: {str(e)}"
            )
            self.logger.error(f"Failed to start startup list check: {e}", exc_info=True)
            self.status_var.set("Error starting task")

    # --- Actions ---

    def manage_startup(self, action: str) -> None:
        """Enable or disable selected startup program with security validation."""
        # Validate action parameter
        if action not in ["enable", "disable"]:
            logger.error(f"Invalid startup management action: {action}")
            return

        selection = self.startup_list.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please select a startup program to manage."
            )
            return

        item_id = selection[0]
        item_values = self.startup_list.item(item_id)["values"]

        # Check for placeholder item
        if not item_values or len(item_values) < 3 or not item_values[0] or item_values[0].startswith("("):
            logger.warning("Invalid or placeholder startup item selected for management.")
            messagebox.showwarning("Invalid Selection", "Cannot manage this item.")
            return

        program_name = str(item_values[0]).strip()
        program_path = str(item_values[1]).strip() # Path is needed for enabling

        # Validate program name and path (path needed for enable)
        if not program_name or (action == "enable" and not program_path):
            logger.error(f"Empty program name or path for action '{action}'")
            messagebox.showerror("Error", "Invalid program details for this action.")
            return

        # Validate path security only if path is provided and action is enable
        if action == "enable" and not self._is_safe_path(program_path):
            logger.error(f"Unsafe program path detected for enabling: {program_path}")
            messagebox.showerror(
                "Security Error", "Invalid or unsafe program path detected for enabling."
            )
            return

        # Optional: Add confirmation dialog
        if not messagebox.askyesno(
            "Confirm Action", f"Are you sure you want to {action} '{program_name}'?"
        ):
            return

        self.status_var.set(f"{action.capitalize()}ing '{program_name}'...")
        logger.info(f"Requesting to {action} startup program: {program_name}")

        def on_complete(
            result: Optional[Dict[str, Any]], error: Optional[str] = None
        ) -> None:
            try:
                if not self.root.winfo_exists():
                    return  # Check if window closed
                if error:
                    messagebox.showerror(
                        "Error", f"Failed to {action} '{program_name}':\n{error}"
                    )
                    logger.error(f"Failed to {action} '{program_name}': {error}")
                elif result and result.get("success"):
                    messagebox.showinfo(
                        "Success", f"'{program_name}' {action}d successfully."
                    )
                    logger.info(
                        f"Successfully {action}d startup program: {program_name}"
                    )
                    # Refresh the list to show the updated status
                    self.update_startup_list()
                else:
                    # Handle cases where core returns success=False or unexpected result
                    err_msg = (
                        result.get("error", "Unknown reason") # Changed from 'message'
                        if isinstance(result, dict)
                        else "Unknown reason"
                    )
                    messagebox.showerror(
                        "Failed", f"Could not {action} '{program_name}':\n{err_msg}"
                    )
                    logger.error(
                        f"Core reported failure to {action} '{program_name}': {err_msg}"
                    )

                self.status_var.set("Ready")
            except tk.TclError:
                logger.warning(
                    f"Startup management ({action}) update aborted: Window closed."
                )
            except Exception as e:
                logger.exception(f"Error processing startup management result: {e}")
                self.status_var.set("Error updating UI")

        if hasattr(self.core, "manage_startup_program"):
            # Pass program_path only if enabling
            task_args = {"action": action, "program_name": program_name}
            if action == "enable":
                task_args["program_path"] = program_path

            self.worker.add_task(
                 lambda: self.core.manage_startup_program(**task_args),
                 on_complete,
            )
        else:
            logger.error("SentinelCore does not have 'manage_startup_program' method.")
            messagebox.showerror(
                "Error", "Core function to manage startup programs is missing."
            )
            self.status_var.set("Error: Core function missing")

    def _is_safe_path(self, path: str) -> bool:
        """Basic validation if a file path seems safe for startup management.

        Args:
            path: The file path to validate
        """
        if not path: return False # Empty path is not safe

        # Disallow relative paths for startup items for security
        if not os.path.isabs(path):
             logger.warning(f"Relative path detected in startup item: {path}")
             return False

        try:
            # Basic path security checks
            if len(path) > 1024:  # Generous path length limit
                logger.warning(f"Excessively long path detected: {path[:100]}...")
                return False

            # Check for suspicious patterns more carefully
            # Avoid patterns that allow command injection or directory traversal
            suspicious_patterns = ["..", "&&", "|", ";", ">", "<", "$(", "`", "\n", "\r"]
            # Check for unquoted spaces if the path isn't enclosed in quotes
            # This is complex, so we'll focus on the patterns above for now.
            # A more robust check might involve ensuring proper quoting if spaces exist.

            if any(pattern in path for pattern in suspicious_patterns):
                 logger.warning(f"Suspicious pattern detected in path: {path}")
                 return False

            # Optional: Check if the path points to an executable?
            # This might be too restrictive. For now, rely on pattern checks.
            # if not path.lower().endswith(('.exe', '.bat', '.cmd', '.com')):
            #     logger.warning(f"Path does not point to a common executable type: {path}")
            #     return False

            # Check if the file exists (basic sanity check)
            # Note: os.path.isfile might fail for some system paths even if valid
            # We rely more on pattern matching above.
            # return os.path.isfile(path)
            return True # Passed basic checks

        except Exception as e:
            logger.error(f"Path validation error for '{path}': {e}")
            return False

    def run_optimization(self) -> None:
        """Run system optimization with selected profile."""
        profile = self.profile_var.get()
        self.status_var.set(f"Starting optimization with profile: {profile}...")
        logger.info(f"Requesting optimization with profile: {profile}")

        def optimization_task():
             if hasattr(self.core, "optimize_system"):
                return self.core.optimize_system(profile)
             else:
                logger.warning("Core object missing 'optimize_system'")
                return {"success": False, "error": "Core function missing"}


        def optimization_callback(result: Optional[Any], error: Optional[str]) -> None:
            try:
                if not self.root.winfo_exists(): return
                self.results_text.configure(state=tk.NORMAL)
                self.results_text.delete("1.0", tk.END) # Clear previous results

                if error:
                    messagebox.showerror("Error", f"Optimization failed: {error}")
                    self.logger.error(f"Optimization error: {error}")
                    self.results_text.insert(tk.END, f"Error: {error}\n")
                elif result:
                    self.display_optimization_results(result) # Use helper to display
                    if result.get("success"):
                        messagebox.showinfo("Success", "Optimization completed successfully!")
                        self.update_system_info()  # Refresh system info after optimization
                    else:
                        failed_tasks = result.get("failed_tasks", [])
                        failed_msg = f"Optimization completed with failures: {', '.join(t['name'] for t in failed_tasks if isinstance(t, dict) and 'name' in t)}" if failed_tasks else "Optimization failed for unknown reasons."
                        messagebox.showerror("Error", failed_msg)
                        logger.error(failed_msg)

                else:
                     messagebox.showerror("Error", "Optimization returned no result.")
                     self.results_text.insert(tk.END, "Error: No result returned.\n")

                self.results_text.configure(state=tk.DISABLED)
                self.status_var.set("Ready")
            except tk.TclError:
                 logger.warning("Optimization callback aborted: Window closed.")
            except Exception as e:
                 logger.exception(f"Error processing optimization result: {e}")
                 messagebox.showerror("Error", "Failed to process optimization results.")
                 self.status_var.set("Error updating UI")


        try:
            # Run optimization in worker thread
            self.worker.add_task(optimization_task, optimization_callback)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start optimization: {str(e)}")
            self.logger.error(f"Failed to start optimization: {e}", exc_info=True)
            self.status_var.set("Error starting task")

    def display_optimization_results(self, results: Dict[str, Any]) -> None:
        """Formats and displays optimization results in the text widget.

        Args:
            results: Dictionary containing optimization results from the core.
        """
        # Assumes results_text is already in NORMAL state
        if not results:
            self.results_text.insert(tk.END, "Received empty results.\n")
            return

        if not results.get("success", False): # Check overall success flag
            self.results_text.insert(
                tk.END, f"\n--- Optimization Reported Failure ---\n"
            )
            error_msg = results.get('error', 'No specific error message provided.')
            failed_tasks_info = results.get('failed_tasks', [])
            if failed_tasks_info:
                 error_msg += "\nFailed Tasks:\n"
                 for task in failed_tasks_info:
                     task_name = task.get('name', 'Unknown Task')
                     task_error = task.get('error', 'Unknown Error')
                     error_msg += f"  - {task_name}: {task_error}\n"

            self.results_text.insert(tk.END, f"Error: {error_msg}\n")
            return  # Stop displaying further details if overall success is false

        self.results_text.insert(tk.END, "\n--- Optimization Summary ---\n")
        self.results_text.insert(tk.END, f"Profile Used: {results.get('profile', 'N/A')}\n")
        self.results_text.insert(tk.END, f"Tasks Completed: {results.get('tasks_completed', 'N/A')}\n")
        self.results_text.insert(tk.END, f"Tasks Failed: {results.get('tasks_failed', 'N/A')}\n")
        timestamp = results.get('timestamp', 'N/A')
        self.results_text.insert(tk.END, f"Timestamp: {timestamp}\n")


        # Display Initial State (Optional - can be verbose)
        if "initial_state" in results and isinstance(results["initial_state"], dict):
            self.results_text.insert(tk.END, "\nInitial State:\n")
            if not results["initial_state"]:
                self.results_text.insert(tk.END, "  (No initial state data provided)\n")
            else:
                for key, value in results["initial_state"].items():
                    self.results_text.insert(
                        tk.END, f"  {key.replace('_', ' ').title()}: {value}\n"
                    )

        # Display Optimizations Performed (using 'tasks' key if available)
        tasks_run = results.get('tasks', results.get('optimizations')) # Check both keys
        if isinstance(tasks_run, list):
            self.results_text.insert(tk.END, "\nOptimizations Performed:\n")
            if not tasks_run:
                self.results_text.insert(
                    tk.END, "  (No specific optimizations listed)\n"
                )
            else:
                for opt in tasks_run:
                    # Check if opt is a dict with details or just a string
                    if isinstance(opt, dict):
                        name = opt.get("name", "Unnamed Task")
                        status = "Success" if opt.get("success", False) else "Failed"
                        details = opt.get("details", opt.get("message", opt.get("error", ""))) # Get more info
                        self.results_text.insert(tk.END, f"  - {name}: {status}")
                        if details:
                            self.results_text.insert(tk.END, f" ({details})\n")
                        else:
                            self.results_text.insert(tk.END, "\n")
                    else:
                        self.results_text.insert(
                            tk.END, f"  - {opt}\n"
                        )  # Assume it's just a string name

        # Display Failed Tasks Separately if available
        failed_tasks_info = results.get('failed_tasks', [])
        if failed_tasks_info:
             self.results_text.insert(tk.END, "\nFailed Tasks Details:\n")
             for task in failed_tasks_info:
                 task_name = task.get('name', 'Unknown Task')
                 task_error = task.get('error', 'Unknown Error')
                 self.results_text.insert(tk.END, f"  - {task_name}: {task_error}\n")


        # Display Final State (Optional)
        if "final_state" in results and isinstance(results["final_state"], dict):
            self.results_text.insert(tk.END, "\nFinal State:\n")
            if not results["final_state"]:
                self.results_text.insert(tk.END, "  (No final state data provided)\n")
            else:
                for key, value in results["final_state"].items():
                    self.results_text.insert(
                        tk.END, f"  {key.replace('_', ' ').title()}: {value}\n"
                    )

        # Display Warnings
        warnings = results.get('warnings', [])
        if warnings:
            self.results_text.insert(tk.END, "\nWarnings:\n")
            for warning in warnings:
                 self.results_text.insert(tk.END, f"  - {warning}\n")


        self.results_text.insert(tk.END, "\n--- Optimization Complete ---\n")
        self.results_text.see(tk.END)  # Scroll to the end

    def _focus_optimization_section(self) -> None:
        """Scrolls the view to make the optimization section visible."""
        # This is a basic implementation. More complex UIs might switch frames.
        try:
            # Ensure layout is updated before calculating position
            self.content_frame.update_idletasks()
            # Focus the control frame itself or the optimize button
            self.optimize_button.focus_set()
            # Scroll the parent ScrollableFrame's canvas to show the control frame
            # Note: This might require access to the canvas in ScrollableFrame
            # or a dedicated method there.
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
            self.worker.stop()  # Ensure worker is stopped cleanly
            logger.info("Worker thread stopped.")


# Example usage (if running this file directly for testing)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Create a mock SentinelCore for testing
    class MockSentinelCore:
        version = "0.1-mock"

        def get_system_info(self):
            import platform
            import time
            time.sleep(0.5)  # Simulate delay
            return {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            }

        def get_disk_usage(self):
            import psutil
            import shutil
            import time
            time.sleep(0.8)  # Simulate delay
            data = {}
            try:
                for part in psutil.disk_partitions(all=False):
                    if os.path.exists(part.mountpoint):
                        try:
                            usage = shutil.disk_usage(part.mountpoint)
                            data[part.device] = {
                                "mountpoint": part.mountpoint, # Added mountpoint
                                "total": usage.total,
                                "used": usage.used,
                                "free": usage.free,
                                "percent": (
                                    (usage.used / usage.total * 100)
                                    if usage.total > 0
                                    else 0
                                ),
                            }
                        except OSError as e:
                             logger.warning(f"Could not get usage for {part.mountpoint}: {e}")
            except Exception as e:
                logger.exception("Error getting disk usage in mock")
                return {"success": False, "error": str(e)}
            return {"success": True, "data": data, "inaccessible": []} # Match expected structure

        def get_startup_programs(self):
            import time
            time.sleep(1.0)  # Simulate delay
            # Mock data - replace with actual logic if possible
            return { # Return dict matching expected structure
                "success": True,
                "programs": [
                    {
                        "name": "Mock Program A",
                        "path": "C:\\Path\\To\\A.exe",
                        "status": "Enabled",
                    },
                    {
                        "name": "Mock Service B",
                        "path": "C:\\Windows\\System32\\b.dll",
                        "status": "Disabled",
                    },
                    {"name": "Another Tool", "path": "/usr/bin/tool", "status": "Enabled"},
                    {"name": "Program To Fail", "path": "C:\\fail.exe", "status": "Enabled"},
                ]
            }

        def manage_startup_program(self, action, program_name, program_path=None): # Added path
            import time
            time.sleep(0.5)
            logger.info(f"Mock: Received request to {action} {program_name} (Path: {program_path})")
            # Simulate success/failure
            if "fail" in program_name.lower():
                return {
                    "success": False,
                    "error": "Simulated failure for this program.", # Use 'error' key
                }
            return {"success": True}

        def optimize_system(self, profile):
            import time
            time.sleep(2.5)  # Simulate delay
            logger.info(f"Mock: Optimizing with profile {profile}")
            # Simulate potential failure
            success = profile != "fail_profile"
            failed_tasks_list = []
            if not success:
                 failed_tasks_list = [{"name": "Simulated Task Fail", "error": "Profile caused failure"}]

            return { # Match expected structure from core optimizer
                "success": success,
                "profile": profile,
                "tasks_completed": 2 if success else 1,
                "tasks_failed": 0 if success else 1,
                "failed_tasks": failed_tasks_list,
                "warnings": ["Mock warning during optimization"] if success else [],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                # Optional detailed task results if needed by display logic
                "tasks": [
                     {"name": "Clean Temp Files", "success": True, "details": "Removed 150 MB"},
                     {"name": "Simulated Task Fail", "success": False, "error": "Profile caused failure"}
                ] if not success else [
                     {"name": "Clean Temp Files", "success": True, "details": "Removed 150 MB"},
                     {"name": "Set Power Profile", "success": True, "details": f"Set to {profile}"}
                ]
            }

        def get_system_metrics(self):
            import psutil
            # time.sleep(0.1) # Keep this fast
            try:
                return {
                    "success": True, # Add success flag
                    "current_metrics": {
                        "cpu_percent": psutil.cpu_percent(),
                        "memory_percent": psutil.virtual_memory().percent,
                    }
                }
            except Exception as e:
                 logger.exception("Error getting system metrics in mock")
                 return {"success": False, "error": str(e)}


    mock_core = MockSentinelCore()
    app = SentinelGUI(mock_core)
    app.run()
