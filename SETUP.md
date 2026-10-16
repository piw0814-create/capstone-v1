# FastAPI 실습 전 세팅 확인

확인 날짜: 2026-10-14. 제공된 노션의 Required 항목을 기준으로 구현 전에 점검한 기록입니다.

| 준비 항목 | 결과 |
| --- | --- |
| 이전 MCP 단계 검증 | Inspector A~F 확인 및 제출물 정리 완료 |
| a10 worktree 비교 | `_ref/a10-mcp-server`, 태그 `a10-mcp-server`, 커밋 `b8305cf375652f7d19ff579a64388ed008654eec` |
| backend 비어 있음 | 기존 자리표시자를 백업한 뒤 빈 폴더로 준비 |
| FastAPI | 0.143.0 설치 및 직접 의존성 등록 |
| Uvicorn | 기존 0.38.0 유지 및 직접 의존성 등록 |
| 기존 패키지 | 버전 변경·삭제 없음. FastAPI와 opentelemetry-api만 추가 |
| 환경 동기화 | `uv sync --locked --dry-run` 변경 없음 |
| 실행 포트 | 점검 시 8000 포트 사용 가능 |

## a10 비교 결과

- 결과 모델 4개와 mock 매뉴얼 검색·mock Jira 검색·Jira 생성 함수는 a10과 같은 코드입니다. 주석·공백 차이는 비교에서 제외했습니다.
- `monitoring.json`과 runbook Markdown 3개는 교수님 참고본과 일치합니다.
- Jira 검색의 실제 API 경로는 a10의 `/rest/api/3/search` 대신 첨부 노션 수정본의 `/rest/api/3/search/jql`을 유지합니다.
- 모니터링 함수는 첨부 노션대로 작성되어 있습니다. a10 참고본에는 데이터 파일이 없을 때의 추가 처리도 포함되어 있습니다.
- Resource와 Prompt는 첨부 노션 문구를 유지합니다. a10과 설명·인코딩 지정·Prompt 일부 문구가 다릅니다.
- a10의 선택적 Vector DB 검색 예시는 현재 코드에 추가하지 않았습니다. 현재 매뉴얼 검색은 노션 실습의 mock 키워드 검색입니다.

## 확인 범위

FastAPI 패키지의 임시 `/health` 응답, 에이전트 관련 라이브러리 import, MCP 클라이언트의 Tool 4개 로드를 확인했습니다. 임시 확인 코드는 backend 파일에 저장하지 않았습니다.

OPENAI_API_KEY가 `.env`와 현재 실행 환경에 있는 것까지 확인했습니다. 실제 API 인증·모델 접근·사용 가능 잔액은 아직 검증하지 않았습니다. 실제 LLM 호출은 다음 구현 단계에서 확인합니다.

이 사전 점검 당시에는 FastAPI 기능 코드를 작성하지 않았습니다. 이후 사용자 요청에 따라 `schemas/chat.py` → `agent/mcp_client.py` → `agent/graph.py` → `main.py`를 교수님 a11 참고본 그대로 작성했습니다. 현재 구현과 테스트 안내는 [Backend 학습 안내](FASTAPI-LEARNING.md)를 참고하세요.
실제 `gpt-4o` API 호출도 T1~T3·E2에서 성공하여 해당 실행 환경의 인증과 모델 접근을 확인했습니다.

## 백업

`/Users/inwoopark/.codex/backups/capstone-v1-before-fastapi-setup-20261014-134816/`

설치 전 `pyproject.toml`, `uv.lock`, `README.md`와 기존 backend 전체를 보관했습니다.
