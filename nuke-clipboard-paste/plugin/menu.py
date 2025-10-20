# -*- coding: utf-8 -*-

import nuke
import os

try:
    # 플러그인 폴더 내의 모듈을 절대 경로로 임포트합니다.
    import paste_from_clipboard
    
    # Nuke 메뉴 생성
    toolbar = nuke.menu('Nuke')
    custom_menu = toolbar.addMenu('Plugins/Clipboard Paste', icon='clipboard_icon.png')
    
    # 메뉴에 명령어 추가
    # 명령어: paste_from_clipboard 모듈의 paste_image_from_clipboard 함수를 실행
    # 단축키: Ctrl+Shift+V
    custom_menu.addCommand(
        'Paste Image from Clipboard',
        'paste_from_clipboard.paste_image_from_clipboard()',
        'ctrl+shift+v'
    )
    
    # 구분선 추가
    custom_menu.addSeparator()
    
    # 임시 파일 정리 명령어 추가
    custom_menu.addCommand(
        'Clean Up Temporary Files',
        'paste_from_clipboard.cleanup_temp_files()'
    )

except ImportError as e:
    print(f"Nuke Clipboard Paste Error: Could not import modules. {e}")

except Exception as e:
    print(f"Nuke Clipboard Paste Error: Failed to initialize menu. {e}")
