# c:\Users\johnw\OneDrive\Desktop\SentinelPC\src\gui\SentinelPC_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import platform
import logging
import winreg

# Project imports

# Assuming these are in the expected locations relative to this file
# Adjust paths if necessary
try:
    from ..core.environment_manager import EnvironmentConfig
    from ..core.performance_optimizer import (
        PerformanceOptimizer,
    )  # Assuming this exists
    from .gui_worker import GUIWorker
    from .exceptions import GuiException  # Or other relevant exceptions
except ImportError as e:
    # Fallback for running standalone or if structure differs
    print(f"Warning: Could not import project modules. Using mock objects. Error: {e}")

    # Define mock classes if needed for standalone testing
    class MockEnvironmentConfig:
        theme = {"base": "#F0F0F0", "text": "#000000", "primary": "#007ACC"}

    class MockPerformanceOptimizer:
        def clean_temp_files(self):
            print("Mock: Cleaning temp files")
            # Simulate success/failure
            import random

            return random.choice([True, False])

    class MockGUIWorker:
        def __init__(self):
            print("Mock GUIWorker initialized")

        def start(self):
            print("Mock GUIWorker started")

        def stop(self):
            print("Mock GUIWorker stopped")

        def add_task(self, task, callback, *args, **kwargs):
            print(f"Mock GUIWorker: Adding task {task.__name__}")
            # Simulate running the task and calling back
            try:
                result = task(*args, **kwargs)
                print(
                    f"Mock GUIWorker: Task {task.__name__} finished, calling callback"
                )
                # Simulate calling back in main thread (not really async here)
                callback(result, None)
            except Exception as e:
                print(f"Mock GUIWorker: Task {task.__name__} failed: {e}")
                callback(None, str(e))

        def process_results(self, root):
            pass  # No-op for mock

    EnvironmentConfig = MockEnvironmentConfig
    PerformanceOptimizer = MockPerformanceOptimizer
    GUIWorker = MockGUIWorker
    GuiException = Exception


logger = logging.getLogger(__name__)
# Basic logging config if running standalone
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


