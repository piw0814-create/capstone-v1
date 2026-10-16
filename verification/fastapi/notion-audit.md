# 첨부 노션 기준 점검

2026-10-14. 기준은 사용자가 첨부한 강의자료 이미지와 교수님 저장소의 a10·a11 태그입니다. 현재 노션 원문 전체를 새로 조회한 결과는 아닙니다.

## 일치한 항목

| 항목 | 근거 | 결과 |
| --- | --- | --- |
| Required: 기존 MCP 검증 | A~F 검증 기록 및 사용자 Inspector 확인 | 완료 |
| Required: a10 worktree 비교 | `_ref/a10-mcp-server`, b8305cf 태그 checkout 및 비교 기록 | 완료 |
| Required: 구현 전 빈 backend | 기존 자리표시자 백업 후 빈 폴더 점검 기록 | 완료 |
| Step 1: Schema | `schemas/chat.py`가 a11과 바이트 단위 일치 | 완료 |
| Step 2: MCP Client | `agent/mcp_client.py`가 a11과 바이트 단위 일치, stdio Tool 로드 | 완료 |
| Step 3: Agent | `agent/graph.py`가 a11과 바이트 단위 일치, gpt-4o·MemorySaver·create_agent | 완료 |
| Step 4: Endpoint | `main.py`가 a11과 바이트 단위 일치, lifespan·/health·/chat·thread_id·tool_calls | 완료 |
| T1·T2·T3 | 실제 도구 호출, T2→T3 같은 thread_id 및 auth-service Jira 검색 | 완료 |
| E2 | 없는 시스템 조회 및 안내 응답 | 완료 |
| E1 오류 전달 | Backend 소유 MCP 종료 후 실제 HTTP 500, 사용자 PID 91245 실행 기록 | 완료, 방법 차이는 아래 참고 |
| ZIP 구성 | T1.png·T2.png·T3.png·E1.png·E2.png 5개, 사용자 첨부 원본과 일치, 압축 무결성 확인 | 완료 |

## 차이와 남은 범위

1. **폴더 그림 전체와는 아직 불일치:** `backend/config.py`와 `backend/requirements.txt`가 없습니다. 첨부한 캡처에 두 파일의 본문 코드는 없고, 교수님 a11 참고본에도 두 파일이 없습니다. 현재 환경변수는 실행 환경에서 전달하고 의존성은 루트 `pyproject.toml`·`uv.lock`에서 관리하므로 기능 실행은 성공했습니다. 그림의 파일 목록까지 맞추려면 두 파일은 추가로 정리해야 합니다.
2. **E1 명령·질문·중단 시점 조정:** 노션은 먼저 `pkill`로 MCP를 종료한 후 “운영 매뉴얼 검색해 주세요.”를 요청합니다. 설치된 어댑터는 도구 호출마다 새 stdio 프로세스를 만들고, 원래 질문에서는 AI가 검색 주제를 되물었습니다. 따라서 DB 다운 대응으로 질문을 구체화하고 도구 호출 중 이 Backend 소유 MCP만 종료했습니다. 오류 전달 목적은 검증했지만 강의 명령 그대로 실행한 캡처는 아닙니다.
3. **실제 Vector DB는 아직 미구현:** 검색은 앞선 MCP 실습의 mock 키워드 검색입니다. Vector DB에 직접 연결된 상태라고 표현할 수 없습니다. Agent→MCP 검색 Tool 경로는 연결됐습니다.
4. **제출 파일 준비와 업로드는 별개:** ZIP은 검증했으며 Slack 업로드 여부는 이 점검에서 확인하지 않았습니다.

## 현재 제출 ZIP

`/Users/inwoopark/Downloads/ai-capstone-fastapi-울산4반-박인우.zip`

기존 안내 이름의 ZIP은 현재 이 이름으로 바뀌어 있습니다. 현재 파일을 실제로 열어 항목 수와 각 원본 캡처를 대조했습니다. E1 방식이 조정된 사실은 위와 같이 명시해야 합니다.

판정: **FastAPI 핵심 구현과 기능·오류 검증은 완료. 폴더 그림까지 완전히 일치한 상태는 아니며, E1 검증 방법에도 차이가 있음.**

## 최신 제출 캡처 교체

이후 사용자가 노션 순서의 `pkill` → 원문 질문으로 E1을 직접 실행했습니다. HTTP 200과 검색 주제를 되묻는 응답, `tool_calls: []`를 확인했습니다. 원문 순서는 수행했지만 해당 요청에서 MCP 오류는 재현되지 않았습니다.

사용자 요청에 따라 제출 ZIP의 E1.png를 이 원문 실행 캡처로 교체했고, E2.png도 최신 curl 실행 캡처로 교체했습니다. T1~T3는 기존 ZIP의 바이트를 그대로 유지했습니다. 이전 HTTP 500 캡처를 포함한 ZIP은 백업에 보관했습니다. 현재 제출물의 구성과 백업 위치는 `submission-latest.json`에 기록했습니다.
