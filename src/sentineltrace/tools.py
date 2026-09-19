from sentineltrace.analysis.authentication import (
    get_failed_logins,
    get_successful_logins,
)
from sentineltrace.analysis.timelines import build_timeline
from sentineltrace.data.repository import get_user_events
from sentineltrace.models.events import SecurityEvent

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_failed_logins",
            "description": "Find failed authentication events for a user.",
            "parameters": {
                "type": "object",
                "required": ["user_id"],
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user to investigate.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_successful_logins",
            "description": "Find successful authentication events for a user.",
            "parameters": {
                "type": "object",
                "required": ["user_id"],
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user to investigate.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_timeline",
            "description": "Build a timeline of events for a user.",
            "parameters": {
                "type": "object",
                "required": ["user_id"],
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user to investigate.",
                    }
                },
            },
        },
    },
]


def execute_tool(
    tool_name: str,
    arguments: dict,
    events: list[SecurityEvent],
) -> dict[str, object]:
    try:
        tool_function = TOOL_FUNCTIONS[tool_name]
    except KeyError as error:
        raise ValueError(f"Tool {tool_name} not found.") from error

    return tool_function(events=events, user_id=arguments["user_id"])


def _summarize_events(events: list[SecurityEvent]) -> dict[str, object]:
    serialized_events = [event.model_dump(mode="json") for event in events]

    return {
        "count": len(serialized_events),
        "event_ids": [event["event_id"] for event in serialized_events],
        "events": serialized_events,
    }


def get_failed_logins_tool(
    events: list[SecurityEvent],
    user_id: str,
) -> dict[str, object]:
    user_events = get_user_events(events=events, user_id=user_id)
    failed_events = get_failed_logins(events=user_events)
    return _summarize_events(failed_events)


def get_successful_logins_tool(
    events: list[SecurityEvent],
    user_id: str,
) -> dict[str, object]:
    user_events = get_user_events(events=events, user_id=user_id)
    successful_events = get_successful_logins(events=user_events)
    return _summarize_events(successful_events)


def build_timeline_tool(
    events: list[SecurityEvent],
    user_id: str,
) -> dict[str, object]:
    user_events = get_user_events(events=events, user_id=user_id)
    timeline = build_timeline(events=user_events)
    return _summarize_events(timeline)


TOOL_FUNCTIONS = {
    "get_failed_logins": get_failed_logins_tool,
    "get_successful_logins": get_successful_logins_tool,
    "build_timeline": build_timeline_tool,
}
