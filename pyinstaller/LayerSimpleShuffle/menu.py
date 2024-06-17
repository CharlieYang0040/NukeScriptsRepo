import nuke
import LayerSimpleShuffle

ChannelMenu = nuke.menu('Nodes').menu('Channel')
ChannelMenu.addCommand('LayerSimpleShuffle', 'LayerSimpleShuffle.shuffle_layers()', 'ctrl+r')