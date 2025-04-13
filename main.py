import argparse
import sys
from src.gui.pc_optimizer_gui_v2 import run_gui
from src.cli.pc_optimizer_cli_v2 import AdaptiveCLI

def main():
    parser = argparse.ArgumentParser(description='PC Optimizer - Unified Application')
    parser.add_argument('--gui', action='store_true', help='Run in GUI mode')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    
    args = parser.parse_args()
    
    if args.gui:
        run_gui()
    elif args.cli:
        cli = AdaptiveCLI()
        cli.run()
    else:
        # Default to GUI mode if no arguments provided
        run_gui()

if __name__ == "__main__":
    main()