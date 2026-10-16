# S1: Backend SSE 실습

기준은 사용자가 첨부한 노션 S1 코드입니다. Schema → Formatter → Converter → Endpoint 순서대로 작성했습니다.

| 파일 | 역할 | 확인할 핵심 |
| --- | --- | --- |
| backend/schemas/stream.py | 이벤트 4종의 양식 | token·tool_call_start·tool_call_end·done |
| backend/streaming/sse_formatter.py | SSE 포장 | event 줄·JSON data 줄·빈 줄 |
| backend/streaming/event_converter.py | messages·updates 변환 | 도구 결과는 앞 200자, 마지막은 done |
| backend/main.py | /chat/stream 연결 | astream·StreamingResponse·text/event-stream |

기존 Agent·MCP Client·Chat Schema·MCP Server와 기존 /chat·/health 함수는 유지했습니다. 이번 S1의 클라이언트는 curl입니다.

## 1. Schema와 Formatter 확인

프로젝트 루트에서 노션 Schema 예시를 확인합니다.

    uv run python -c "from backend.schemas.stream import TokenEvent; print(TokenEvent(content='Hello').model_dump_json())"
    uv run python -c 'from backend.schemas.stream import ToolCallStartEvent; print(ToolCallStartEvent(tool_name="search_manual", args={"query":"DB"}).model_dump_json())'

Formatter 예시의 schemas·streaming import는 backend 폴더 기준입니다.

    cd /Users/inwoopark/workspace/ai-service/capstone-v1/backend
    uv run python -c 'from schemas.stream import TokenEvent; from streaming.sse_formatter import format_sse; print(format_sse(TokenEvent(content="안녕")))'

## 노션 임시 테스트 코드

이후 사용자가 펼쳐서 보내준 본문 그대로 backend/scripts/test_stream.py를 추가했습니다. 질문은 “운영 매뉴얼 검색해 주세요”, thread_id는 test-001입니다.

backend 폴더에서 아래 명령으로 실행합니다.

    cd /Users/inwoopark/workspace/ai-service/capstone-v1/backend
    uv run python -m scripts.test_stream

이번 실제 실행은 token 39개와 마지막 done(thread_id=test-001)을 출력하고 정상 종료했습니다. 응답은 검색할 주제나 검색어를 되묻는 내용으로, 도구 호출은 없었습니다. 이는 노션 Desired Output처럼 token과 done을 확인한 결과이며, 도구 호출 검증과 구분합니다.

이 테스트는 웹 서버를 거치지 않고 별도 Agent를 생성하여 이벤트 변환까지 확인합니다. 출력은 verification/streaming/notion-temp-test.jsonl, stderr는 notion-temp-test.stderr.log에 보관했습니다.

## 2. 서버 실행

    cd /Users/inwoopark/workspace/ai-service/capstone-v1/backend
    uv run uvicorn main:app --reload --port 8000

이미 실행 중이면 중복으로 서버를 켜지 않습니다. reload가 코드 변경을 반영합니다. 서버 재시작 시 메모리의 대화 기록은 초기화됩니다.

## 3. 노션 기본 Stream 검증

다른 터미널에서 실행합니다.

    curl -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d '{"message":"데이터베이스 다운 시 대응 절차를 알려주세요."}'

확인할 순서는 tool_call_start → tool_call_end → 여러 token → done입니다. 이벤트 사이에 빈 줄이 있어야 합니다. done의 thread_id를 후속 요청에 사용합니다.

이번 실제 실행은 매뉴얼 검색 도구 시작·종료, token 182개, done을 확인했습니다. 총 약 3.55초였으며 토큰도 시간차를 두고 도착했습니다. 수량과 시간은 요청마다 달라질 수 있습니다.

## 4. 같은 Thread로 후속 질문

아래 자리표시자를 방금 받은 thread_id로 바꿉니다.

    curl -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d '{"message":"방금 그 절차에서 첫 단계만 자세히 설명해 주세요.","thread_id":"방금 받은 thread_id"}'

실제 검증에서는 같은 ID로 DB 다운 절차의 첫 단계인 “증상 인식”을 설명했습니다. 도구를 다시 사용할 필요가 없으면 token·done만 올 수도 있습니다.

## 5. 노션의 의도된 한계 확인

빈 메시지:

    curl -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d '{"message":""}'

실제 결과는 HTTP 200, 인사 응답 token, done이었습니다. 노션처럼 입력 검증·별도 스트림 오류 처리는 추가하지 않았습니다. 이 결과로 스트림 중 오류 처리까지 검증한 것은 아닙니다.

중단:

    curl -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d '{"message":"운영 매뉴얼을 모두 검색하고 상세히 분석해 주세요."}'

노션은 스트림 시작 1~2초 후 curl 터미널에서 Ctrl+C를 누르고 Backend 로그를 확인하도록 합니다. 최초 자동 실행은 약 1.2초에 done까지 완료되어 중단을 재현하지 못했습니다. 질문을 바꾸거나 인위적으로 지연을 넣지 않았습니다.

이후 사용자가 보낸 LangSmith 실행 화면에서 원문 질문의 CancelledError(Cancelled via cancel scope)와 No outputs를 확인했습니다. 따라서 해당 요청의 Agent 실행으로 취소가 전파된 사실은 관찰했습니다. 화면에 실제 도구 실행 노드는 없어 진행 중 MCP 도구의 취소 여부는 확인하지 못했고, 외부 LLM 서버 작업의 완전 종료까지 이 화면으로 단정할 수는 없습니다. 원본 캡처는 verification/streaming/captures/disconnect-langsmith.png에 보관했습니다.

## 원문 유지와 확인 범위

- Converter의 인자 처리식은 원문 그대로입니다. 일부 도구 인자 조각의 문자열 타입과 Schema의 dict 타입이 다를 가능성은 사전에 알렸습니다. 실제 기본 요청에서는 시작 인자가 빈 문자열에서 빈 dict가 되어 오류 없이 통과했습니다. 임의 변환 코드는 추가하지 않았습니다.
- 첫 캡처에서는 임시 테스트 본문이 접혀 있어 작성하지 않았고, 이후 사용자가 보내준 전체 본문으로 파일을 추가·실행했습니다.
- 사용자가 제공한 LangSmith 중단 trace 화면을 확인했습니다. LangSmith 계정에 직접 접속하여 전체 로그를 조회한 것은 아닙니다.
- Frontend와 CORS는 S2 구현 자료를 확인한 뒤 진행할 범위입니다.

실제 SSE 응답·수신 시간·검증 요약은 verification/streaming/에 보관했습니다. summary.json에서 완료와 미확인 항목을 구분합니다.

공식 참고: [OpenAI Streaming API responses](https://developers.openai.com/api/docs/guides/streaming-responses).
