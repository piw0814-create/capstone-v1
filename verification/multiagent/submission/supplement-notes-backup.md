# Multi-Agent Streaming 결과
- 울산 - 4반, 박인우

## 노션 원문 대비 보완 사항

노션의 설명에는 작업별 `pending → in_progress → completed` 상태와 하위 에이전트의 토큰 스트리밍을 화면에 표시하도록 되어 있으나, 제공 코드는 작업이 완료된 상태만 반환하여 `task_started` 이벤트와 하위 토큰이 발생하지 않았다. 설명된 UX를 구현하기 위해 다음을 보완했다.

1. **작업 시작 단계 분리**: Supervisor graph에 `start_task` 노드를 추가하여, 실제 작업을 실행하기 전에 `in_progress` 상태가 별도 업데이트로 반환되도록 했다. 이벤트 변환기가 이 업데이트에서 `task_started`를 보내고 작업 카드가 노란색으로 바뀐다.
2. **하위 토큰 전달 연결**: 하위 에이전트를 `astream`으로 실행해 실제 생성 토큰을 읽고, `get_stream_writer()`로 작업 ID를 포함한 custom 이벤트를 상위 그래프에 전달했다. Supervisor endpoint는 `updates`와 `custom`을 수신하여 기존 SSE `sub_agent_token` 형식으로 변환한다.
3. **토큰 귀속 검증**: 현재 진행 중인 작업과 ID가 일치하는 생성 토큰만 보내고, 작업 완료 시 활성 ID를 해제한다. 계획 생성 텍스트와 원시 도구 응답이 작업 토큰으로 노출되지 않게 했다.

작업은 기존대로 순차 실행하고, Research/Writing의 역할·모델·MCP 도구는 유지했다. 최종 답변 전체를 `token` 이벤트 한 번으로 보내는 원문의 간단화도 유지했다.

## 보완 후 실제 검증

입력: "운영 매뉴얼과 최근 incident를 종합해 장애 대응 가이드를 만들어 주세요."

- HTTP 응답: 200
- `plan_created`: 1회
- `task_list_created`: 1회
- `task_started`: 3회
- `sub_agent_token`: 712회 (task_1 53회, task_2 218회, task_3 441회)
- `task_completed`: 3회
- 최종 `token`: 1회
- `done`: 1회
- 소요 시간: 약 10.09초
- `done`의 thread_id가 요청 ID와 일치: Y

각 작업의 시작 → 해당 ID의 토큰 → 완료 순서를 검증했다. 마지막 Writing 작업의 토큰을 이어 붙인 문자열은 최종 답변과 정확히 일치하여 중복 반영이 없음을 확인했다.

실제 Chrome 화면에서도 노란 진행 카드 안에 생성 텍스트가 점진적으로 나타난 뒤 녹색 완료 카드로 바뀌고 최종 답변이 표시되는 것을 확인했다. 캡처와 DOM 관찰 기록은 `progress-fix/captures/`에 보관했다.

## 회귀 검사

작업 토큰의 ID 귀속, 완료 후 늦게 도착한 토큰 제외, 다른 작업의 토큰 제외, 계획 토큰·원시 도구 응답 제외, 최종 답변 1회 전송을 자동 검사했다. 실제 SSE 순서와 Writing 토큰/최종 답변 일치 검사도 통과했다.
