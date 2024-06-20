import os
import nuke

def add_all_plugin_paths():
    # .nuke 폴더 경로
    nuke_dot_nuke = os.path.expanduser('~/.nuke')

    # 모든 하위 폴더를 탐색
    for root, dirs, files in os.walk(nuke_dot_nuke):
        # .gizmo, .nk 파일이 있는 폴더 경로를 추가
        if any(f.endswith('.gizmo') or f.endswith('.nk') or f.endswith('.py') for f in files):
            nuke.pluginAddPath(root)

add_all_plugin_paths()
