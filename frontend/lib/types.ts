/** Backend schemas/stream.py와 대응하는 SSE 이벤트 타입. */
export interface TokenEvent {
  type: 'token';
  content: string;
}
export interface ToolCallStartEvent {
  type: 'tool_call_start';
  tool_name: string;
  args: Record<string, unknown>;
}
export interface ToolCallEndEvent {
  type: 'tool_call_end';
  tool_name: string;
  result?: string;
}
export interface DoneEvent {
  type: 'done';
  thread_id: string;
}
export type StreamEvent =
  | TokenEvent | ToolCallStartEvent | ToolCallEndEvent | DoneEvent
  | PlanCreatedEvent | TaskListCreatedEvent | TaskStartedEvent
  | TaskCompletedEvent | SubAgentTokenEvent;

/** Backend thread state와 별개로 frontend가 관리하는 UI 메시지. */
export interface UIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolCalls: UIToolCall[];
}
export interface UIToolCall {
  toolName: string;
  args: Record<string, unknown>;
  result?: string;
  status: 'pending' | 'completed';
}

/** Multi-agent (Supervisor pattern) event types. */
export interface PlanCreatedEvent {
  type: 'plan_created';
  plan: string;
}
export interface Task {
  id: string;
  description: string;
  agent: string;
  status: 'pending' | 'in_progress' | 'completed';
  result?: string;
}
export interface TaskListCreatedEvent {
  type: 'task_list_created';
  tasks: Task[];
}
export interface TaskStartedEvent {
  type: 'task_started';
  task_id: string;
  agent_name: string;
}
export interface TaskCompletedEvent {
  type: 'task_completed';
  task_id: string;
  result_preview?: string;
}
export interface SubAgentTokenEvent {
  type: 'sub_agent_token';
  task_id: string;
  content: string;
}

/** 기존 single-agent 메시지와 도구 표시를 유지하면서 확장. */
export interface UISupervisorMessage extends UIMessage {
  plan?: string;
  tasks: Task[];
  taskTokens: Record<string, string>;
}
