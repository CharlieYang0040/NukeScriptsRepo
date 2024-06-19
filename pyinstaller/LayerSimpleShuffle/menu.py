import nuke
import LayerSimpleShuffle

shuffle_tool = LayerSimpleShuffle.NukeShuffleTool()
ChannelMenu = nuke.menu('Nuke')
ChannelMenu.addCommand('Plugins/LayerSimpleShuffle', lambda: shuffle_tool.startShuffle(), 'ctrl+r')