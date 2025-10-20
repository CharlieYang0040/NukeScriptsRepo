import os
import sys

# 플러그인 루트 디렉토리를 기반으로 `libs` 폴더를 sys.path에 추가합니다.
# 이를 통해 플러그인에 포함된(vendored) 라이브러리를 우선적으로 로드할 수 있습니다.
plugin_root = os.path.dirname(__file__)
libs_path = os.path.join(plugin_root, 'libs')

if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

# `icons` 폴더를 Nuke의 플러그인 경로에 추가하여 아이콘을 로드할 수 있도록 합니다.
# nuke.pluginAddPath()는 상대 경로도 처리해줍니다.
import nuke
nuke.pluginAddPath('./icons')
