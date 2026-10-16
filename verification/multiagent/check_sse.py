"""실제 endpoint의 이벤트 순서와 시각을 기록하는 검증용 스크립트."""
import json, time, uuid
from pathlib import Path
from urllib.request import Request, urlopen

output = Path(__file__).parent
thread_id = str(uuid.uuid4())
message = "운영 매뉴얼과 최근 incident를 종합해 장애 대응 가이드를 만들어 주세요."
request = Request('http://localhost:8000/chat/supervisor/stream',
    data=json.dumps({'message': message, 'thread_id': thread_id}).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
start = time.monotonic()
events = []
with urlopen(request, timeout=120) as response:
    status = response.status
    with (output/'supervisor.sse').open('w') as raw:
        for line in response:
            text = line.decode()
            raw.write(text)
            if text.startswith('data: '):
                events.append({'seconds': time.monotonic()-start, 'event': json.loads(text[6:])})
counts = {}
for item in events:
    kind = item['event']['type']
    counts[kind] = counts.get(kind, 0)+1
summary = {'status': status, 'message': message, 'thread_id': thread_id,
    'elapsed_seconds': time.monotonic()-start, 'counts': counts,
    'done_thread_matches': events[-1]['event'].get('thread_id') == thread_id,
    'events': events}
(output/'sse-check.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='events'}, ensure_ascii=False))