class AdaptiveGUI:
    def __init__(self):
        logger.info("Initializing AdaptiveGUI...")
        try:
            self.config = EnvironmentConfig()
        except Exception as e:
            logger.error(f"Failed to load EnvironmentConfig: {e}. Using default theme.")

            # Provide a default theme if config fails
            class DefaultConfig:
                theme = {"base": "#F0F0F0", "text": "#000000", "primary": "#007ACC"}

            self.config = DefaultConfig()

        self.root = tk.Tk()
        self.root.title("PC Optimizer (Adaptive)")
        self.root.geometry("600x500")  # Adjusted size

        # --- Worker Setup ---
        self.worker = GUIWorker()
        self.worker.start()
        self.active_tasks = 0  # Counter for running tasks
        self.active_tasks_lock = threading.Lock()

        self._apply_theme()

        # Map display names to task functions and their callbacks
        self.optimization_tasks = {
            "Clean Temporary Files": (
                self._clean_temp_files_task,
                self._on_task_complete,
            ),
            "Check Disk Usage": (self._check_disk_usage_task, self._on_task_complete),
            "List Startup Programs": (
                self._get_startup_programs_task,
                self._on_task_complete,
            ),  # Renamed for clarity
            "Optimize Power Settings (Windows)": (
                self._optimize_power_settings_task,
                self._on_task_complete,
            ),
            "Run Disk Cleanup (Windows)": (
                self._run_disk_cleanup_task,
                self._on_task_complete,
            ),
        }
        self.create_widgets()

        # Start processing worker results
        self.worker.process_results(self.root)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        logger.info("AdaptiveGUI initialized.")

    def _apply_theme(self):
        logger.debug("Applying theme...")
        base_color = self.config.theme.get("base", "#F0F0F0")
        text_color = self.config.theme.get("text", "#000000")
        primary_color = self.config.theme.get("primary", "#007ACC")

        self.root.configure(bg=base_color)

        style = ttk.Style(self.root)

        # Basic color adjustment for hover (example)
        def adjust_color(hex_color, factor=0.8):
            if not hex_color.startswith("#") or len(hex_color) != 7:
                return hex_color  # Invalid format
            try:
                rgb = tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
                adjusted_rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
                return (
                    f"#{adjusted_rgb[0]:02x}{adjusted_rgb[1]:02x}{adjusted_rgb[2]:02x}"
                )
            except ValueError:
                return hex_color  # Fallback

        hover_color = adjust_color(primary_color)

        try:
            # Use 'clam' or 'alt' theme as a base for better customization possibilities
            style.theme_use("clam")
        except tk.TclError:
            logger.warning("Could not use 'clam' theme, using default.")
            # Fallback to default theme if 'clam' is not available

        style.configure(
            ".", background=base_color, foreground=text_color, font=("Segoe UI", 9)
        )
        style.configure("TLabel", background=base_color, foreground=text_color)
        style.configure("TFrame", background=base_color)
        style.configure(
            "TLabelframe",
            background=base_color,
            foreground=text_color,
            bordercolor=primary_color,
        )
        style.configure(
            "TLabelframe.Label", background=base_color, foreground=text_color
        )
        style.configure("TCheckbutton", background=base_color, foreground=text_color)
        style.map(
            "TCheckbutton",
            indicatorcolor=[("selected", primary_color), ("!selected", text_color)],
            background=[("active", adjust_color(base_color, 0.95))],
        )  # Subtle hover on checkbutton background

        style.configure(
            "TButton",
            background=primary_color,
            foreground="white",
            padding=(10, 5),
            borderwidth=0,
        )
        style.map(
            "TButton",
            background=[
                ("active", hover_color),
                ("disabled", adjust_color(primary_color, 1.2)),
            ],
        )

        style.configure(
            "Log.TText", background="white", foreground=text_color, font=("Consolas", 9)
        )  # Specific style for log

        logger.debug("Theme applied.")

    def create_widgets(self):
        logger.debug("Creating widgets...")
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # --- Options Frame ---
        options_frame = ttk.LabelFrame(
            main_frame, text="Optimization Options", padding="10"
        )
        options_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), pady=(0, 10))
        self.option_vars = {}
        row = 0
        for option_name in self.optimization_tasks.keys():
            self.option_vars[option_name] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                options_frame, text=option_name, variable=self.option_vars[option_name]
            )
            cb.grid(row=row, column=0, sticky=tk.W, pady=2)
            row += 1

        # --- Log Frame ---
        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding="10")
        log_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        # Use ScrolledText for built-in scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, height=15, width=70, relief=tk.FLAT
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.log_text.configure(
            font=("Consolas", 9), state=tk.DISABLED
        )  # Start disabled

        # Configure tags for log messages AFTER creating the widget
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure(
            "task_start", foreground="blue", font=("Consolas", 9, "bold")
        )

        # --- Button Frame ---
        button_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))  # Padding top only
        button_frame.grid(row=2, column=0, sticky=(tk.E, tk.W))

        self.run_button = ttk.Button(
            button_frame,
            text="Run Selected Optimizations",
            command=self.run_optimizations,
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))

        self.exit_button = ttk.Button(button_frame, text="Exit", command=self.on_close)
        self.exit_button.pack(side=tk.RIGHT)

        # --- Grid Resizing Configuration ---
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # Options frame doesn't expand much
        main_frame.rowconfigure(1, weight=1)  # Log frame takes most space
        main_frame.rowconfigure(2, weight=0)  # Button frame fixed size
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        logger.debug("Widgets created.")

    def _log(self, message: str, level: str = "info"):
        """Safely logs messages to the Text widget from the main thread."""
        try:
            if not self.root.winfo_exists():
                return
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n", level)
            self.log_text.configure(state=tk.DISABLED)
            self.log_text.see(tk.END)  # Scroll to the end
        except tk.TclError as e:
            logger.error(f"TclError while logging to GUI: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error logging to GUI: {e}")

    def run_optimizations(self):
        """Adds selected optimization tasks to the worker queue."""
        selected_options = [name for name, var in self.option_vars.items() if var.get()]

        if not selected_options:
            self._log("No optimization options selected.", "warning")
            return

        self._log("Starting selected optimizations...", "info")
        self.run_button.configure(state=tk.DISABLED)

        with self.active_tasks_lock:
            self.active_tasks = 0  # Reset counter

        for option_name in selected_options:
            if option_name in self.optimization_tasks:
                task_func, callback_func = self.optimization_tasks[option_name]
                self._log(f"Queueing task: {option_name}", "info")

                # Pass option_name to the callback using a lambda
                # This way the callback knows which task just finished
                task_callback = lambda result, error, name=option_name: callback_func(
                    name, result, error
                )

                # Add task to worker
                added = self.worker.add_task(task_func, task_callback)

                if added:
                    with self.active_tasks_lock:
                        self.active_tasks += 1
                else:
                    self._log(
                        f"Failed to queue task: {option_name}. Worker queue might be full.",
                        "error",
                    )
            else:
                self._log(f"No task function defined for: {option_name}", "error")

        # If no tasks were successfully added, re-enable button immediately
        with self.active_tasks_lock:
            if self.active_tasks == 0:
                self.run_button.configure(state=tk.NORMAL)
                self._log("No tasks were successfully queued.", "warning")

    def _on_task_complete(self, task_name: str, result: any, error: Optional[str]):
        """Generic callback executed in the main thread when a task finishes."""
        logger.debug(f"Callback received for task: {task_name}, Error: {error}")
        if error:
            self._log(f"Error running {task_name}: {error}", "error")
        else:
            # Log the result if it's informative (tasks should return strings or simple dicts)
            if isinstance(result, str) and result:
                self._log(f"{task_name} Result:\n{result}", "success")
            elif isinstance(result, dict) and result.get("message"):
                log_level = "success" if result.get("success", True) else "warning"
                self._log(f"{task_name}: {result['message']}", log_level)
            else:
                self._log(f"{task_name} completed successfully.", "success")

        # Decrement counter and check if all tasks are done
        with self.active_tasks_lock:
            self.active_tasks -= 1
            if self.active_tasks <= 0:
                self.active_tasks = 0  # Ensure it doesn't go below zero
                logger.info("All queued tasks finished.")
                self._log("All selected optimizations finished.", "info")
                if self.root.winfo_exists():
                    self.run_button.configure(state=tk.NORMAL)

    # --- Task Functions (Executed by Worker Thread) ---

    def _clean_temp_files_task(self) -> dict:
        """Task to clean temporary files."""
        logger.info("Worker: Running clean_temp_files task...")
        try:
            # Ensure PerformanceOptimizer is instantiated correctly
            # It might be better to pass the core/optimizer instance to the GUI
            optimizer = PerformanceOptimizer()
            success = optimizer.clean_temp_files()
            message = (
                "Temporary files cleaned successfully."
                if success
                else "Failed to clean temporary files (or none found)."
            )
            logger.info(f"Worker: clean_temp_files task finished. Success: {success}")
            return {"success": success, "message": message}
        except Exception as e:
            logger.exception("Worker: Error in clean_temp_files task")
            raise GuiException(
                f"Cleaning temp files failed: {e}"
            )  # Raise custom exception

    def _check_disk_usage_task(self) -> str:
        """Task to check disk usage using the core performance optimizer."""
        logger.info("Worker: Running check_disk_usage task...")
        log_messages = []
        try:
            optimizer = PerformanceOptimizer()
            disk_info = optimizer.get_disk_usage()

            if not disk_info:
                return "No physical disk partitions found."

            for device, info in disk_info.items():
                try:
                    total_gb = info["total"] / (1024**3)
                    used_gb = info["used"] / (1024**3)
                    free_gb = info["free"] / (1024**3)
                    percent_used = info["percent"]

                    msg = f"Drive {device}: "
                    msg += f"Total: {total_gb:.1f} GB, "
                    msg += f"Used: {used_gb:.1f} GB ({percent_used:.1f}%), "
                    msg += f"Free: {free_gb:.1f} GB"
                    log_messages.append(msg)

                    if percent_used > 90:
                        log_messages.append(
                            f"  WARNING: Drive {device} is over 90% full!"
                        )
                    elif percent_used > 80:
                        log_messages.append(f"  INFO: Drive {device} is over 80% full.")
                except Exception as e:
                    log_messages.append(f"Error processing drive {device}: {e}")

            logger.info("Worker: check_disk_usage task finished.")
            return (
                "\n".join(log_messages)
                if log_messages
                else "Could not retrieve disk usage."
            )
        except Exception as e:
            logger.exception("Worker: Error in check_disk_usage task")
            raise GuiException(f"Checking disk usage failed: {e}")

    def _get_startup_programs_task(self) -> str:
        """Task to list startup programs (Windows only)."""
        logger.info("Worker: Running get_startup_programs task...")
        if platform.system() != "Windows":
            logger.warning(
                "Worker: get_startup_programs task skipped (Not on Windows)."
            )
            return "Startup program listing is only available on Windows."

        log_messages = ["Scanning Windows startup programs..."]
        startup_locations = [
            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
            ),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
            ),
            (
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            ),
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            ),
            # Add Wow6432Node paths for 32-bit apps on 64-bit Windows if needed
            (
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Run",
            ),
        ]
        found_any = False
        for hkey, key_path in startup_locations:
            try:
                # Use KEY_READ | KEY_WOW64_64KEY for 64-bit view, KEY_WOW64_32KEY for 32-bit if needed
                key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
                log_messages.append(f"\n--- Location: {key_path} ---")
                try:
                    i = 0
                    while True:
                        name, value, _ = winreg.EnumValue(key, i)
                        log_messages.append(f"  {name}: {value}")
                        found_any = True
                        i += 1
                except OSError:  # Reached end of enumeration
                    if i == 0:  # No items found in this key
                        log_messages.append("  (No items found)")
                finally:
                    winreg.CloseKey(key)
            except FileNotFoundError:
                log_messages.append(f"\n--- Location: {key_path} ---")
                log_messages.append("  (Registry key not found)")
            except Exception as e:
                log_messages.append(f"\nError accessing {key_path}: {e}")

        if not found_any:
            log_messages = ["No startup programs found in common registry locations."]

        logger.info("Worker: get_startup_programs task finished.")
        return "\n".join(log_messages)

    def _optimize_power_settings_task(self) -> dict:
        """Task to optimize power settings using the core performance optimizer."""
        logger.info("Worker: Running optimize_power_settings task...")
        if platform.system() != "Windows":
            logger.warning(
                "Worker: optimize_power_settings task skipped (Not on Windows)."
            )
            return {
                "success": False,
                "message": "Power settings optimization is only available on Windows.",
            }

        messages = []
        try:
            optimizer = PerformanceOptimizer()
            result = optimizer.optimize_system("power_settings")

            if result["success"]:
                messages.append("Power settings optimization completed successfully.")
                messages.append(f"Tasks completed: {result['tasks_completed']}")
                if result.get("power_profile"):
                    messages.append(f"Active power profile: {result['power_profile']}")
            else:
                if result.get("failed_tasks"):
                    messages.append(
                        f"Failed tasks: {', '.join(result['failed_tasks'])}"
                    )
                messages.append("Some power optimization tasks failed.")

            logger.info("Worker: optimize_power_settings task finished.")
            return {"success": result["success"], "message": "\n".join(messages)}

        except Exception as e:
            error_msg = f"An unexpected error occurred during power optimization: {e}"
            messages.append(error_msg)
            logger.exception("Worker: Error in optimize_power_settings task")
            return {"success": False, "message": "\n".join(messages)}

    def _run_disk_cleanup_task(self) -> dict:
        """Task to run disk cleanup using the core performance optimizer."""
        logger.info("Worker: Running run_disk_cleanup task...")
        if platform.system() != "Windows":
            logger.warning("Worker: run_disk_cleanup task skipped (Not on Windows).")
            return {
                "success": False,
                "message": "Disk Cleanup is only available on Windows.",
            }

        messages = []
        try:
            optimizer = PerformanceOptimizer()
            cleanup_result = optimizer.clean_temp_files()

            if cleanup_result.get("success", False):
                messages.append("Disk cleanup completed successfully.")
                if "files_removed" in cleanup_result:
                    messages.append(f"Files removed: {cleanup_result['files_removed']}")
                if "space_freed" in cleanup_result:
                    space_freed_gb = cleanup_result["space_freed"] / (1024**3)
                    messages.append(f"Space freed: {space_freed_gb:.2f} GB")
            else:
                if "error" in cleanup_result:
                    messages.append(f"Cleanup failed: {cleanup_result['error']}")
                else:
                    messages.append("Cleanup completed with no changes.")

            logger.info("Worker: Disk cleanup task finished.")
            return {
                "success": cleanup_result.get("success", False),
                "message": "\n".join(messages),
            }

        except Exception as e:
            error_msg = f"An unexpected error occurred during disk cleanup: {e}"
            messages.append(error_msg)
            logger.exception("Worker: Error in run_disk_cleanup task")
            return {"success": False, "message": "\n".join(messages)}

    # --- Application Lifecycle ---

    def run(self):
        """Start the Tkinter main loop."""
        logger.info("Starting AdaptiveGUI main loop...")
        self.root.mainloop()

    def on_close(self):
        """Handles window closing action."""
        logger.info("Close requested. Stopping worker and closing application...")
        # Disable buttons immediately
        try:
            if self.run_button.winfo_exists():
                self.run_button.configure(state=tk.DISABLED)
            if self.exit_button.winfo_exists():
                self.exit_button.configure(state=tk.DISABLED)
        except tk.TclError:
            pass  # Window might already be closing

        # Stop the worker thread gracefully
        self.worker.stop(timeout=2.0)  # Wait up to 2 seconds

        # Destroy the main window
        if self.root.winfo_exists():
            self.root.destroy()
        logger.info("Application closed.")


if __name__ == "__main__":
    # Setup basic logging for standalone run
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    gui = AdaptiveGUI()
    gui.run()
