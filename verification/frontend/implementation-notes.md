# S2 구현 및 검증 메모

- 제공된 노션의 옵션 A: custom SSE transport + React state로 구현. AI SDK 패키지는 설치했으나 useChat은 제공 코드에서 사용하지 않음.
- Next.js 15.5.28. 생성기의 React 19.1.0과 최신 AI SDK peer dependency 충돌로, 사용자 승인 후 React/React DOM 19.1 계열 최신 패치 설치.
- backend/main.py에는 localhost:3000 CORS 설정만 추가. SSE 프로토콜은 유지.
- TypeScript 검사 및 프로덕션 빌드 통과. / 및 /dev/thread HTTP 200, CORS preflight HTTP 200.
- 실제 transport 테스트는 transport-smoke.json 참고. 브라우저 렌더링 및 F1~E2 전체 검증을 대신하지 않음.

## 원문에서 유지한 제약

- F5는 스트리밍 중 새 메시지 전송을 요구하지만 ChatInput은 스트리밍 중 disabled 상태. 실제 UI에서 관찰한 결과를 기록할 것.
- 원문의 state updater가 메시지와 toolCalls를 직접 수정하여 개발 모드에서 토큰/도구가 중복 표시됨. 사용자 승인 후 메시지·도구를 새 객체로 갱신하도록 수정. 요청별 assistant message ID로 갱신 대상을 찾음. Strict Mode와 SSE 형식은 유지.
- 자동 재시도 코드는 없음. E2에서 실제 오류와 관찰 결과 기록.
- npm audit: next moderate, 포함된 postcss high 보고. 제시된 자동 수정은 Next 16 major upgrade이므로 실행하지 않음.

## 제출

results.md는 미작성 양식이며 검증 결과로 제출하지 말 것.
실제 캡처 F1.png, F2.png, F3.png, F4.png, F5-front.png, F5-back.png, E1.png, E2-front.png, E2-back.png와 작성 완료한 results.md를 ZIP으로 묶는다.
