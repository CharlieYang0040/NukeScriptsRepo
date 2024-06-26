# SimpleShuffle

## 개요

SimpleShuffle 플러그인은 Nuke 사용자가 합성 작업에서 다양한 채널 패스를 분류하고 셔플링하는 과정을 도와줍니다. 이 도구는 채널을 자동으로 분류하여 메인 패스, 엑스트라 패스, AOV 패스, 라이트 패스 및 기타 패스로 나누어 관리하는 작업을 단순화합니다.

![image](https://github.com/CharlieYang0040/NukeScriptsRepo/assets/129147417/f72a6160-aa39-45df-9799-fd46d981a342)


## 주요 기능

- **채널 분류**: 채널을 메인 패스, 엑스트라 패스, AOV 패스, 라이트 패스 및 기타 패스로 자동 분류합니다.
- **사용자 지정 패스 이름**: 사용자가 필요에 따라 미리 정의된 패스 이름을 쉽게 수정할 수 있습니다.
- **채널 관리**: 노드 내에서 채널을 관리하고 셔플링하는 과정을 단순화하여 작업 효율성을 높입니다.

## 설치 방법

### 간편 설치

1. GitHub 릴리즈 페이지에서 `SimpleShuffle_Install.exe` 파일을 [다운로드](https://github.com/CharlieYang0040/NukeScriptsRepo/releases)합니다. 
2. 다운로드한 파일을 실행하여 설치를 완료합니다.

### 또는 매뉴얼 설치

1. GitHub 리포지토리 [NukeScriptsRepo](https://github.com/CharlieYang0040/NukeScriptsRepo)에서 `LayerSimpleShuffle` 폴더를 다운로드합니다.
2. 다운로드한 폴더를 Nuke 플러그인 디렉토리에 위치시킵니다. (C:\Users\사용자이름\.nuke)
3. `init.py` 파일에 다음 줄을 추가하여 시작 시 플러그인이 로드되도록 합니다:
    ```python
    nuke.pluginAddPath('./LayerSimpleShuffle')
    ```

## 사용 방법

1. Nuke에서 멀티 채널 파일을 불러옵니다. Read 노드를 선택합니다.
2. 단축키 Ctrl + R 을 누르거나 메뉴에서 `LayerSimpleShuffle` 플러그인을 실행합니다.
3. 플러그인이 미리 정의된 카테고리별로 선택된 노드의 채널을 분류하고 표시합니다.

## 커스터마이징

`LayerSimpleShuffle.py` 스크립트의 관련 섹션을 편집하여 패스 이름을 사용자 지정할 수 있습니다. 메인 패스 이름, 엑스트라 패스 이름 및 기타 분류 항목을 자신의 합성 요구에 맞게 조정할 수 있습니다.

## 버전

v0.2.0 : 비상업용(Non-commercial) 버전 Nuke에서 "10 nodes python scripts limits"에 의해 작동이 안되는 문제를 수정하였습니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 기여

기능 향상을 위한 기여를 환영합니다. 버그나 기능 요청은 풀 리퀘스트를 제출하거나 이슈를 열어주세요.

## 문의

질문이나 지원이 필요하시면 Charlie Yang에게 yhc1401@gmail.com으로 연락해주세요.
