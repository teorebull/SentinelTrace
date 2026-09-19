from datetime import UTC, datetime
from pathlib import Path

import pytest

from sentineltrace.data.loaders import load_events
from sentineltrace.data.repository import get_date_range_events
from sentineltrace.tools import (
    TOOL_DEFINITIONS,
    build_timeline_tool,
    execute_tool,
    get_failed_logins_tool,
    get_successful_logins_tool,
)


def get_investigation_events():
    dataset_path = Path(__file__).parents[1] / "datasets" / "authentication_events.json"
    events = load_events(dataset_path)
    return get_date_range_events(
        events,
        datetime(2026, 1, 7, tzinfo=UTC),
        datetime(2026, 1, 8, tzinfo=UTC),
    )


def test_failed_login_tool_returns_serialized_events():
    result = get_failed_logins_tool(get_investigation_events(), "john.martinez")

    assert result["count"] == 20
    assert len(result["event_ids"]) == 20
    assert result["events"][0]["user_id"] == "john.martinez"
    assert isinstance(result["events"][0]["timestamp"], str)


def test_successful_login_tool_returns_serialized_events():
    result = get_successful_logins_tool(
        get_investigation_events(),
        "john.martinez",
    )

    assert result["count"] == 2
    assert all(event["success"] is True for event in result["events"])


def test_timeline_tool_returns_events_in_timestamp_order():
    result = build_timeline_tool(
        get_investigation_events(),
        "john.martinez",
    )

    timestamps = [event["timestamp"] for event in result["events"]]

    assert timestamps == sorted(timestamps)
    assert result["events"][0]["event_id"] == "evt-00369"


def test_tool_definitions_expose_only_user_id():
    names = [tool["function"]["name"] for tool in TOOL_DEFINITIONS]

    assert names == [
        "get_failed_logins",
        "get_successful_logins",
        "build_timeline",
    ]
    for tool in TOOL_DEFINITIONS:
        parameters = tool["function"]["parameters"]
        assert parameters["required"] == ["user_id"]
        assert set(parameters["properties"]) == {"user_id"}


def test_execute_tool_dispatches_to_the_requested_function():
    result = execute_tool(
        "get_failed_logins",
        {"user_id": "john.martinez"},
        get_investigation_events(),
    )

    assert result["count"] == 20


def test_execute_tool_rejects_unknown_tools():
    with pytest.raises(ValueError, match="not found"):
        execute_tool(
            "unknown_tool",
            {"user_id": "john.martinez"},
            get_investigation_events(),
        )
