"""
Grand Loong (hoolongvfx@gmail.com)
vimeo: https://vimeo.com/loong
linkedin: https://www.linkedin.com/in/grandloong
update
    v1.01:
        remove print
        Optimized some code
    v1.02:
        add profile setting other folder
        add new function collect read Node file in Group
"""

import os
from os.path import join as joinpath
import re
import zipfile
import shutil
import threading
import time
import configparser
import multiprocessing.pool
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import nuke


class NukeToPack:
    def __init__(self):
        script_dir = os.path.dirname(__file__)
        profile = joinpath(script_dir, 'profile.ini')
        nuke_file = nuke.Root().name()
        self.source_dir = os.path.dirname(nuke_file)
        if os.path.exists(profile):
            cf = configparser.ConfigParser()
            cf.read(profile, encoding='utf-8')
            self.source_dir = cf.get("root", "path")
        self.base_name = os.path.basename(nuke_file).split('.')[0]
        self.pack_dir = joinpath(self.source_dir, self.base_name)
        self.nuke_version = nuke.NUKE_VERSION_STRING
        if not os.path.exists(self.pack_dir):
            os.makedirs(self.pack_dir)
        self.pack_ = '[file dirname [value root.name]]/'
        # CPU 코어 수의 절반만 사용 (최소 2개)
        self.max_workers = max(2, multiprocessing.cpu_count() // 2)
        print(f"작업자 수: {self.max_workers}")

    def to_zip(self, packed_script):
        """
        파일들을 ZIP으로 압축
        packed_script: 저장된 .nk 파일의 경로
        """
        zipfilename = os.path.join(self.source_dir, f"{self.base_name}.zip")
        filelist = []
        
        # 복사된 파일들 추가
        for root, dirs, files in os.walk(self.pack_dir):
            for name in files:
                filelist.append(os.path.join(root, name))
        
        # 수정된 .nk 파일 추가
        filelist.append(packed_script)

        zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED, True)
        for tar in filelist:
            if tar == packed_script:
                # .nk 파일은 최상위에 저장
                arcname = os.path.basename(tar)
            else:
                # 나머지 파일들은 원래 구조 유지
                arcname = tar[len(self.pack_dir)+1:]
            print(f"압축 중: {arcname}")
            zf.write(tar, arcname)
        zf.close()

    @staticmethod
    def check_format(filepath):
        # 더 다양한 시퀀스 포맷 지원
        sequence_patterns = [
            r'(.+)(%\d*d)',  # %d, %04d 등
            r'(.+)(#+)',     # #, ####
            r'(.+)(\$F\d*)', # $F, $F4
            r'(.+)(\[\-?\d+\-?\d*\])'  # [1-100] 형식
        ]
        
        for pattern in sequence_patterns:
            if re.match(pattern, filepath):
                return False
        return True

    @staticmethod
    def unified_path_format(filepath):
        return filepath.replace('\\', '/')

    def convert(self):
        self.task = nuke.ProgressTask("NukeToPacking....")
        pack_dir = self.pack_dir + '/'
        pack_dir = pack_dir.replace('\\', '/')
        reads = [n for n in nuke.allNodes(recurseGroups=True) if n.Class() == 'Read']
        
        if not reads:
            nuke.message("No Read nodes found in the script!")
            return
        
        try:
            # 1. 모든 Read 노드의 파일 복사 (ThreadPool 사용)
            prog_incr = 90.0 / len(reads)
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []  # 모든 future 객체를 추적
                
                for i, n in enumerate(reads):
                    if self.task.isCancelled():
                        executor.shutdown(wait=False)
                        nuke.executeInMainThread(nuke.message, args=('cancel',))
                        return
                    
                    self.task.setProgress(int(i * prog_incr))
                    file_ = n['file'].getValue()
                    
                    if not file_:
                        print(f"경고: 빈 파일 경로 - {n.name()}")
                        continue
                    
                    # 경로 정규화
                    if file_.startswith('//'):
                        file_ = '//' + file_[2:]
                    file_ = file_.replace('\\', '/')
                    
                    self.task.setMessage(f"Copy {n.fullName()} files..")
                    
                    if not os.path.isabs(file_):
                        source_dir = self.source_dir.replace('\\', '/')
                        file_ = os.path.abspath(os.path.join(source_dir, file_)).replace('\\', '/')

                    # Future 객체 저장
                    if self.check_format(file_):
                        future = executor.submit(self._copy_single_file, file_, pack_dir, n)
                    else:
                        future = executor.submit(self._copy_sequence_files, file_, pack_dir, n)
                    futures.append(future)
                
                # 모든 작업 완료 대기
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        print(f"작업 실행 중 오류: {str(e)}")
            
            # 메인 스레드에서 실행해야 하는 작업들
            def finish_tasks():
                try:
                    # .nk 파일 저장
                    original_script = nuke.Root().name()
                    script_name = os.path.basename(original_script)
                    base_name = os.path.splitext(script_name)[0]
                    packed_script = os.path.join(self.source_dir, f"{base_name}_pack.nk").replace('\\', '/')
                    
                    nuke.scriptSaveAs(packed_script)
                    print(f"Nuke 스크립트 저장됨: {packed_script}")

                    # ZIP 파일 생성
                    self.to_zip(packed_script)
                    
                    nuke.message("패키징이 완료되었습니다!")
                except Exception as e:
                    nuke.message(f"완료 작업 중 오류 발생: {str(e)}")

            # 메인 스레드에서 실행
            nuke.executeInMainThread(finish_tasks)
            
        except Exception as e:
            def show_error():
                nuke.message(f"오류 발생: {str(e)}")
            nuke.executeInMainThread(show_error)
        finally:
            # 진행 표시줄 정리
            def cleanup():
                if hasattr(self, 'task'):
                    self.task.setProgress(100)
                    self.task = None
            nuke.executeInMainThread(cleanup)

    def _copy_single_file(self, file_, pack_dir, n):
        file_ = file_.replace('\\', '/')
        pack_dir = pack_dir.replace('\\', '/')
        print(f"\n[작업 시작] 단일 파일 복사")
        
        m = re.compile(r'(?P<root_dir>(//?[^/]+/[^/]+/|[A-Za-z]:/))')
        match_ = m.match(file_)
        if match_:
            old_file = file_
            file_name = os.path.basename(file_)
            new_file = os.path.join(pack_dir, file_name).replace('\\', '/')
            new_dir = os.path.dirname(new_file)
            
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            
            try:
                shutil.copy2(old_file, new_dir)
                print(f"[성공] 파일 복사 완료: {old_file} -> {new_dir}")
                # 노드 경로 업데이트는 메인 스레드에서 실행
                def update_node():
                    # 네트워크 경로 처리
                    if new_dir.startswith('//'):
                        # 네트워크 경로의 시작 // 보존
                        clean_dir = '//' + new_dir.lstrip('/').rstrip('/')
                    else:
                        clean_dir = new_dir.rstrip('/')
                    clean_path = f"{clean_dir}/{file_name}"
                    n['file'].setValue(clean_path)
                    print(f"노드 경로 업데이트: {clean_path}")
                nuke.executeInMainThread(update_node)
            except Exception as e:
                print(f"[오류] 파일 복사 실패: {e}")
                raise
        else:
            raise ValueError("Invalid file path format")

    def _copy_sequence_files(self, file_, pack_dir, n):
        file_ = file_.replace('\\', '/')
        pack_dir = pack_dir.replace('\\', '/')
        print(f"\n[작업 시작] 시퀀스 파일 복사")
        
        dir_ = os.path.dirname(file_)
        base_name = os.path.basename(file_)
        new_dir = pack_dir
        
        for f in os.listdir(dir_):
            seq_file_ = os.path.join(dir_, f).replace('\\', '/')
            
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            
            try:
                shutil.copy2(seq_file_, new_dir)
                print(f"[성공] 파일 복사 완료: {seq_file_} -> {new_dir}")
            except Exception as e:
                print(f"[오류] 파일 복사 실패: {e}")
                continue
        
        # 노드 경로 업데이트는 메인 스레드에서 실행
        def update_node():
            # 네트워크 경로 처리
            if new_dir.startswith('//'):
                # 네트워크 경로의 시작 // 보존
                clean_dir = '//' + new_dir.lstrip('/').rstrip('/')
            else:
                clean_dir = new_dir.rstrip('/')
            clean_path = f"{clean_dir}/{base_name}"
            n['file'].setValue(clean_path)
            print(f"노드 경로 업데이트: {clean_path}")
        nuke.executeInMainThread(update_node)

    def run_to_pack(self):
        # 별도의 스레드에서 실행
        threading.Thread(None, self.convert).start()


def run():
    r = NukeToPack()
    r.run_to_pack()  # 스레드로 실행
