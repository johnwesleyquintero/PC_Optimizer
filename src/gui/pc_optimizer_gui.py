import tkinter as tk
from tkinter import ttk
import psutil
import threading
from ..core.environment_manager import EnvironmentConfig

class AdaptiveGUI:
    def __init__(self):
        self.config = EnvironmentConfig()
        self.root = tk.Tk()
        self.root.title("PC Optimizer")
        self._apply_theme()

        self.optimization_options = {
            "Clean Temporary Files": self.clean_temp_files,
            "Check Disk Usage": self.check_disk_usage,
            "Manage Startup Programs": self.manage_startup_programs,
            "Optimize Power Settings": self.optimize_power_settings,
            "Run Disk Cleanup": self.run_disk_cleanup,
        }
        self.create_widgets()

    def _apply_theme(self):
        self.root.configure(bg=self.config.theme['base'])

        style = ttk.Style()
        style.theme_create('adaptive', settings={
            'TLabel': {
                'configure': {
                    'background': self.config.theme['base'],
                    'foreground': self.config.theme['text']
                }
            },
            'TButton': {
                'configure': {
                    'background': self.config.theme['primary'],
                    'foreground': self.config.theme['text']
                },
                'map': {'background': [('active', self._adjust_color(self.config.theme['primary'], -20))]}
            },
            'TCheckbutton': {
                'configure': {
                    'background': self.config.theme['base'],
                    'foreground': self.config.theme['text']
                }
            },
            'TFrame': {
                'configure': {
                    'background': self.config.theme['base']
                }
            }
        })
        style.theme_use('adaptive')

    def _adjust_color(self, hex_color, brightness_offset):
        # Implement color adjustment logic for hover effects (simplified for now)
        return hex_color

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Configure text widget tags
        self.log_text.tag_configure('warning', foreground='orange')
        self.log_text.tag_configure('error', foreground='red')

        options_frame = ttk.LabelFrame(main_frame, text="Optimization Options", padding="5")
        options_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.option_vars = {}
        row = 0
        for option in self.optimization_options:
            self.option_vars[option] = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text=option, variable=self.option_vars[option]).grid(row=row, column=0, sticky=tk.W)
            row += 1

        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding="5")
        log_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, height=10)
        self.log_text.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.grid(row=2, column=0, sticky=(tk.E, tk.W))
        ttk.Button(button_frame, text="Run Selected Optimizations", command=self.run_optimizations).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).grid(row=0, column=1, sticky=tk.E)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=2)
        options_frame.columnconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

    def run_optimizations(self):
        for option, var in self.option_vars.items():
            if var.get():
                self.log_text.insert(tk.END, f"Running {option}...\n")
                self.optimization_options[option]()
                self.log_text.insert(tk.END, f"{option} complete.\n")
        self.log_text.see(tk.END)  # Scroll to the end

    def clean_temp_files(self):
        from src.core.performance_optimizer import PerformanceOptimizer
        optimizer = PerformanceOptimizer()
        result = optimizer.clean_temp_files()
        if result:
            self.log_text.insert(tk.END, "Temporary files cleaned successfully.\n")
        else:
            self.log_text.insert(tk.END, "Failed to clean temporary files.\n")

    def check_disk_usage(self):
        import shutil
        import threading
        
        def check_disk():
            try:
                # Get disk usage for all mounted partitions
                for partition in psutil.disk_partitions():
                    if partition.fstype:
                        usage = shutil.disk_usage(partition.mountpoint)
                        total_gb = usage.total / (1024**3)
                        used_gb = usage.used / (1024**3)
                        free_gb = usage.free / (1024**3)
                        percent_used = (used_gb / total_gb) * 100
                        
                        msg = f"Drive {partition.mountpoint}:\n"
                        msg += f"Total: {total_gb:.1f} GB\n"
                        msg += f"Used: {used_gb:.1f} GB ({percent_used:.1f}%)\n"
                        msg += f"Free: {free_gb:.1f} GB\n\n"
                        
                        self.log_text.insert(tk.END, msg)
                        
                        # Warn if disk space is low
                        if percent_used > 90:
                            self.log_text.insert(tk.END, f"Warning: Drive {partition.mountpoint} is nearly full!\n", 'warning')
                            
                self.log_text.see(tk.END)
                
            except Exception as e:
                self.log_text.insert(tk.END, f"Error checking disk usage: {str(e)}\n", 'error')
        
        # Run disk check in a separate thread
        thread = threading.Thread(target=check_disk)
        thread.start()

    def manage_startup_programs(self):
        import winreg
        import threading
        
        def get_startup_programs():
            try:
                startup_locations = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
                ]
                
                self.log_text.insert(tk.END, "Scanning startup programs...\n")
                
                for hkey, key_path in startup_locations:
                    try:
                        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
                        self.log_text.insert(tk.END, f"\nStartup programs in {key_path}:\n")
                        
                        try:
                            i = 0
                            while True:
                                name, value, _ = winreg.EnumValue(key, i)
                                self.log_text.insert(tk.END, f"{name}: {value}\n")
                                i += 1
                        except WindowsError:
                            pass
                            
                        winreg.CloseKey(key)
                        
                    except WindowsError as e:
                        self.log_text.insert(tk.END, f"Error accessing {key_path}: {str(e)}\n", 'error')
                
                self.log_text.see(tk.END)
                
            except Exception as e:
                self.log_text.insert(tk.END, f"Error managing startup programs: {str(e)}\n", 'error')
        
        # Run startup check in a separate thread
        thread = threading.Thread(target=get_startup_programs)
        thread.start()

    def optimize_power_settings(self):
        import subprocess
        import threading
        
        def adjust_power_settings():
            try:
                # Get current power scheme
                result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True)
                self.log_text.insert(tk.END, "Current power schemes:\n")
                self.log_text.insert(tk.END, result.stdout)
                
                # Set to high performance
                self.log_text.insert(tk.END, "\nSetting power scheme to High Performance...\n")
                subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'])
                
                # Adjust specific settings
                subprocess.run(['powercfg', '/change', 'monitor-timeout-ac', '15'])
                subprocess.run(['powercfg', '/change', 'disk-timeout-ac', '0'])
                
                self.log_text.insert(tk.END, "Power settings optimized successfully.\n")
                
            except Exception as e:
                self.log_text.insert(tk.END, f"Error optimizing power settings: {str(e)}\n", 'error')
            
            self.log_text.see(tk.END)
        
        # Run power optimization in a separate thread
        thread = threading.Thread(target=adjust_power_settings)
        thread.start()

    def run_disk_cleanup(self):
        import subprocess
        import threading
        
        def execute_cleanup():
            try:
                self.log_text.insert(tk.END, "Starting Windows Disk Cleanup...
")
                
                # Calculate disk space before cleanup
                total_before = 0
                for partition in psutil.disk_partitions():
                    if partition.fstype:
                        usage = shutil.disk_usage(partition.mountpoint)
                        total_before += usage.used
                
                # Run disk cleanup
                process = subprocess.Popen(['cleanmgr', '/sagerun:1'], 
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
                
                self.log_text.insert(tk.END, "Disk Cleanup is running. This may take several minutes...\n")
                process.wait()
                
                # Calculate space freed
                total_after = 0
                for partition in psutil.disk_partitions():
                    if partition.fstype:
                        usage = shutil.disk_usage(partition.mountpoint)
                        total_after += usage.used
                
                space_freed = (total_before - total_after) / (1024**3)
                self.log_text.insert(tk.END, f"Disk Cleanup completed. Freed approximately {space_freed:.2f} GB\n")
                
            except Exception as e:
                self.log_text.insert(tk.END, f"Error during disk cleanup: {str(e)}\n", 'error')
            
            self.log_text.see(tk.END)
        
        # Run cleanup in a separate thread
        thread = threading.Thread(target=execute_cleanup)
        thread.start()

if __name__ == "__main__":
    gui = AdaptiveGUI()
    gui.root.mainloop()
