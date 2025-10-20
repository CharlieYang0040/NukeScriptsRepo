# -*- coding: utf-8 -*-

import nuke
import sys
import os
import tempfile

def paste_image_from_clipboard():
    """
    클립보드에서 이미지를 가져와 Nuke Read 노드로 생성합니다.
    Windows 플랫폼에 최적화되어 있습니다.
    """
    try:
        # Pillow와 pywin32는 설치 스크립트를 통해 Nuke의 Python 환경에 설치되어야 합니다.
        from PIL import ImageGrab
        
        # ImageGrab.grabclipboard()는 클립보드에서 이미지를 가져오는 가장 간편한 방법입니다.
        img = ImageGrab.grabclipboard()

        if img is None:
            nuke.message("클립보드에 이미지가 없습니다.")
            return

        # 임시 파일로 저장 (PNG 포맷으로 투명도 보존)
        # tempfile.mkstemp는 파일 핸들과 경로를 반환하므로, 핸들은 닫아주어야 합니다.
        fd, temp_path = tempfile.mkstemp(suffix='.png', prefix='nuke_clipboard_')
        os.close(fd)
        
        img.save(temp_path, 'PNG')

        # Nuke 노드 생성은 메인 스레드에서 실행되어야 합니다.
        # menu.py를 통해 실행되는 코드는 이미 메인 스레드에서 동작하므로 안전합니다.
        read_node = nuke.createNode('Read')
        
        # Nuke는 파일 경로에 역슬래시(\) 대신 슬래시(/)를 사용합니다.
        read_node['file'].setValue(temp_path.replace('\\', '/'))
        
        # 생성된 Read 노드의 프레임 범위를 현재 프레임으로 설정합니다.
        current_frame = nuke.frame()
        read_node['first'].setValue(current_frame)
        read_node['last'].setValue(current_frame)
        
        print(f"Clipboard image saved to temporary file: {temp_path}")

    except ImportError:
        nuke.message("오류: 필수 패키지(Pillow)가 설치되지 않았습니다.\n"
                     "setup/install_windows.bat 스크립트를 실행하여 설치해주세요.")
    except Exception as e:
        nuke.message(f"알 수 없는 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()


def cleanup_temp_files():
    """
    Nuke 클립보드 플러그인으로 생성된 임시 PNG 파일들을 정리합니다.
    """
    temp_dir = tempfile.gettempdir()
    files_to_delete = []
    
    # 임시 디렉토리에서 플러그인이 생성한 파일들을 찾습니다.
    for filename in os.listdir(temp_dir):
        if filename.startswith('nuke_clipboard_') and filename.endswith('.png'):
            files_to_delete.append(os.path.join(temp_dir, filename))
            
    if not files_to_delete:
        nuke.message("삭제할 임시 클립보드 파일이 없습니다.")
        return
        
    deleted_count = 0
    errors = []
    
    # 찾은 파일들을 삭제합니다.
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            deleted_count += 1
        except OSError as e:
            errors.append(f"'{os.path.basename(file_path)}': {e.strerror}")
            
    # 결과 메시지를 생성합니다.
    message = f"{deleted_count}개의 임시 파일을 성공적으로 삭제했습니다."
    if errors:
        message += f"\n\n다음 {len(errors)}개 파일 삭제 중 오류가 발생했습니다:\n" + "\n".join(errors)
        
    nuke.message(message)
