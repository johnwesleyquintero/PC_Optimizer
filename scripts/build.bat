@echo off
pip install pyinstaller
pyinstaller --onefile --console --name PC_Optimizer_GUI_v2 --icon=wwwroot/Assets/Branding/app_icon.ico src/gui/pc_optimizer_gui_v2.py
pyinstaller --onefile --name PC_Optimizer_CLI_v2 --hidden-import config_manager_v2 --hidden-import performance_optimizer_v2 --icon=wwwroot/Assets/Branding/app_icon.ico pc_optimizer_cli_v2.py
