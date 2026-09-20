from pathlib import Path

from sentineltrace.data.loaders import load_events
from sentineltrace.graph import build_graph


class FakeMessage:
    def __init__(self, message: dict):
        self._message = message
        self.content = message.get("content", "")
        self.tool_calls = message.get("tool_calls")

    def model_dump(self, exclude_none: bool = False) -> dict:
        return self._message


class FakeResponse:
    def __init__(self, message: dict):
        self.message = FakeMessage(message)


def test_graph_executes_tool_and_returns_final_response(monkeypatch):
    dataset_path = Path(__file__).parents[1] / "datasets" / "authentication_events.json"
    events = load_events(dataset_path)

    responses = iter(
        [
            FakeResponse(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "get_failed_logins",
                                "arguments": {"user_id": "john.martinez"},
                            }
                        }
                    ],
                }
            ),
            FakeResponse(
                {
                    "role": "assistant",
                    "content": "Investigation complete.",
                }
            ),
        ]
    )

    def fake_ask_model(*, messages, tools, model="qwen3"):
        return next(responses)

    monkeypatch.setattr("sentineltrace.graph.ask_model", fake_ask_model)

    graph = build_graph()
    final_state = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Investigate john.martinez.",
                }
            ],
            "events": events,
            "tool_call_count": 0,
            "final_response": None,
        }
    )

    assert final_state["tool_call_count"] == 1
    assert final_state["messages"][-1]["content"] == "Investigation complete."
    assert any(message["role"] == "tool" for message in final_state["messages"])


def test_graph_finalizes_when_tool_budget_is_reached(monkeypatch):
    dataset_path = Path(__file__).parents[1] / "datasets" / "authentication_events.json"
    events = load_events(dataset_path)

    responses = iter(
        [
            FakeResponse(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "get_failed_logins",
                                "arguments": {"user_id": "john.martinez"},
                            }
                        }
                    ],
                }
            ),
            FakeResponse(
                {
                    "role": "assistant",
                    "content": "Budget-limited final report.",
                }
            ),
        ]
    )

    def fake_ask_model(*, messages, tools, model="qwen3"):
        return next(responses)

    monkeypatch.setattr("sentineltrace.graph.ask_model", fake_ask_model)

    final_state = build_graph().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Investigate john.martinez.",
                }
            ],
            "events": events,
            "tool_call_count": 4,
            "final_response": None,
        }
    )

    assert final_state["tool_call_count"] == 5
    assert final_state["final_response"] == "Budget-limited final report."


def test_graph_finalizes_when_tool_budget_is_already_exceeded(monkeypatch):
    responses = iter(
        [
            FakeResponse(
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "get_failed_logins",
                                "arguments": {"user_id": "john.martinez"},
                            }
                        }
                    ],
                }
            ),
            FakeResponse(
                {
                    "role": "assistant",
                    "content": "Final report after exceeded budget.",
                }
            ),
        ]
    )

    def fake_ask_model(*, messages, tools, model="qwen3"):
        return next(responses)

    monkeypatch.setattr("sentineltrace.graph.ask_model", fake_ask_model)

    final_state = build_graph().invoke(
        {
            "messages": [{"role": "user", "content": "Investigate John."}],
            "events": [],
            "tool_call_count": 6,
            "final_response": None,
        }
    )

    assert final_state["tool_call_count"] == 6
    assert final_state["final_response"] == "Final report after exceeded budget."
