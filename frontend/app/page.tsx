'use client';

import { useState, useEffect, useRef } from 'react';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { getOrCreateThreadId, startNewThread } from '@/lib/thread';
import { sendChatMessage } from '@/lib/transport';
import type { UISupervisorMessage } from '@/lib/types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function ChatPage() {
  const [messages, setMessages] = useState<UISupervisorMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [threadId, setThreadId] = useState<string>('');
  const [activeTaskId, setActiveTaskId] = useState<string | undefined>();
  const [useMultiAgent, setUseMultiAgent] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // 페이지 마운트 시 thread_id 초기화
  useEffect(() => { setThreadId(getOrCreateThreadId()); }, []);

  // 새 메시지 추가 시 자동 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (text: string) => {
    const userMessage: UISupervisorMessage = {
      id: crypto.randomUUID(), role: 'user', content: text, toolCalls: [], tasks: [], taskTokens: {},
    };
    const assistantMessage: UISupervisorMessage = {
      id: crypto.randomUUID(), role: 'assistant', content: '', toolCalls: [], tasks: [], taskTokens: {},
    };
    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setIsStreaming(true);
    setActiveTaskId(undefined);
    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    const endpoint = useMultiAgent ? '/chat/supervisor/stream' : '/chat/stream';
    try {
      await sendChatMessage(
        BACKEND_URL,
        endpoint,
        text,
        threadId,
        (event) => {
          // 상태 updater 밖에서 작업 선택 상태를 갱신한다.
          if (event.type === 'task_started') setActiveTaskId(event.task_id);
          if (event.type === 'task_completed') {
            setActiveTaskId(current => current === event.task_id ? undefined : current);
          }
          setMessages(prev => {
            return prev.map(message => {
              if (message.id !== assistantMessage.id) return message;
              switch (event.type) {
                case 'token':
                  return { ...message, content: message.content + event.content };
                case 'tool_call_start':
                  return {
                    ...message,
                    toolCalls: [...message.toolCalls, {
                      toolName: event.tool_name,
                      args: event.args,
                      status: 'pending',
                    }],
                  };
                case 'tool_call_end': {
                  const pendingIndex = message.toolCalls.findLastIndex(
                    tc => tc.toolName === event.tool_name && tc.status === 'pending'
                  );
                  return {
                    ...message,
                    toolCalls: message.toolCalls.map((toolCall, index) =>
                      index === pendingIndex
                        ? { ...toolCall, status: 'completed', result: event.result }
                        : toolCall
                    ),
                  };
                }
                case 'plan_created':
                  return { ...message, plan: event.plan };
                case 'task_list_created':
                  return { ...message, tasks: event.tasks };
                case 'task_started':
                  return {
                    ...message,
                    tasks: message.tasks.map(t => t.id === event.task_id
                      ? { ...t, status: 'in_progress' as const } : t),
                  };
                case 'task_completed':
                  return {
                    ...message,
                    tasks: message.tasks.map(t => t.id === event.task_id
                      ? { ...t, status: 'completed' as const, result: event.result_preview } : t),
                  };
                case 'sub_agent_token':
                  return {
                    ...message,
                    taskTokens: {
                      ...message.taskTokens,
                      [event.task_id]: (message.taskTokens[event.task_id] || '') + event.content,
                    },
                  };
                case 'done':
                  return message;
              }
            });
          });
        },
        abortControllerRef.current.signal,
      );
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        console.log('Stream cancelled by user');
      } else {
        console.error('Stream error:', error);
        setMessages(prev => {
          return prev.map(message => message.id === assistantMessage.id
            ? { ...message, content: `[에러 발생: ${(error as Error).message}]` }
            : message
          );
        });
      }
    } finally {
      setIsStreaming(false);
      setActiveTaskId(undefined);
    }
  };

  const handleNewThread = () => {
    abortControllerRef.current?.abort();
    setMessages([]);
    setThreadId(startNewThread());
    setActiveTaskId(undefined);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      <header className="flex justify-between items-center p-4 border-b">
        <div>
          <h1 className="text-xl font-bold">ICT 운영 지원 Agent</h1>
          <label className="flex items-center gap-2 mt-2 text-sm">
            <input
              type="checkbox"
              checked={useMultiAgent}
              onChange={(e) => setUseMultiAgent(e.target.checked)}
            />
            Multi-Agent 모드 (Supervisor)
          </label>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-500">Thread: {threadId.slice(0, 8)}...</span>
          <button
            onClick={handleNewThread}
            className="px-3 py-1 text-sm border rounded hover:bg-gray-100"
          >새 대화</button>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-20">메시지를 입력하여 대화를 시작하세요.</div>
        ) : (
          messages.map(msg => <ChatMessage key={msg.id} message={msg} activeTaskId={activeTaskId} />)
        )}
        <div ref={messagesEndRef} />
      </main>
      <ChatInput onSubmit={handleSubmit} disabled={isStreaming} />
    </div>
  );
}
