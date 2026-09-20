import json

from langgraph.graph import END, START, StateGraph

from sentineltrace.llm import ask_model
from sentineltrace.state import MessagesState
from sentineltrace.tools import TOOL_DEFINITIONS, execute_tool

# This is a limit on actual Python tool executions, not model responses.
MAX_TOOL_CALLS = 5


def call_model(state: MessagesState) -> dict:
    """Ask the model what to do next and preserve its complete message."""
    response = ask_model(
        messages=state["messages"],
        tools=TOOL_DEFINITIONS,
    )

    # Convert the Ollama message object into the dictionary format used by our
    # graph state. This preserves content and any requested tool calls.
    assistant_message = response.message.model_dump(exclude_none=True)

    return {"messages": [assistant_message]}


def execute_tools(state: MessagesState) -> dict:
    """Execute the tools requested by the latest assistant message."""
    latest_message = state["messages"][-1]
    tool_calls = latest_message.get("tool_calls", [])
    remaining_calls = MAX_TOOL_CALLS - state["tool_call_count"]
    tool_messages = []

    # Never execute more tools than the remaining investigation budget.
    for tool_call in tool_calls[:remaining_calls]:
        tool_name = tool_call["function"]["name"]
        tool_arguments = tool_call["function"]["arguments"]
        tool_result = execute_tool(
            tool_name=tool_name,
            arguments=tool_arguments,
            events=state["events"],
        )

        # Tool results become messages so the next model call can reason over
        # the evidence returned by Python.
        tool_messages.append(
            {
                "role": "tool",
                "tool_name": tool_name,
                "content": json.dumps(tool_result),
            }
        )

    return {
        "messages": tool_messages,
        "tool_call_count": state["tool_call_count"] + len(tool_messages),
    }


def route_after_model(state: MessagesState) -> str:
    """Choose whether to execute tools, finalize, or finish normally."""
    latest_message = state["messages"][-1]

    if state["tool_call_count"] >= MAX_TOOL_CALLS:
        return "finalize_model"
    if latest_message.get("tool_calls"):
        return "execute_tools"
    return "end"


def route_after_tools(state: MessagesState) -> str:
    """Choose whether another model call is allowed after tool execution."""
    if state["tool_call_count"] >= MAX_TOOL_CALLS:
        return "finalize_model"
    return "call_model"


def finalize_model(state: MessagesState) -> dict:
    """Ask the model for a final report without allowing more tools."""
    final_prompt = (
        "The tool-call limit has been reached. Analyze the complete evidence "
        "above and produce a human-readable report. Separate observations, "
        "inferences, unknowns, and recommendations. Cite event IDs and do not "
        "request additional tools."
    )
    messages = state["messages"] + [
        {
            "role": "user",
            "content": final_prompt,
        }
    ]

    final_response = ask_model(messages=messages, tools=[])
    final_message = final_response.message.model_dump(exclude_none=True)

    return {
        "messages": [final_message],
        "final_response": final_response.message.content,
    }


def build_graph():
    """Build and compile the bounded investigation graph."""
    graph = StateGraph(state_schema=MessagesState)
    graph.add_node("call_model", call_model)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("finalize_model", finalize_model)

    graph.add_edge(START, "call_model")

    # The model either requests tools, finishes normally, or must be finalized
    # because the budget was already exhausted.
    graph.add_conditional_edges(
        "call_model",
        route_after_model,
        {
            "execute_tools": "execute_tools",
            "finalize_model": "finalize_model",
            "end": END,
        },
    )

    # After tools run, either ask the model for another decision or finalize.
    graph.add_conditional_edges(
        "execute_tools",
        route_after_tools,
        {
            "call_model": "call_model",
            "finalize_model": "finalize_model",
        },
    )

    graph.add_edge("finalize_model", END)

    return graph.compile()
