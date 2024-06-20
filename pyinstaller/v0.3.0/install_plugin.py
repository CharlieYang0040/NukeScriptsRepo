import os
import shutil
from pathlib import Path
import sys

def install_plugin():
    # Set paths
    home_dir = Path.home()
    nuke_dir = home_dir / ".nuke"
    plugin_dirs = ["LayerSimpleShuffle", "Gizmos"]  # Include Gizmos directory for additional plugins

    # Determine if running as a bundled executable
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
    else:
        bundle_dir = Path(__file__).parent

    # Create the .nuke directory if it doesn't exist
    nuke_dir.mkdir(exist_ok=True)

    # Copy the plugin folders
    for plugin_dir_name in plugin_dirs:
        source_plugin_dir = bundle_dir / plugin_dir_name
        plugin_dir_path = nuke_dir / plugin_dir_name

        if not source_plugin_dir.exists():
            print(f"Source plugin directory {source_plugin_dir} does not exist.")
            return

        if plugin_dir_path.exists():
            shutil.rmtree(plugin_dir_path)
        shutil.copytree(source_plugin_dir, plugin_dir_path)

    # Overwrite init.py file with the new content
    init_file_path = nuke_dir / "init.py"
    new_init_content = '''
import os
import nuke

def add_all_plugin_paths():
    nuke_dot_nuke = os.path.expanduser('~/.nuke')
    for root, dirs, files in os.walk(nuke_dot_nuke):
        if any(f.endswith('.gizmo') or f.endswith('.nk') or f.endswith('.py') for f in files):
            nuke.pluginAddPath(root)

add_all_plugin_paths()
'''
    with open(init_file_path, "w", encoding="utf-8") as init_file:
        init_file.write(new_init_content)

    print("Plugin installed successfully.")

if __name__ == "__main__":
    install_plugin()
