import nuke
import nukescripts

def get_channel_passes(node):
    pass_categories = {
        "main_pass": ["lighting", "GI", "reflect", "refract", "specular", "SSS", "Self_Illumination", "selfIllum", "caustics", "atmosphere", "background"],
        "extra_pass": ["coat_filter", "coat_reflection", "coat_specular", "sheen_filter", "sheen_reflection", "sheen_specular", "Toon", "toonLighting", "toonSpecular"],
        "aov_pass": ["depth", "cryptomatte", "cryptomatte00", "cryptomatte01", "cryptomatte02", "bumpNormals", "coatGloss", "coverage", "custom_color", "DR", "diffuse", "extraTex", "LightingAnalysis", "materialID", "materialSelect", "matteShadow", "metalness", "multimatte", "multimatteID", "noise_level", "normals", "objectId", "objectSelect", "reflIOR", "reflGloss", "refrGloss", "renderId", "render_time", "sampleRate", "samplerInfo", "shadow", "sheenGloss", "totalLight", "unclampedColor", "VRScansPaintMask", "VRScansZoneMask", "velocity", "zDepth", "albedo"],
        "light_pass": ["Light", "VRay", "LGT", "light", "key", "fill", "rim", "top"]
    }
    categories = {k: [] for k in pass_categories.keys()}
    etc_pass = []

    channels = list(set(channel.split('.')[0] for channel in node.channels()))
    channels = [channel for channel in channels if channel not in ["rgba", "alpha"]]

    for channel in channels:
        added = False
        for category, names in pass_categories.items():
            if any(name in channel for name in names):
                categories[category].append(channel)
                added = True
                break
        if not added:
            etc_pass.append(channel)
    
    return categories["main_pass"], categories["extra_pass"], categories["aov_pass"], categories["light_pass"], etc_pass

