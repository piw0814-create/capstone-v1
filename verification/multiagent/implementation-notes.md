# Multi-agent 노션 구현 기록

## 기준과 구현

사용자 제공 이미지 01.png~26.png를 기준으로 작성했다. 기존 단일 agent graph, /chat, /chat/stream은 유지하고 /chat/supervisor/stream을 추가했다.

- agent/supervisor_graph.py: planning → execute 반복 → finalize. Research는 기존 MCP 도구, Writing은 도구 없이 동일한 gpt-4o 모델을 사용한다.
- schemas/stream.py: 원문의 새 이벤트 6종을 추가했다.
- streaming/event_converter.py: convert_supervisor_events를 원문 로직대로 추가했다.
- main.py: lifespan에서 Supervisor graph를 생성하고 별도 endpoint를 연결했다.
- scripts/test_supervisor.py: 노션 임시 테스트를 추가했다.
- frontend: 타입·transport endpoint 인자 확장, PlanView·TaskListView 추가, ChatMessage·메인 페이지에 모드 선택 및 이벤트 처리를 연결했다.

## 기존 수정 유지와 연결에 필요한 보완

- 앞서 사용자 승인으로 수정한 React 상태의 불변 갱신과 assistant message ID별 갱신을 유지했다. 원문의 직접 수정 코드로 되돌리지 않았다.
- single-agent 모드의 toolCalls 타입·이벤트 처리·ToolCallView를 유지했다. 새 UISupervisorMessage는 기존 UIMessage를 확장한다.
- 작업 선택 상태는 메시지 updater 밖에서 갱신한다. 기존 오류 UI 처리도 유지했다.
- 이미지에서 생략한 새 import와 endpoint 인자를 연결했다. 새로운 패키지나 모델로 변경하지 않았다.

## 최초 노션 원문 구현 검증 (보완 전)

- Python 컴파일, TypeScript 검사, Next.js 프로덕션 빌드: 통과.
- 노션 임시 테스트: Research와 Writing 작업이 completed로 완료되고 최종 DB 대응 답변 생성.
- 실제 supervisor SSE: HTTP 200, plan_created 1, task_list_created 1, task_completed 3, token 1, done 1. 소요 약 10.52초. done의 thread_id가 요청 ID와 일치.
- Chrome: 단일 모드, 멀티 모드, 복합 질문, 인사 질문을 실제 실행. captures/observations.json에 관찰 DOM 기록.
- 기존 단일 모드에서 DB 다운 질문을 전송하여 search_operations_manual 완료 박스와 답변이 유지됨을 확인.
- React updater를 동결한 이전 상태로 반복 호출하는 회귀 검사 통과. 토큰·작업이 중복 반영되지 않음.

## 원문에서 확인된 한계와 현재 상태

1. 원문에서는 execute_task_node 내부에서만 in_progress를 만들고 완료 상태만 반환해 task_started가 발생하지 않았다. 사용자 승인 후 start_task 노드 분리로 보완했다.
2. 원문에서는 sub_agent_token도 발생하지 않았다. 사용자 승인 후 하위 agent.astream + get_stream_writer custom 전달로 보완하여 실제 노란 진행 카드와 토큰 표시를 확인했다.
3. finalize의 전체 최종 답변을 token 이벤트 1개로 전송한다. 최종 답변이 글자 단위로 누적되는 구현은 아니다.
4. SubAgentToolCallEvent는 스키마만 제공되어 있다. converter에서 이 이벤트를 생성하는 코드와 frontend 타입·처리는 원문에 없어 추가 구현하지 않았다.
5. 디렉터리 그림의 SubAgentView.tsx는 별도 코드가 없고 제공된 TaskListView가 하위 토큰을 표시한다. 사용되지 않는 파일을 임의로 만들지 않았다.
6. MemorySaver에 대화를 저장하지만 planning prompt는 마지막 사용자 메시지만 사용한다. 이전 대화를 계획에 반영하는 기능은 별도로 보장하지 않는다.
7. 계획 JSON을 정규식으로 파싱하며 빈 tasks, 알 수 없는 agent 등의 예외 처리는 원문대로 추가하지 않았다.

1~2번은 사용자가 명시적으로 보완을 승인하여 수정했다. 나머지는 원문의 범위대로 유지했다. 상세 변경과 보완 후 검증값은 results.md에 기록했다.

## 보완 후 검증 (2026-10-16)

- 실행 흐름: planning → start_task → execute → 다음 start_task 또는 finalize.
- Supervisor endpoint의 내부 LangGraph stream mode는 updates/custom으로 변경했다. 기존 단일 endpoint의 messages/updates와 외부 SSE 이벤트 이름·필드는 유지했다.
- 하위 LLM 생성 텍스트만 명시적 작업 ID로 전달하고, ToolMessage 원시 응답과 계획 토큰은 전달하지 않는다.
- 실제 SSE: task_started 3, sub_agent_token 712, task_completed 3. token 1, done 1 유지.
- 작업별 이벤트 순서와 마지막 Writing 토큰 전체가 최종 답변과 정확히 같음을 확인했다.
- backend/tests/test_supervisor_streaming.py: 토큰 귀속·작업 밖 토큰 차단·최종 응답 검사 통과.
- 보완 전 실제 SSE는 before-progress-fix/에 보관했고, 현재 sse-check.json은 보완 후 실제 실행이다.
- 보완된 화면과 관찰 기록은 progress-fix/captures/에 보관했다.
