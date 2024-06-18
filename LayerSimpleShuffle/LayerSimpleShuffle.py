import nuke

# 채널 이름 분류 함수
def get_channel_passes(node):
    main_pass = []
    extra_pass = []
    aov_pass = []
    light_pass = []
    etc_pass = []

    # 선택된 노드의 채널 가져오기
    channels = list(set(channel.split('.')[0] for channel in node.channels()))

    # 'rgba'와 'alpha' 채널 제거
    channels = [channel for channel in channels if channel not in ["rgba", "alpha"]]
    
    # 메인 패스
    main_pass_names = ["lighting", "GI", "reflect", "refract", "specular", "SSS", "Self_Illumination", "selfIllum", "caustics", "atmosphere", "background"]
    for channel in main_pass_names:
        if channel in channels:
            main_pass.append(channel)
            channels.remove(channel)

    # 엑스트라 패스
    extra_pass_names = ["coat_filter", "coat_reflection", "coat_specular", "sheen_filter", "sheen_reflection", "sheen_specular", "Toon", "toonLighting", "toonSpecular"]
    for channel in channels:
        if any(name in channel for name in ["raw", "Filter"]):
            extra_pass.append(channel)
        elif channel in extra_pass_names:
            extra_pass.append(channel)

    for channel in extra_pass:
        if channel in channels:
            channels.remove(channel)

    # AOV 패스
    aov_pass_names = ["depth", "cryptomatte", "cryptomatte00", "cryptomatte01", "cryptomatte02", "bumpNormals", "coatGloss", "coverage", "custom_color", "DR", "diffuse", "extraTex", "LightingAnalysis", "materialID", "materialSelect", "matteShadow", "metalness", "multimatte", "multimatteID", "noise_level", "normals", "objectId", "objectSelect", "reflIOR", "reflGloss", "refrGloss", "renderId", "render_time", "sampleRate", "samplerInfo", "shadow", "sheenGloss", "totalLight", "unclampedColor", "VRScansPaintMask", "VRScansZoneMask", "velocity", "zDepth", "albedo"]
    for channel in aov_pass_names:
        if channel in channels:
            aov_pass.append(channel)
            channels.remove(channel)

    # 라이트 패스
    light_keywords = ["Light", "VRay", "LGT", "light", "key", "fill", "rim", "top"]
    light_pass = [channel for channel in channels if any(keyword.lower() in channel.lower() for keyword in light_keywords)]
    for channel in light_pass:
        if channel in channels:
            channels.remove(channel)

    # 기타 패스
    etc_pass = channels

    return main_pass, extra_pass, aov_pass, light_pass, etc_pass

# 각 패스의 백드롭 색상 지정
pass_colors = {
    "main_pass": (0.8, 0.8, 0.95),
    "extra_pass": (0.8, 0.95, 0.8),
    "aov_pass": (0.95, 0.8, 0.8),
    "light_pass": (0.95, 0.95, 0.8),
    "etc_pass": (0.8, 0.95, 0.95),
}

# 노드 생성 및 정렬
def create_shuffles(pass_name, layers, xpos, ypos, read_node):
    nodes = []

    # Read 노드를 복사하여 메인 Dot 노드의 왼쪽에 배치
    read_copy = nuke.nodes.Read(file=read_node['file'].value())
    read_copy.setXYpos(xpos - 200, ypos)
    
    main_dot = nuke.nodes.Dot()
    main_dot.setInput(0, read_copy)
    main_dot.setXYpos(xpos, ypos)
    ypos += 100
    
    previous_dot = main_dot

    for layer in layers:
        new_dot = nuke.nodes.Dot()
        new_dot.setInput(0, previous_dot)
        new_dot.setXYpos(previous_dot.xpos() + 200, previous_dot.ypos())
        
        shuffle2_node = nuke.nodes.Shuffle2()
        shuffle2_node.setInput(0, new_dot)
        shuffle2_node['in1'].setValue(layer)
        shuffle2_node['label'].setValue(layer)
        shuffle2_node['postage_stamp'].setValue(1)
        shuffle2_node.setName(f"Shuffle2_{layer}")
        shuffle2_node.setXYpos(new_dot.xpos() - 34, new_dot.ypos() + 200)
        
        previous_dot = new_dot
        nodes.append(shuffle2_node)
    
    create_backdrop(pass_name, nodes, pass_colors[pass_name], main_dot)
    return nodes, ypos + 400  # ypos를 더 많이 증가시켜 다음 그룹과의 간격을 확보

# 백드롭 생성
def create_backdrop(label, nodes, color, main_dot):
    if not nodes:
        return
    
    min_x = min(node.xpos() for node in nodes + [main_dot])
    min_y = min(node.ypos() for node in nodes + [main_dot])
    max_x = max(node.xpos() for node in nodes + [main_dot])
    max_y = max(node.ypos() for node in nodes + [main_dot])

    backdrop = nuke.nodes.BackdropNode()
    backdrop['bdwidth'].setValue(max_x - min_x + 400)
    backdrop['bdheight'].setValue(max_y - min_y + 400)
    backdrop.setXYpos(min_x - 100, min_y - 200)  # 더 위쪽으로 생성
    
    # 색상 값을 정수로 변환하여 설정
    r, g, b = [int(c * 255) for c in color]
    color_value = (r << 24) + (g << 16) + (b << 8) + 255
    backdrop['tile_color'].setValue(color_value)
    backdrop['label'].setValue(label)
    backdrop['note_font_size'].setValue(100)  # 폰트 크기 설정

# 전체 레이어 셔플링 함수
def shuffle_layers():
    node = nuke.selectedNode()
    xpos, ypos = node.xpos(), node.ypos() + 200

    main_pass, extra_pass, aov_pass, light_pass, etc_pass = get_channel_passes(node)

    all_nodes = {"main_pass": [], "light_pass": []}

    for pass_name, layers in [
        ("main_pass", main_pass),
        ("extra_pass", extra_pass),
        ("aov_pass", aov_pass),
        ("light_pass", light_pass),
        ("etc_pass", etc_pass)
    ]:
        if layers:
            nodes, ypos = create_shuffles(pass_name, layers, xpos, ypos, node)
            if pass_name in all_nodes:
                all_nodes[pass_name].extend(nodes)
            ypos += 300  # 다음 그룹의 시작 위치

    # Merge 노드 생성
    for pass_name in ["main_pass", "light_pass"]:
        if all_nodes[pass_name]:
            first_shuffle_node = all_nodes[pass_name][0]
            merge_node = nuke.nodes.Merge2()
            merge_node.setInput(0, all_nodes[pass_name][0])
            input_index = 1
            for i in range(1, len(all_nodes[pass_name])):
                if input_index == 2:
                    input_index += 1  # Skip index 2
                merge_node.setInput(input_index, all_nodes[pass_name][i])
                input_index += 1
            merge_node['operation'].setValue('plus')
            merge_node.setXYpos(first_shuffle_node.xpos(), first_shuffle_node.ypos() + 300)

    nuke.message("Layers shuffled into individual Shuffle2 nodes.")
    