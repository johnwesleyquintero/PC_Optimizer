import argparse
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import time
import traceback
from src.core.sentinel_pc import SentinelPC
from src.core.performance_optimizer import PerformanceOptimizer
from src.core.monitoring_manager import MonitoringManager
import psutil
import threading

class SentinelPCApp:
    def __init__(self, root):
        self.root = root
        self.sentinel = SentinelPC()
        self.root.title(f"SentinelPC v{SentinelPC.VERSION}")
        self.performance_optimizer = PerformanceOptimizer()
        self.monitoring_manager = MonitoringManager()
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

        # System metrics frame
        metrics_frame = ttk.LabelFrame(main_frame, text="System Metrics")
        metrics_frame.pack(fill='x', pady=5)

        # CPU usage
        self.cpu_label = ttk.Label(metrics_frame, text="CPU Usage: --%")
        self.cpu_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Memory usage
        self.mem_label = ttk.Label(metrics_frame, text="Memory Usage: --%")
        self.mem_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Disk usage
        self.disk_label = ttk.Label(metrics_frame, text="Disk Usage: --%")
        self.disk_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')

        # Network usage
        self.network_label = ttk.Label(metrics_frame, text="Network I/O: -- KB/s")
        self.network_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Optimization controls frame
        controls_frame = ttk.LabelFrame(main_frame, text="Optimization Controls")
        controls_frame.pack(fill='x', pady=5)

        # Preset selection
        preset_frame = ttk.Frame(controls_frame)
        preset_frame.pack(fill='x', pady=5, padx=5)

        ttk.Label(preset_frame, text="Optimization Preset:").pack(side='left')
        self.preset_combobox = ttk.Combobox(preset_frame, 
            values=["Basic", "Advanced", "Custom"], 
            state="readonly")
        self.preset_combobox.current(0)
        self.preset_combobox.pack(side='left', padx=5)

        configure_btn = ttk.Button(preset_frame, 
            text="Configure",
            command=self.configure_preset)
        configure_btn.pack(side='left')

        # Optimize button with progress
        optimize_frame = ttk.Frame(controls_frame)
        optimize_frame.pack(fill='x', pady=5, padx=5)

        optimize_btn = ttk.Button(
            optimize_frame,
            text="Optimize System",
            command=self.optimize_system
        )
        optimize_btn.pack(side='left')

        self.progress_bar = ttk.Progressbar(optimize_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=5)

        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side='left', padx=5)

        self.details_button = ttk.Button(
            status_frame,
            text="Details",
            state='disabled',
            command=self.show_error_details
        )
        self.details_button.pack(side='right', padx=5)

    def optimize_system(self):
        try:
            self.status_label.config(text="Starting optimization...")
            self.progress_bar['value'] = 0
            self.root.update()
            
            # Initialize optimization
            if not self.performance_optimizer.initialize(self.preset_combobox.get().lower()):
                raise Exception("Failed to initialize optimization")
            self.progress_bar['value'] = 20
            
            # Perform optimization
            self.status_label.config(text="Optimizing system performance...")
            if self.performance_optimizer.optimize_system():
                self.status_label.config(text="Optimization completed successfully!")
                self.progress_bar['value'] = 100
            else:
                self.status_label.config(text="Optimization completed with some issues.")
                self.progress_bar['value'] = 100
                
        except Exception as e:
            logging.error(f"Optimization failed: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
            self.details_button.config(state='normal')
            self.current_error = str(e)

        # Preset selection
        preset_frame = ttk.Frame(main_frame)
        preset_frame.pack(fill='x', pady=5)

        ttk.Label(preset_frame, text="Optimization Preset:").pack(side='left', padx=5)
        self.preset_combobox = ttk.Combobox(preset_frame, 
            values=["Basic", "Advanced", "Custom"], 
            state="readonly")
        self.preset_combobox.current(0)
        self.preset_combobox.pack(side='left', padx=5)

        configure_btn = ttk.Button(preset_frame, 
            text="Configure",
            command=self.configure_preset)
        configure_btn.pack(side='left', padx=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack(side='left', pady=5)
        
        self.details_button = ttk.Button(
            main_frame,
            text="Details",
            state='disabled',
            command=self.show_error_details
        )
        self.details_button.pack(side='right', padx=5)

        # System metrics frame
        metrics_frame = ttk.Frame(main_frame)
        metrics_frame.pack(fill='x', pady=10)

        # CPU usage
        self.cpu_label = ttk.Label(metrics_frame, text="CPU Usage: --%")
        self.cpu_label.grid(row=0, column=0, padx=5, sticky='w')

        # Memory usage
        self.mem_label = ttk.Label(metrics_frame, text="Memory Usage: --%")
        self.mem_label.grid(row=0, column=1, padx=5, sticky='w')

        # Initialize system monitor
        self.monitor = SystemMonitor(self)
        self.root.protocol('WM_DELETE_WINDOW', self.stop_monitoring)

    def stop_monitoring(self):
        self.monitor.stop()
        self.root.destroy()

    def update_metrics(self):
        metrics = self.monitoring_manager.collect_metrics()
        if metrics:
            self.cpu_label.config(text=f"CPU Usage: {metrics.cpu_percent:.1f}%")
            self.mem_label.config(text=f"Memory Usage: {metrics.memory_percent:.1f}%")
            
            # Update disk usage (average of all partitions)
            avg_disk = sum(metrics.disk_usage.values()) / len(metrics.disk_usage) if metrics.disk_usage else 0
            self.disk_label.config(text=f"Disk Usage: {avg_disk:.1f}%")
            
            # Calculate network throughput
            bytes_total = metrics.network_io['bytes_sent'] + metrics.network_io['bytes_recv']
            throughput = bytes_total / 1024  # Convert to KB
            self.network_label.config(text=f"Network I/O: {throughput:.1f} KB/s")
        
        self.root.after(1000, self.update_metrics)

class SystemMonitor:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = threading.Thread(target=self.monitor_loop)
        self.thread.start()

    def monitor_loop(self):
        self.running = True
        while self.running:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            self.app.root.after(0, self.app.update_metrics, cpu, mem)
            time.sleep(1)

    def stop(self):
        self.running = False
        self.thread.join()

    def optimize_system(self):
        try:
            steps = [
                ("Cleaning temporary files", 20),
                ("Optimizing registry", 30),
                ("Defragmenting disks", 40),
                ("Finalizing optimizations", 10)
            ]
            
            self.status_label.config(text="Preparing optimization...")
            self.progress_bar['value'] = 0
            self.root.update()
            
            for description, increment in steps:
                self.status_label.config(text=description)
                self.progress_bar.step(increment)
                self.root.update()
                # Simulated work delay - replace with actual optimization calls
                self.root.after(1000)
            
            self.status_label.config(text="Optimization completed successfully!")
            self.progress_bar['value'] = 100
            if self.sentinel.optimize_system():
                self.status_label.config(text="Optimization completed successfully!")
            else:
                self.status_label.config(text="Optimization completed with some issues.")
        except Exception as e:
            error_id = f"ERR-{time.strftime('%Y%m%d-%H%M%S')}"
            user_message = self.get_user_friendly_error(e)
            technical_details = f"{error_id}: {str(e)}\n{''.join(traceback.format_exc())}"
            
            self.status_label.config(text=f"{user_message} (Error ID: {error_id})")
            self.details_button.config(state='normal')
            self.current_error = technical_details
            logging.error(technical_details)

    def show_error_details(self):
        messagebox.showerror("Technical Details", self.current_error)

    def get_user_friendly_error(self, error):
        error_map = {
            PermissionError: "Please run as administrator to perform system optimizations",
            FileNotFoundError: "Required system file not found - verify system integrity",
            Exception: "An unexpected error occurred during optimization"
        }
        return error_map.get(type(error), "An unexpected error occurred")

    def configure_preset(self):
        selected_preset = self.preset_combobox.get()
        if selected_preset == "Custom":
            self.show_custom_config_dialog()

    def show_custom_config_dialog(self):
        config_win = tk.Toplevel(self.root)
        config_win.title("Custom Configuration")
        
        # Add configuration options here
        ttk.Label(config_win, text="Custom optimization settings").pack(pady=10)
        
        # Example checkbox
        self.registry_clean_var = tk.BooleanVar()
        ttk.Checkbutton(config_win, 
            text="Perform deep registry clean",
            variable=self.registry_clean_var).pack(anchor='w')

        ttk.Button(config_win, 
            text="Apply", 
            command=lambda: self.save_custom_config(config_win)).pack(pady=10)

    def save_custom_config(self, window):
        window.destroy()
        self.status_label.config(text="Custom settings saved")

def main():
    parser = argparse.ArgumentParser(description='SentinelPC - System Optimization Tool')
    parser.add_argument('--version', action='version', version=f'SentinelPC {SentinelPC.VERSION}')
    
    args = parser.parse_args()
    
    root = tk.Tk()
    app = SentinelPCApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()