class NukeShuffleTool:
    def __init__(self):
        self.distanceMult = 1
        self.pass_dicts = {
            "main_pass": {},
            "extra_pass": {},
            "aov_pass": {},
            "light_pass": {},
            "etc_pass": {}
        }
        self.rebuildStart_highestY = None
        self.pass_dict_list_missingEntries = {}

    def rgb_to_hex(self, r, g, b):
        # Convert RGB to Nuke hex color.
        return int('%02x%02x%02x%02x' % (r, g, b, 1), 16)

    def renamingHandler(self, name, mode="node", listWidget=None):
        name = str(name)
        num = 1
        if mode == "node":
            if nuke.exists(name):
                while nuke.exists(name + str(num)):
                    num += 1
                return name + str(num)
            return name
        elif mode == "list" and listWidget is not None:
            listItems = set(str(listWidget.item(i).text()) for i in range(listWidget.count()))
            if name in listItems:
                while True:
                    new_name = f"{name}_{num:02}"
                    if new_name not in listItems:
                        return new_name
                    num += 1
            return name

    def missingEntriesHandler(self, dictToCheck, missingEntriesStorage):
        for node in list(dictToCheck.keys()):
            try:
                nuke.exists(node.name())
            except ValueError:
                missingEntriesStorage[node] = dictToCheck.pop(node)

        for node in list(missingEntriesStorage.keys()):
            if nuke.exists(node.name()):
                dictToCheck[node] = missingEntriesStorage.pop(node)

    def findLastConnected(self, nodeToStartFrom, pass_dict_list):
        lastNode = nodeToStartFrom
        visited = set()

        def recursiveSearch(node):
            nonlocal lastNode
            visited.add(node)
            connections = nuke.dependentNodes(nuke.INPUTS | nuke.HIDDEN_INPUTS, node)
            for conn in connections:
                if conn not in visited and conn in pass_dict_list:
                    lastNode = conn
                    recursiveSearch(conn)

        recursiveSearch(nodeToStartFrom)
        return lastNode

    def shufflingLoop(self, passesList, enumStart, startingX, startingY, section, startDot, pass_dict, groupName):
        pass_colors = {
            "main_pass": self.rgb_to_hex(204-180, 229-180, 255-180),
            "extra_pass": self.rgb_to_hex(204-180, 255-180, 204-180),
            "aov_pass": self.rgb_to_hex(255-180, 204-180, 229-180),
            "light_pass": self.rgb_to_hex(255-180, 255-180, 204-180),
            "etc_pass": self.rgb_to_hex(230-180, 204-180, 255-180)
        }

        for index, item in enumerate(passesList, enumStart):
            createdNodes = []

            dot = nuke.nodes.Dot()
            dot.setXYpos(startingX + 250 * self.distanceMult, startingY)
            dot.connectInput(0, startDot)
            dot.knob("name").setValue(self.renamingHandler("Dot_" + item))

            for n in nuke.selectedNodes():
                n.setSelected(False)
            dot.setSelected(True)

            shuf = nuke.createNode("Shuffle2", inpanel=False)
            shuf.setXYpos(dot.xpos() - 33, dot.ypos() + 250)
            shuf.knob("in1").setValue(item)
            shuf.knob("name").setValue(self.renamingHandler(item))
            shuf.knob("postage_stamp").setValue(True)

            if createdNodes:
                for node in createdNodes:
                    node.setSelected(True)

            backd = nukescripts.autobackdrop.autoBackdrop()
            backd.setXYpos(int(shuf.xpos() - ((222 / 2) - 32)), int(shuf.ypos() - ((111 / 2) - 14) - 150))
            backd.knob("bdheight").setValue(backd["bdheight"].value() + 185 - 80)
            backd.knob("bdwidth").setValue(backd["bdwidth"].value() * 0.8)
            backd.knob("tile_color").setValue(pass_colors[groupName])
            backd.knob("label").setValue(item.split('_')[-1] if groupName == "light_pass" else item)
            backd.knob("name").setValue(self.renamingHandler("Backdrop_" + item))
            backd.knob("note_font_size").setValue(25)

            if len(nuke.selectedNodes()) == 1:
                backd.knob("bdwidth").setValue(backd.knob("bdwidth").value() + 160)
                backd.knob("bdheight").setValue(backd.knob("bdheight").value() + 50)

            for n in nuke.selectedNodes():
                n.setSelected(False)

            dot.setSelected(True)
            startingY = dot.ypos()
            startingX = dot.xpos()

            pass_dict[dot] = {"shuffleIndex": index, "layerName": item, "section": section}
            pass_dict[shuf] = {"shuffleIndex": index, "layerName": item, "section": section}
            pass_dict[backd] = {"shuffleIndex": index, "layerName": item, "section": section}

        for n in nuke.selectedNodes():
            n.setSelected(False)

    def shuffleLayers(self, targetNode, passes, pass_dict, currentShuffleIndex, startingDot, groupName):
        xpos, ypos = startingDot.xpos(), startingDot.ypos() + 0
        self.shufflingLoop(passes, currentShuffleIndex, xpos, ypos, groupName, startingDot, pass_dict, groupName)
        lastDot = self.findLastConnected(startingDot, pass_dict)
        newStartDot = None

        if groupName != "etc_pass":
            newStartDot = nuke.nodes.Dot()
            newStartDot.setInput(0, startingDot)
            newStartDot.setXYpos(xpos, lastDot.ypos() + 250)

        def create_backdrop(pass_dict, groupName, xpos, start_ypos):
            max_xpos = max(node.xpos() + node.screenWidth() for node in pass_dict.keys())
            max_ypos = max(node.ypos() for node in pass_dict.keys()) + 50

            backd = nukescripts.autobackdrop.autoBackdrop()
            backd.knob("label").setValue(groupName)
            backd.knob("note_font_size").setValue(70)
            backd.knob("bdwidth").setValue(max_xpos - xpos + 100)
            backd.knob("bdheight").setValue(max_ypos - start_ypos + 150)
            pass_colors = {
                "main_pass": self.rgb_to_hex(204-80, 229-80, 255-80),
                "extra_pass": self.rgb_to_hex(204-80, 255-80, 204-80),
                "aov_pass": self.rgb_to_hex(255-80, 204-80, 229-80),
                "light_pass": self.rgb_to_hex(255-80, 255-80, 204-80),
                "etc_pass": self.rgb_to_hex(230-80, 204-80, 255-80)
            }
            backd.knob("tile_color").setValue(pass_colors[groupName])
            backd.setXYpos(xpos - 50, start_ypos - 50)

            for node in pass_dict:
                backd.setInput(0, node)

        create_backdrop(pass_dict, groupName, xpos, startingDot.ypos())
        return newStartDot, pass_dict[lastDot]["shuffleIndex"] + 1

    def startShuffle(self):
        targetedNode = nuke.selectedNode()
        try:
            nuke.exists(targetedNode.name())
        except:
            nuke.message("\"Selected Node\" no longer exists!")
            return

        self.rebuildStart_highestY = 0
        startingSelection = nuke.selectedNodes()
        initialDot = nuke.nodes.Dot()
        initialDot.setInput(0, targetedNode)
        xpos, ypos = targetedNode.xpos(), targetedNode.ypos() + 200
        initialDot.setXYpos(xpos + 32, ypos)

        currentDot = initialDot
        currentShuffleIndex = 1

        passes = get_channel_passes(targetedNode)
        groupNames = ["main_pass", "extra_pass", "aov_pass", "light_pass", "etc_pass"]
        
        for groupName in groupNames:
            pass_list = passes[groupNames.index(groupName)]
            if pass_list:
                currentDot, currentShuffleIndex = self.shuffleLayers(targetedNode, pass_list, self.pass_dicts[groupName], currentShuffleIndex, currentDot, groupName)

        for n in nuke.selectedNodes():
            n.setSelected(False)
        for sel in reversed(startingSelection):
            sel.setSelected(True)