import nuke

class SyncModePlugin:
    def __init__(self):
        self.sync_mode = False

    def toggle_sync_mode(self):
        self.sync_mode = not self.sync_mode
        self.display_status()
        if self.sync_mode:
            nuke.addKnobChanged(self.knob_changed, nodeClass='*')
        else:
            nuke.removeKnobChanged(self.knob_changed)

    def knob_changed(self):
        if self.sync_mode:
            sender = nuke.thisNode()
            knob_name = nuke.thisKnob().name()
            knob_value = self.get_knob_value(sender, knob_name)
            self.apply_to_selected_nodes(sender, knob_name, knob_value)

    def get_knob_value(self, node, knob_name):
        return node[knob_name].value()

    def apply_to_selected_nodes(self, sender, knob_name, knob_value):
        for node in nuke.selectedNodes():
            if node.Class() == sender.Class() and node != sender:
                if knob_name in node.knobs():
                    node[knob_name].setValue(knob_value)

    def display_status(self):
        message = "Sync Mode ON" if self.sync_mode else "Sync Mode OFF"
        nuke.message(message)

# Create an instance of the plugin
sync_mode_plugin = SyncModePlugin()

# UI Setup
nuke.menu("Nuke").addCommand("Plugins/Toggle Sync Mode", SyncModePlugin().toggle_sync_mode, "F8")
