# FastAPI + Agent + MCP 실습

첨부한 교수님 노션의 Step 1~4를 구현했습니다. 핵심 4개 파일과 `__init__.py` 2개는 교수님 `a11-fastapi` 참고본과 동일합니다.

## 파일별로 배우는 내용

| 순서 | 파일 | 핵심 | 확인 방법 |
| --- | --- | --- | --- |
| 1 | `backend/schemas/chat.py` | Pydantic으로 요청·응답 양식을 정의합니다. `thread_id`는 선택 입력이고 `tool_calls`의 기본값은 빈 목록입니다. | `/docs`에서 ChatRequest·ChatResponse 양식을 확인합니다. |
| 2 | `backend/agent/mcp_client.py` | MCP Server를 subprocess로 실행하고 stdio로 연결합니다. `get_tools()`는 MCP Tool을 LangChain Tool로 변환합니다. | Agent가 기존 MCP Tool 4개를 사용할 수 있는지 확인합니다. |
| 3 | `backend/agent/graph.py` | `gpt-4o`, MCP Tool, MemorySaver를 `create_agent()`로 묶습니다. | T1·T2에서 질문에 맞는 도구를 선택하는지 확인합니다. |
| 4 | `backend/main.py` | lifespan에서 Agent를 한 번 만들고, 요청을 Agent에 전달한 뒤 응답을 반환합니다. | `/health`, `/chat`을 호출하고 T3에서 이전 대화를 기억하는지 확인합니다. |

요청 경로는 사용자 → FastAPI → Agent → MCP Tool → Agent 응답입니다. MCP Server의 Resource와 Prompt는 이번 `get_tools()` 연결에 자동으로 포함되지 않습니다. 실제 Vector DB 대신 이전 MCP 실습의 mock 매뉴얼 검색을 사용합니다.

## 직접 실행

터미널 1:

```sh
cd /Users/inwoopark/workspace/ai-service/capstone-v1/backend
uv run uvicorn main:app --reload --port 8000
```

이미 8000에서 서버가 실행 중이면 같은 서버를 사용합니다. 새 터미널에서도 `OPENAI_API_KEY`가 실행 환경에 설정돼 있어야 합니다. 교수님 제공 핵심 코드는 `.env`를 직접 읽는 코드를 포함하지 않습니다. 의존성은 기존 프로젝트의 `pyproject.toml`·`uv.lock`으로 관리합니다.

터미널 2:

```sh
curl http://localhost:8000/health

curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"데이터베이스 다운 시 대응 절차를 알려주세요."}'

curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"auth-service 시스템 상태가 어떤가요?"}'
```

T3에서는 바로 위 T2 응답의 `thread_id`를 아래 자리표시자에 넣습니다.

```sh
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"방금 그 시스템에 대한 ticket을 검색해 주세요.","thread_id":"여기에 T2 응답의 thread_id"}'
```

브라우저에서 `http://localhost:8000/docs`를 열고 POST /chat → Try it out → 요청 입력 → Execute로도 확인할 수 있습니다.

## 결과를 읽는 방법

- `message`: 도구 결과를 참고하여 AI가 작성한 답변입니다. 검색은 문서의 일부만 반환하므로 답변이 전체 runbook 절차를 담는다는 뜻은 아닙니다.
- `thread_id`: 같은 값을 보내면 대화를 이어갑니다. 서버가 재시작되면 MemorySaver의 기록은 사라집니다.
- `tool_calls`: 교수님 코드는 해당 대화의 전체 기록에서 도구 호출을 수집합니다. T3 응답에는 T2의 모니터링 호출과 T3의 Jira 호출이 함께 나타납니다.

실제 테스트 요청과 응답은 `verification/fastapi/`에 보관합니다. 이 JSON 기록은 교수님이 요구한 제출용 캡처 이미지와는 별도 자료입니다.

## 검증 결과와 E1 차이

T1은 매뉴얼 검색, T2는 auth-service 모니터링 조회, T3은 같은 thread_id의 auth-service Jira 검색에 성공했습니다. E2는 없는 시스템을 조회한 뒤 상태 정보를 제공할 수 없다고 안내했습니다.

현재 langchain-mcp-adapters 0.1.14의 `get_tools()`는 도구 호출마다 새 세션과 stdio 프로세스를 만듭니다. Agent는 lifespan에서 한 번 만들지만 MCP 프로세스가 계속 유지되는 것은 아닙니다. 호출 전에 종료한 MCP는 다음 호출에서 다시 실행될 수 있습니다.

E1의 원래 문구인 “운영 매뉴얼 검색해 주세요.”만 보냈을 때는 AI가 검색 주제를 되물었고 도구를 호출하지 않았습니다. 따라서 검색 주제를 DB 다운 대응으로 명확히 한 후, 도구 호출 중 Backend 소유 MCP 프로세스만 종료했습니다. 이때 `/chat`은 HTTP 500을 반환했습니다. 두 실행의 기록을 모두 저장했습니다. Inspector까지 종료할 수 있는 광범위한 `pkill`은 사용하지 않았습니다.

직접 캡처할 때는 아래 검증 보조 명령으로 요청과 Backend 소유 MCP 종료를 함께 실행할 수 있습니다. 기능 코드를 수정하지 않으며, 이번 실행의 실제 결과를 날짜별 JSON으로 저장합니다. `--check`를 붙이면 연결 준비 상태만 확인합니다.

```sh
cd /Users/inwoopark/workspace/ai-service/capstone-v1
uv run python verification/fastapi/e1_check.py
```

화면에 요청 내용, 종료한 MCP PID, HTTP 500과 실제 오류 응답이 보이면 `E1.png`로 캡처합니다. MCP 종료가 재현되지 않으면 PASS로 기록하지 않습니다.

## 사용자 직접 검증 및 제출 파일

사용자가 직접 실행한 T1·T2·T3·E2와 E1 캡처를 모두 확인했습니다. E1은 사용자의 실제 실행에서도 MCP PID 91245 종료 후 HTTP 500을 반환했습니다. 해당 기록은 `manual-E1-20261014-141327-482132.json`입니다.

사용자가 채팅에 첨부한 캡처 원본 5개를 T1.png·T2.png·T3.png·E1.png·E2.png로 복사하여 아래 ZIP을 만들었습니다. 이미지 내용은 수정하지 않았으며, ZIP 항목 5개와 압축 무결성을 확인했습니다.

- ZIP: `/Users/inwoopark/Downloads/ai-capstone-fastapi-울산4반-박인우.zip`
- 캡처 폴더: `/Users/inwoopark/Downloads/ai-capstone-fastapi-울산캠퍼스4반-박인우/`

제출용 파일을 준비한 상태이며 Slack 업로드는 실행하지 않았습니다.

이후 사용자 요청으로 ZIP의 E1·E2를 최신 원문 curl 실행 캡처로 교체했습니다. 현재 E1.png는 `pkill` 후 원문 질문에 HTTP 200·`tool_calls: []`가 나온 실제 결과입니다. 기존 500 결과는 호출 중 종료 방식의 보완 검증 기록으로 남아 있습니다. T1~T3는 유지했으며 최신 파일 점검 기록은 `verification/fastapi/submission-latest.json`입니다.
