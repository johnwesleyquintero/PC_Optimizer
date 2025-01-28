import tkinter as tk
from tkinter import ttk
from src.core.environment_manager import EnvironmentConfig

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
        from src.core.performance_optimizer_v2 import PerformanceOptimizerV2
        optimizer = PerformanceOptimizerV2()
        result = optimizer.clean_temp_files()
        if result:
            self.log_text.insert(tk.END, "Temporary files cleaned successfully.\n")
        else:
            self.log_text.insert(tk.END, "Failed to clean temporary files.\n")

    def check_disk_usage(self):
        # Placeholder - Replace with actual implementation
        pass

    def manage_startup_programs(self):
        # Placeholder - Replace with actual implementation
        pass

    def optimize_power_settings(self):
        # Placeholder - Replace with actual implementation
        pass

    def run_disk_cleanup(self):
        # Placeholder - Replace with actual implementation
        pass

if __name__ == "__main__":
    gui = AdaptiveGUI()
    gui.root.mainloop()
