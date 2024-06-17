import os
import shutil
from pathlib import Path
import sys

def install_plugin():
    # Set paths
    home_dir = Path.home()
    nuke_dir = home_dir / ".nuke"
    plugin_dir_name = "LayerSimpleShuffle"
    plugin_dir_path = nuke_dir / plugin_dir_name
    init_file_path = nuke_dir / "init.py"
    plugin_path_line = f"nuke.pluginAddPath('./{plugin_dir_name}')"

    # Determine if running as a bundled executable
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent

    source_plugin_dir = bundle_dir / plugin_dir_name

    # Create the .nuke directory if it doesn't exist
    nuke_dir.mkdir(exist_ok=True)

    # Copy the plugin folder
    if not source_plugin_dir.exists():
        print(f"Source plugin directory {source_plugin_dir} does not exist.")
        return
    
    if plugin_dir_path.exists():
        shutil.rmtree(plugin_dir_path)
    shutil.copytree(source_plugin_dir, plugin_dir_path)

    # Create init.py file if it doesn't exist
    if not init_file_path.exists():
        init_file_path.touch()

    # Read init.py content
    with init_file_path.open("r", encoding="utf-8") as init_file:
        lines = init_file.readlines()

    # Add plugin path to init.py if it doesn't exist
    if plugin_path_line not in [line.strip() for line in lines]:
        with init_file_path.open("a", encoding="utf-8") as init_file:
            if not lines or not lines[-1].endswith('\n'):
                init_file.write('\n')
            init_file.write(plugin_path_line + '\n')

    print("Plugin installed successfully.")

if __name__ == "__main__":
    install_plugin()
