import nuke

sync_mode = False

def toggle_sync_mode():
    global sync_mode
    sync_mode = not sync_mode
    display_status()
    if sync_mode:
        nuke.addKnobChanged(knob_changed, nodeClass='*')
    else:
        nuke.removeKnobChanged(knob_changed)

def knob_changed():
    if sync_mode:
        sender = nuke.thisNode()
        knob_name = nuke.thisKnob().name()
        knob_value = sender[knob_name].value()

        for node in nuke.selectedNodes():
            if node.Class() == sender.Class() and node != sender:
                if knob_name in node.knobs():
                    node[knob_name].setValue(knob_value)

def display_status():
    global sync_mode
    message = "Sync Mode ON" if sync_mode else "Sync Mode OFF"
    nuke.message(message)

# UI Setup
nuke.menu("Nuke").addCommand("Custom/Toggle Sync Mode", toggle_sync_mode, "F8")
