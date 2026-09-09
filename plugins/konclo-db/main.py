# -*- coding: utf-8 -*-
"""데스크톱 확장(.mcpb) 진입점.

manifest.json 의 server.entry_point 가 이 파일을 가리킨다.
konclo_db 패키지는 이 파일과 같은 폴더에 있으므로 그대로 import 된다.
Claude Code 플러그인 쪽은 konclo-db-server 콘솔 스크립트를 쓰므로 이 파일을 지나지 않는다.
"""
from konclo_db.server import main

if __name__ == "__main__":
    main()
