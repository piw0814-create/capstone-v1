# AI Agent Capstone

첨부한 교수님 노션의 Project Structure v1과 MCP Server 가이드를 기준으로 구성합니다.
**MCP Server의 Tool 4개, Resource 1개, Prompt 1개와 결과 모델 4개**를 작성하고 A~F 검증을 완료했습니다.
FastAPI 단계의 핵심 4개 파일을 첨부 노션과 교수님 a11 참고본대로 작성했고, 이후 첨부 노션 S1의 SSE 스트리밍 코드를 추가했습니다.

## 프로젝트 구조

```text
capstone-v1/
├── .env
├── pyproject.toml
├── uv.lock
├── mcp-server/
│   ├── server.py
│   └── data/
│       ├── monitoring.json
│       └── runbooks/
├── backend/
│   ├── main.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── mcp_client.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── stream.py
│   └── streaming/
│       ├── __init__.py
│       ├── sse_formatter.py
│       └── event_converter.py
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
└── docker-compose.yml
```

`backend`를 실습 사전 조건대로 비운 후 Step 1~4 코드를 작성했습니다. 기존 자리표시자는 별도 백업했습니다.
frontend의 `.gitkeep`에는 실행 코드가 없습니다.
`docker-compose.yml`은 교수님 GitHub 참고본의 PostgreSQL 설정입니다. 아직 실행하지 않았습니다.
Part C의 config.py·supervisor/v1·v2 구조는 선택 리팩터링 단계에서 추가합니다.

FastAPI 단계의 환경 준비와 a10 비교 결과: [세팅 확인](SETUP.md)
FastAPI 코드별 역할과 직접 확인하는 방법: [Backend 학습 안내](FASTAPI-LEARNING.md)
S1 스트리밍 구현과 원문 검증 결과: [SSE 학습 안내](STREAMING-LEARNING.md)

## 현재 MCP 단계

노션에 제공된 코드의 타입·기본 반환값·프롬프트 문구를 따릅니다.

- Tool: `get_monitoring_status`, 결과 모델 `SystemStatus`
- Resource: `get_incident_runbook`
- Prompt: `incident_analysis_prompt`

TO-DO 결과 모델 `ManualSnippet`, `JiraTicket`, `JiraTicketCreated`는 교수님 a10 참고본대로 작성했습니다.
매뉴얼 검색·Jira 검색·Jira 생성 함수도 노션 제공 코드와 a10 참고본을 기준으로 작성했습니다.
Jira 검색의 실제 API 경로는 첨부한 노션의 수정 코드대로 `/rest/api/3/search/jql`입니다.
이번 검증은 JIRA_BASE_URL·JIRA_EMAIL·JIRA_API_TOKEN 미설정에 따른 mock 모드로 진행했습니다.
사용자가 받은 data 파일은 그대로 사용합니다.

## 실행

```sh
cd /Users/inwoopark/workspace/ai-service/capstone-v1
uv sync --locked
npx @modelcontextprotocol/inspector@v1-latest uv run python mcp-server/server.py
```

교수님이 수정 안내한 `v1-latest` 명령과 `mcp-server` 경로를 사용합니다.
Inspector에서 Connect를 누르고, 코드 변경 후에는 Restart로 새 코드를 반영합니다.
Python 환경은 기존 langgraph-v1의 설정을 재사용하며 프로젝트 이름은 capstone-v1입니다.
FastMCP는 현재 설치된 2.13.0으로 예제를 실행합니다. 교수님 화면의 서버 버전과 동일하다는 뜻은 아닙니다.

단계별 핵심과 확인 방법: [MCP 학습 안내](mcp-server/LEARNING.md)

## 제출물

- ZIP: `/Users/inwoopark/Downloads/ai-capstone-mcp-울산캠퍼스4반-박인우.zip`
- 폴더: `/Users/inwoopark/Downloads/ai-capstone-mcp-울산캠퍼스4반-박인우/`
- 구성: 최종 워크시트 Word 1개와 Inspector 캡처 A.png~F.png 6개
- 검증 기록: `mcp-server/verification/submission-check.json`

| 캡처 | 기능 | 검증 결과 |
| --- | --- | --- |
| A | 모니터링 조회 | auth-service, degraded, 알림 2건 |
| B | 매뉴얼 검색 | 로그인 실패, top_k=3, auth-failure 최상위 |
| C | Runbook 읽기 | auth-failure Markdown 본문 |
| D | Jira 검색 | auth-service mock 티켓 2건 |
| E | Jira 생성 | OPS-9999 mock 응답 |
| F | 진단 Prompt | auth-service / 로그인 실패 급증, 표준 진단 절차 |

제출 ZIP에는 워크시트와 캡처만 포함합니다. 실제 Jira 티켓 생성과 Slack 업로드는 수행하지 않았습니다.

## 참고

- [교수님 참고 저장소](https://github.com/elizabeth-kj-bae/capstone-v1)
- [MCP Server 단계 완성 참고본](https://github.com/elizabeth-kj-bae/capstone-v1/tree/a10-mcp-server)

참고 저장소는 단계별 완성본입니다. 이후 단계의 코드를 현재 실습에 미리 복사하지 않습니다.
