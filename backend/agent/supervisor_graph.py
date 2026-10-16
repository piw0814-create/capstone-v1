"""Supervisor 패턴 기반 Multi-agent Graph."""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.config import get_stream_writer
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from .mcp_client import get_mcp_tools


class SupervisorState(TypedDict):
    """대화 이력, 계획, 상태·결과를 포함한 작업 목록, 현재 작업 인덱스."""
    messages: Annotated[list[BaseMessage], add_messages]
    plan: str
    tasks: list[dict]
    current_task_index: int


async def build_supervisor_graph():
    """Supervisor 기반 multi-agent graph 생성."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    mcp_tools = await get_mcp_tools()
    research_agent = create_agent(
        model=llm,
        tools=mcp_tools,
        system_prompt=(
            "당신은 Research Agent입니다. "
            "주어진 task에 대해 적절한 tool을 호출하여 정보를 수집하세요. "
            "수집된 정보를 명확하게 요약하여 반환하세요."
        ),
    )
    writing_agent = create_agent(
        model=llm,
        tools=[],
        system_prompt=(
            "당신은 Writing Agent입니다. "
            "Research Agent가 수집한 정보를 받아 사용자가 이해하기 쉬운 형태로 "
            "통합된 답변을 작성하세요."
        ),
    )

    async def planning_node(state: SupervisorState) -> dict:
        """사용자 요청을 받아 plan 수립 및 task 분해."""
        user_msg = state["messages"][-1].content
        planning_prompt = f"""\
사용자 요청을 분석하여 다음 두 가지를 작성하세요.

사용자 요청: {user_msg}

1. plan: 전체 진행 계획 (자연어 2-3문장)
2. tasks: 실행할 task 목록 (각 task는 어느 sub-agent가 담당하는지 명시)
   - 가능한 agent: "research" (정보 검색), "writing" (응답 작성)

다음 JSON 형식으로 응답:
{{
  "plan": "...",
  "tasks": [
    {{"description": "...", "agent": "research"}},
    {{"description": "...", "agent": "writing"}}
  ]
}}
"""
        response = await llm.ainvoke([
            SystemMessage(content="You are a planning supervisor."),
            HumanMessage(content=planning_prompt),
        ])
        # JSON 파싱 (실습 원문의 간단화된 방식)
        import json
        import re
        json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
        parsed = json.loads(json_match.group())
        tasks = [
            {
                "id": f"task_{i+1}",
                "description": t["description"],
                "agent": t["agent"],
                "status": "pending",
                "result": None,
            }
            for i, t in enumerate(parsed["tasks"])
        ]
        return {
            "plan": parsed["plan"],
            "tasks": tasks,
            "current_task_index": 0,
        }

    def start_task_node(state: SupervisorState) -> dict:
        """작업 시작 상태를 별도 업데이트로 반환하여 UI에 먼저 전달."""
        idx = state["current_task_index"]
        tasks = state["tasks"].copy()
        tasks[idx] = {**tasks[idx], "status": "in_progress"}
        return {"tasks": tasks}

    async def execute_task_node(state: SupervisorState) -> dict:
        """현재 task를 담당 sub-agent에 위임하여 실행."""
        idx = state["current_task_index"]
        task = state["tasks"][idx]
        tasks = state["tasks"].copy()

        if task["agent"] == "research":
            agent = research_agent
        elif task["agent"] == "writing":
            previous_results = "\n\n".join([
                f"- {t['description']}\n  결과: {t['result']}"
                for t in tasks if t["result"] is not None
            ])
            task_context = (
                f"이전 task의 수집 결과:\n{previous_results}\n\n"
                f"위 정보를 바탕으로: {task['description']}"
            )
            agent = writing_agent

        agent_input_message = task["description"] if task["agent"] == "research" else task_context
        # 하위 그래프의 토큰을 명시적으로 읽고 작업 ID와 함께 상위로 전달.
        writer = get_stream_writer()
        result_text = ""
        async for mode, data in agent.astream(
            {"messages": [HumanMessage(content=agent_input_message)]},
            stream_mode=["messages", "updates"],
        ):
            if mode == "messages":
                message_chunk, metadata = data
                if isinstance(message_chunk, AIMessageChunk) and isinstance(message_chunk.content, str) and message_chunk.content:
                    writer({
                        "type": "sub_agent_token",
                        "task_id": task["id"],
                        "content": message_chunk.content,
                    })
            elif mode == "updates":
                for update in data.values():
                    if isinstance(update, dict):
                        for message in update.get("messages", []):
                            if isinstance(message, AIMessage):
                                result_text = message.content
        tasks[idx] = {**tasks[idx], "status": "completed", "result": result_text}
        return {
            "tasks": tasks,
            "current_task_index": idx + 1,
        }

    def should_continue(state: SupervisorState) -> Literal["execute", "finalize"]:
        if state["current_task_index"] < len(state["tasks"]):
            return "execute"
        return "finalize"

    async def finalize_node(state: SupervisorState) -> dict:
        """모든 task 완료 후 마지막 작업 결과를 최종 응답으로 반환."""
        last_task = state["tasks"][-1]
        final_response = last_task["result"]
        return {"messages": [AIMessage(content=final_response)]}

    workflow = StateGraph(SupervisorState)
    workflow.add_node("planning", planning_node)
    workflow.add_node("start_task", start_task_node)
    workflow.add_node("execute", execute_task_node)
    workflow.add_node("finalize", finalize_node)
    workflow.add_edge(START, "planning")
    workflow.add_edge("planning", "start_task")
    workflow.add_edge("start_task", "execute")
    workflow.add_conditional_edges(
        "execute", should_continue,
        {"execute": "start_task", "finalize": "finalize"},
    )
    workflow.add_edge("finalize", END)
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
