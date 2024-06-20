import nuke
import os
import subprocess
import platform

def open_file_knob_directory():
    selected_nodes = nuke.selectedNodes()

    if not selected_nodes:
        nuke.message("No node selected.")
        return

    for node in selected_nodes:
        file_knob = node.knob('file')
        if file_knob:
            file_path = file_knob.value()
            if file_path:
                directory = os.path.dirname(file_path)
                if platform.system() == "Windows":
                    subprocess.Popen(['explorer', os.path.normpath(directory)])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(['open', directory])
                else:  # Linux
                    subprocess.Popen(['xdg-open', directory])
            else:
                nuke.message("File knob is empty.")
        else:
            nuke.message(f"No File knob found in node {node.name()}.")

# Add the function to a menu item for easy access
menu = nuke.menu("Nuke")
menu.addCommand("Plugins/Open File Knob Directory", open_file_knob_directory, "f6")