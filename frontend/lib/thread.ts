/** Frontend가 thread_id를 생성하고 localStorage에 보관한다. */
const STORAGE_KEY = 'capstone:active_thread_id';

export function getOrCreateThreadId(): string {
  if (typeof window === 'undefined') {
    return 'ssr-placeholder';
  }
  const existing = localStorage.getItem(STORAGE_KEY);
  if (existing) {
    return existing;
  }
  const newId = crypto.randomUUID();
  localStorage.setItem(STORAGE_KEY, newId);
  return newId;
}

export function startNewThread(): string {
  if (typeof window === 'undefined') {
    return 'ssr-placeholder';
  }
  const newId = crypto.randomUUID();
  localStorage.setItem(STORAGE_KEY, newId);
  return newId;
}

export function clearThread(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(STORAGE_KEY);
}
