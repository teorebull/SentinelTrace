from datetime import UTC, datetime

from sentineltrace.data.repository import (
    get_date_range_events,
    get_ip_events,
    get_user_events,
)
from sentineltrace.models.events import SecurityEvent

# Events for testing
security_events = [
    SecurityEvent(
        event_id="12345",
        timestamp="2023-10-01T12:34:56Z",
        user_id="user_001",
        device_id="device_001",
        event_type="login",
        success=True,
        source_ip="192.168.1.1",
        country="US",
        user_agent="Mozilla/5.0",
        resource=None,
        session_id="session_001",
    ),
    SecurityEvent(
        event_id="67890",
        timestamp="2024-07-05T19:14:36Z",
        user_id="user_099",
        device_id="device_099",
        event_type="login",
        success=True,
        source_ip="182.177.1.1",
        country="US",
        user_agent="Mozilla/5.0",
        resource=None,
        session_id="session_010",
    ),
]


def test_get_user_events():
    user_events = get_user_events(security_events, "user_001")

    assert security_events[0] in user_events
    assert security_events[1] not in user_events


def test_get_date_range_events():
    range_events = get_date_range_events(
        security_events,
        datetime(2023, 10, 1, tzinfo=UTC),
        datetime(2024, 6, 5, tzinfo=UTC),
    )

    assert security_events[0] in range_events
    assert security_events[1] not in range_events


def test_get_ip_events():
    ip_events = get_ip_events(security_events, "192.168.1.1")

    assert security_events[0] in ip_events
    assert security_events[1] not in ip_events
