# AI Agent Capstone

ICT 운영 지원 Agent 실습 저장소. MCP Server, FastAPI, 단일 Agent SSE, Next.js 채팅 화면, Supervisor 기반 멀티에이전트까지 구현하고 검증했다. 사용자 제공 노션과 교재를 기준으로 학습 내용과 구현 차이를 기록한다.

## 학습 문서

| 문서 | 내용 |
| --- | --- |
| [수업 핵심 정리](COURSE-NOTES.md) | 핵심 개념, 주의점, 설계 질문, 실제 보완과 검증의 한계 |
| [후속 운영·Agent 확장](OPERATIONS-LEARNING.md) | 교재 후반의 관측·평가, 오류, 비용·시간, 영속 상태, Agent 확장 |
| [MCP 학습](mcp-server/LEARNING.md) | Tool·Resource·Prompt 및 Inspector 확인 |
| [환경 준비](SETUP.md) | 초기 환경과 참고본 비교 |
| [FastAPI 학습](FASTAPI-LEARNING.md) | API와 Agent 연결 |
| [S1 Streaming 학습](STREAMING-LEARNING.md) | S1 당시 SSE 구현·검증 기록 |
| [Multi-agent 학습](MULTIAGENT-LEARNING.md) | 실행 방법과 최신 검증 결과 연결 |

이전 단계 문서는 당시의 구현·측정 기록이다. 현재 상태와 후속 계획은 위의 핵심·후속 학습 문서를 함께 본다. 교재 원문 PDF와 비밀 환경 설정은 저장소에 포함하지 않는다.

## 현재 구조

```text
frontend/                 Next.js 채팅 화면, thread 관리, 자체 SSE 파싱
backend/main.py           FastAPI API, CORS, lifespan
backend/agent/            단일 Agent, Supervisor Graph, MCP Client
backend/schemas/          요청·응답·이벤트 모델
backend/streaming/        Graph 이벤트 변환과 SSE 직렬화
mcp-server/               Tool·Resource·Prompt 및 실습 데이터
verification/             단계별 관측 결과와 캡처
```

단일 Agent는 `/chat/stream`, Multi-Agent는 `/chat/supervisor/stream`을 사용한다. `/chat`은 최종 응답을 받는 일반 요청 API다. 프런트는 AI SDK 패키지를 설치했지만 현재 `useChat` 대신 자체 `fetch` 파서로 서비스 SSE를 처리한다.

Multi-agent는 계획 후 Research/Writing 작업을 순차 실행한다. 진행 카드와 하위 토큰 표시를 보완했으며 최종 답변은 한 번의 token 이벤트로 전송한다. 각 Graph의 상태는 MemorySaver에 있어 서버 재시작 후 사라진다. PostgreSQL 영속화·자동 재시도·Validator·동적 재계획은 후속 범위다.

## 실행

프로젝트 루트에서 Python 의존성을 준비하고 `.env`에 필요한 설정을 입력한다. 비밀 값은 커밋하지 않는다. 자세한 설정은 [환경 준비](SETUP.md)를 참고한다.

```sh
uv sync --locked
```

Backend 터미널:

```sh
cd backend
uv run --env-file ../.env uvicorn main:app --reload --port 8000
```

별도 Frontend 터미널에서 프로젝트 루트를 기준으로 실행:

```sh
cd frontend
npm ci
npm run dev
```

[채팅 화면](http://localhost:3000)에서 모드를 선택한다. 서버 상태는 [health](http://localhost:8000/health), API 문서는 [docs](http://localhost:8000/docs)에서 확인한다. CORS는 `http://localhost:3000`을 허용한다. 브라우저 주소창의 GET으로 POST 전용 스트림 API를 열면 405가 발생한다.

MCP를 별도로 점검할 때는 프로젝트 루트에서 실행한다.

```sh
npx @modelcontextprotocol/inspector@v1-latest uv run python mcp-server/server.py
```

Inspector에서 Connect 후 확인하고 코드 변경 시 Restart한다. `docker-compose.yml`의 PostgreSQL 설정은 현재 Graph의 저장소와 연결되지 않았다.

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
