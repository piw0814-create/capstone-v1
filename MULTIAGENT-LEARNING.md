# Multi-agent 실습

기준: 사용자 제공 멀티에이전트 노션 이미지 26장.

## 실행

프로젝트 루트에서 backend 실행:

```sh
cd backend
uv run --env-file ../.env uvicorn main:app --reload --port 8000
```

다른 터미널에서 frontend 실행:

```sh
cd frontend
npm run dev
```

http://localhost:3000 에서 Multi-Agent 모드 (Supervisor)를 선택한다. 선택 시 /chat/supervisor/stream, 해제 시 기존 /chat/stream으로 전송한다.

## 검증 질문

1. 운영 매뉴얼과 최근 incident를 종합해 장애 대응 가이드를 만들어 주세요.
2. DB 다운 시 절차와 네트워크 장애 시 절차를 비교해서 알려주세요
3. 안녕하세요

각 모드를 비교할 때 새 대화를 시작하여 별도 thread에서 확인한다.

## 현재 관찰 결과

계획과 작업 목록, 노란 진행 카드의 실제 토큰 표시, 녹색 완료 카드, 최종 답변을 확인했다. 원문에서 빠진 시작 상태 전달과 하위 토큰 스트리밍을 사용자 승인 후 보완했다. 작업은 순차 실행하며 최종 답변은 원문대로 token 이벤트 한 번으로 전송한다.

보완 사항과 검증 결과: verification/multiagent/results.md

구현 차이와 실제 검증 로그: verification/multiagent/implementation-notes.md
