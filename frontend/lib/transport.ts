/** Backend SSE stream을 파싱하여 이벤트마다 callback을 호출한다. */
import type { StreamEvent } from './types';

export async function sendChatMessage(
  backendUrl: string,
  endpoint: string,
  message: string,
  threadId: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${backendUrl}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId }),
    signal,
  });
  if (!response.ok) {
    throw new Error(`Backend error: ${response.status} ${response.statusText}`);
  }
  if (!response.body) {
    throw new Error('No response body');
  }
  const reader = response.body
    .pipeThrough(new TextDecoderStream())
    .getReader();
  let buffer = '';
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += value;
      const events = buffer.split('\n\n');
      buffer = events.pop() || '';
      for (const eventBlock of events) {
        const parsed = parseSSEEvent(eventBlock);
        if (parsed) onEvent(parsed);
      }
    }
  } finally {
    reader.releaseLock();
  }
}

function parseSSEEvent(block: string): StreamEvent | null {
  const lines = block.split('\n');
  let dataLine: string | null = null;
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      dataLine = line.slice(6);
    }
    // event: 라인은 data의 type 필드와 같은 정보이므로 사용하지 않음
  }
  if (!dataLine) return null;
  try {
    return JSON.parse(dataLine) as StreamEvent;
  } catch (e) {
    console.error('Failed to parse SSE event:', dataLine, e);
    return null;
  }
}
