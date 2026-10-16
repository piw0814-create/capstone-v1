다음 장애에 대해 표준 진단 절차를 수행하세요.

## 장애 정보
- 시스템: auth-service
- 증상: 로그인 실패 급증

## 진단 절차 (반드시 순서대로 수행)

1. **현재 상태 확인**: get_monitoring_status Tool로 auth-service의 현재 상태를 조회하세요.
2. **Runbook 참조**: 증상에 해당하는 runbook이 있는지 확인하세요.
   (예: 'api-latency', 'db-down', 'auth-failure')
3. **관련 ticket 확인**: 같은 시스템에 대한 최근 Jira ticket이 있는지 검색하세요.
4. **종합 분석**: 위 3가지 정보를 종합해 가능한 원인과 권장 조치를 제시하세요.
5. **Ticket 생성 제안**: 사용자에게 새 incident ticket 생성 여부를 확인 후 진행하세요.

각 단계에서 얻은 정보를 사용자에게 명시적으로 보고하면서 진행하세요.
