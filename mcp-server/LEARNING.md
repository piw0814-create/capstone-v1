# MCP Server — 노션 가이드 순서

TO-DO를 포함한 MCP 기능 6개를 작성하고 검증했습니다. 코드는 첨부한 노션 예제와 교수님 a10 참고본을 따릅니다.

| 순서 | 배울 핵심 | Inspector에서 확인 |
| --- | --- | --- |
| 서버 초기화 | FastMCP 이름을 정하고 data 경로를 지정 | Connect → Connected, ict-operations-support |
| 5. 모니터링 Tool | SystemStatus로 결과 형식을 정하고 함수를 공개 | Tools → List Tools → get_monitoring_status → auth-service → Run Tool |
| 2. Runbook Resource | URI의 incident_type으로 지정 문서를 읽기 | Resources → List Templates → get_incident_runbook → auth-failure → Read Resource |
| 6. 진단 Prompt | 시스템명·증상을 넣어 표준 지시문 생성 | Prompts → List Prompts → incident_analysis_prompt → auth-service / 로그인 실패 급증 → Get Prompt |

## 결과 확인

- 모니터링: status=degraded, CPU 78.4, 메모리 71.2, 알림 2건. 결과가 Output Schema와 일치하는지 확인합니다.
- 없는 시스템: status=unknown, CPU·메모리는 노션 예제대로 0.0, 알림에 시스템을 찾지 못했다는 안내.
- Runbook: 해당 Markdown 본문. 없는 incident_type은 Runbook Not Found 안내.
- Resource는 URI 템플릿이므로 List Resources가 비어 있어도 List Templates에서 확인할 수 있습니다.
- Prompt: 현재 상태 확인 → Runbook 참조 → 관련 ticket 확인 → 종합 분석 → 생성 여부 확인 순서의 지시문.
- Get Prompt는 지시문을 반환합니다. 실제 진단이나 Jira 작업을 실행하지 않습니다.

## 코드 읽을 때 확인

- `@mcp.tool()` / `@mcp.resource(...)` / `@mcp.prompt()`가 각각 어떤 기능을 공개하는지 봅니다.
- `SystemStatus`의 필드명·타입·설명이 Inspector의 결과 형식으로 연결됩니다.
- runbook 주소의 `{incident_type}`이 함수 인자와 파일명으로 연결됩니다.
- Prompt의 f-string에 system_name과 symptom이 삽입됩니다.
- `mcp.run()`으로 실행하고 Inspector가 stdio 연결을 만듭니다.

실습 모니터링 값은 monitoring.json에 저장된 mock 데이터입니다.
`last_checked`는 조회 시각이며 실제 운영 지표의 측정 시각은 아닙니다.

## TO-DO 완료 내역

1. ManualSnippet, JiraTicket, JiraTicketCreated 모델 3개 작성 — 완료.
2. 운영 매뉴얼 검색 Tool 작성 — 완료.
3. Jira ticket 검색 Tool 작성 — 완료.
4. Jira ticket 생성 Tool 작성 — 완료.
5. Inspector의 A~F 항목 검증 및 캡처 — 완료.

`JiraTicket.assignee`의 `Optional[str]`은 `str | None`과 같은 뜻이며, 담당자가 없을 수 있습니다.
`ManualSnippet.score` 설명은 참고본과 동일합니다. mock 검색에서는 키워드 등장 횟수를 점수로 사용합니다.
현재 검증 기록은 verification/에 저장합니다.

| 기능 | 핵심 | 검증 결과 |
| --- | --- | --- |
| 매뉴얼 검색 | 검색어를 공백으로 분리하고 문서 내 등장 횟수로 정렬, top_k는 최대 개수 | 로그인 실패 → auth-failure 5점, db-down 2점. 결과 없음은 빈 목록 |
| Jira 검색 | 환경변수 3개가 모두 있으면 API, 아니면 mock. 결과를 JiraTicket 목록으로 반환 | OPS-101 / OPS-87 두 건, 두 번째 담당자는 None |
| Jira 생성 | Literal로 유형·우선순위 제한, 결과 번호·URL 반환. mock과 실제 등록 구분 | OPS-9999 / To Do. 실제 등록 없이 검증 |

워크시트는 기존 양식의 모델명·반환 필드와 공개 후 비교를 최종 코드에 맞춰 정리했습니다.
제출 ZIP은 Downloads의 ai-capstone-mcp-울산캠퍼스4반-박인우.zip입니다.
