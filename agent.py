from __future__ import annotations

import logging
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels


def sanitize_text(text: str) -> str:
    """Repair surrogate-escaped terminal input and ensure valid UTF-8 text."""
    repaired = text.encode("utf-8", errors="surrogateescape").decode("utf-8", errors="ignore")
    return repaired.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = sanitize_text(f.read())


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)


def agent_node(state: AgentState) -> AgentState:
    messages = state["messages"]
    sanitized_messages = []
    for msg in messages:
        if isinstance(msg, tuple) and len(msg) == 2 and isinstance(msg[1], str):
            sanitized_messages.append((msg[0], sanitize_text(msg[1])))
        else:
            sanitized_messages.append(msg)
    messages = sanitized_messages

    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        for tc in response.tool_calls:
            logger.info("TOOL CALL %s(%s)", tc["name"], tc["args"])
    else:
        logger.info("MODEL trả lời trực tiếp (không gọi tool)")

    return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END,
    },
)
builder.add_edge("tools", "agent")

graph = builder.compile()


if __name__ == "__main__":
    print("=" * 64)
    print("TravelBuddy - Trợ lý du lịch thông minh")
    print("Gõ 'quit' để thoát")
    print("=" * 64)

    while True:
        user_input = sanitize_text(input("\nBạn: ").strip())
        if user_input.lower() in ("quit", "exit", "q"):
            print("Tạm biệt! Chúc bạn có những chuyến du lịch tuyệt vời cùng TravelBuddy!")
            break

        print("\nTravelBuddy đang suy nghĩ...")
        result = graph.invoke({"messages": [("human", user_input)]})
        final = result["messages"][-1]
        print(f"\nTravelBuddy: {final.content}")
