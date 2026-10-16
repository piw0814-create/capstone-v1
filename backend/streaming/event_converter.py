"""
LangGraph event → SSE event 변환.

다음 4가지 SSE event로 변환:
- TokenEvent
- ToolCallStartEvent
- ToolCallEndEvent
- DoneEvent
"""
from typing import AsyncIterator, Optional
from langchain_core.messages import AIMessageChunk, ToolMessage
from schemas.stream import (
    StreamEvent,
    TokenEvent,
    ToolCallStartEvent,
    ToolCallEndEvent,
    DoneEvent,
    PlanCreatedEvent,
    TaskListCreatedEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    SubAgentTokenEvent,
)


async def convert_langgraph_events(
    langgraph_stream: AsyncIterator,
    thread_id: str,
) -> AsyncIterator[StreamEvent]:
    """
    LangGraph event stream을 SSE event stream으로 변환.

    Args:
        langgraph_stream: agent.astream(...)이 반환한 async iterator
        thread_id: 이번 stream의 thread_id (DoneEvent에 포함)

    Yields:
        StreamEvent 인스턴스
    """
    async for mode, data in langgraph_stream:
        if mode == "messages":
            # LLM token chunk
            message_chunk, metadata = data

            if isinstance(message_chunk, AIMessageChunk):
                # Tool call이 시작되는 chunk인지 확인
                if message_chunk.tool_call_chunks:
                    for tc_chunk in message_chunk.tool_call_chunks:
                        if tc_chunk.get("name"):
                            yield ToolCallStartEvent(
                                tool_name=tc_chunk["name"],
                                args=tc_chunk.get("args", {}) or {},
                            )
                # 일반 token (텍스트 content)
                elif message_chunk.content:
                    yield TokenEvent(content=message_chunk.content)

        elif mode == "updates":
            # Node 단위 업데이트 — tool 응답 도착 시 ToolCallEndEvent
            for node_name, node_update in data.items():
                if "messages" in node_update:
                    for msg in node_update["messages"]:
                        if isinstance(msg, ToolMessage):
                            yield ToolCallEndEvent(
                                tool_name=msg.name,
                                result=str(msg.content)[:200],  # preview
                            )

    # 모든 event 처리 완료 후 done event
    yield DoneEvent(thread_id=thread_id)


async def convert_supervisor_events(supervisor_stream, thread_id: str):
    """Supervisor graph stream을 본 capstone SSE event로 변환."""
    current_task_id = None
    previous_tasks = None

    async for mode, data in supervisor_stream:
        if mode == "updates":
            for node_name, node_update in data.items():
                if node_name == "planning":
                    if "plan" in node_update:
                        yield PlanCreatedEvent(plan=node_update["plan"])
                    if "tasks" in node_update:
                        yield TaskListCreatedEvent(tasks=node_update["tasks"])
                        previous_tasks = node_update["tasks"]
                elif node_name in ("start_task", "execute"):
                    if "tasks" in node_update:
                        new_tasks = node_update["tasks"]
                        for new_t, old_t in zip(new_tasks, previous_tasks or []):
                            if new_t["status"] == "in_progress" and old_t["status"] == "pending":
                                yield TaskStartedEvent(
                                    task_id=new_t["id"], agent_name=new_t["agent"],
                                )
                                current_task_id = new_t["id"]
                            elif new_t["status"] == "completed" and old_t["status"] != "completed":
                                yield TaskCompletedEvent(
                                    task_id=new_t["id"],
                                    result_preview=(new_t["result"] or "")[:200],
                                )
                                if current_task_id == new_t["id"]:
                                    current_task_id = None
                        previous_tasks = new_tasks
                elif node_name == "finalize":
                    if "messages" in node_update:
                        last_msg = node_update["messages"][-1]
                        if hasattr(last_msg, "content"):
                            yield TokenEvent(content=last_msg.content)
        elif mode == "custom":
            # 작업 ID가 현재 진행 중인 작업과 일치하는 생성 토큰만 전달.
            if (
                data.get("type") == "sub_agent_token"
                and data.get("task_id") == current_task_id
                and isinstance(data.get("content"), str)
                and data["content"]
            ):
                yield SubAgentTokenEvent(
                    task_id=current_task_id, content=data["content"],
                )

    yield DoneEvent(thread_id=thread_id)
