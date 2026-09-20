from pathlib import Path

from sentineltrace.data.loaders import load_events
from sentineltrace.graph import build_graph

events = load_events(Path("../datasets/authentication_events.json"))

initial_state = {
    "messages": [
        {
            "role": "user",
            "content": (
                "Investigate authentication activity for "
                "john.martinez. Use the available tools."
            ),
        }
    ],
    "events": events,
    "tool_call_count": 0,
    "final_response": None,
}

graph = build_graph()
final_state = graph.invoke(initial_state)

print("Tool calls:", final_state["tool_call_count"])
print("Final message:", final_state["messages"][-1]["content"])
