"""작업 이벤트 순서·토큰 귀속과 계획/도구 응답 노출 방지 검증."""
import unittest
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from streaming.event_converter import convert_supervisor_events


class SupervisorStreamingTest(unittest.IsolatedAsyncioTestCase):
    async def test_task_lifecycle_and_token_ownership(self):
        pending = [
            {"id": "task_1", "agent": "research", "status": "pending", "result": None},
            {"id": "task_2", "agent": "writing", "status": "pending", "result": None},
        ]
        first_started = [{**pending[0], "status": "in_progress"}, pending[1]]
        first_done = [{**pending[0], "status": "completed", "result": "조사"}, pending[1]]
        second_started = [first_done[0], {**pending[1], "status": "in_progress"}]
        second_done = [first_done[0], {**pending[1], "status": "completed", "result": "답변"}]

        async def source():
            yield "messages", (AIMessageChunk(content="계획 JSON"), {})
            yield "updates", {"planning": {"plan": "계획", "tasks": pending}}
            yield "updates", {"start_task": {"tasks": first_started}}
            yield "custom", {"type": "sub_agent_token", "task_id": "task_2", "content": "다른 작업 토큰"}
            yield "custom", {"type": "sub_agent_token", "task_id": "task_1", "content": "조사"}
            yield "messages", (ToolMessage(content="원시 도구 응답", tool_call_id="call_1"), {})
            yield "updates", {"execute": {"tasks": first_done}}
            yield "custom", {"type": "sub_agent_token", "task_id": "task_1", "content": "작업 밖 토큰"}
            yield "updates", {"start_task": {"tasks": second_started}}
            yield "custom", {"type": "sub_agent_token", "task_id": "task_2", "content": "답"}
            yield "custom", {"type": "sub_agent_token", "task_id": "task_2", "content": "변"}
            yield "updates", {"execute": {"tasks": second_done}}
            yield "updates", {"finalize": {"messages": [AIMessage(content="최종 답변")]}}

        events = [event.model_dump() async for event in convert_supervisor_events(source(), "thread-test")]
        self.assertEqual([event["type"] for event in events], [
            "plan_created", "task_list_created",
            "task_started", "sub_agent_token", "task_completed",
            "task_started", "sub_agent_token", "sub_agent_token", "task_completed",
            "token", "done",
        ])
        tokens = [event for event in events if event["type"] == "sub_agent_token"]
        self.assertEqual([(event["task_id"], event["content"]) for event in tokens], [
            ("task_1", "조사"), ("task_2", "답"), ("task_2", "변"),
        ])
        self.assertEqual(events[-2]["content"], "최종 답변")
        self.assertEqual(events[-1]["thread_id"], "thread-test")
        self.assertEqual(pending[0]["status"], "pending")


if __name__ == "__main__":
    unittest.main()
