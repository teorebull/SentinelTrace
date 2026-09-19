from datetime import datetime

import pytest
from pydantic import ValidationError

from sentineltrace.models.events import SecurityEvent


def test_valid_event_is_accepted():
    security_event = SecurityEvent(
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
    )
    assert security_event.event_id == "12345"


def test_timestamp_is_parsed_as_datetime():
    security_event = SecurityEvent(
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
    )
    assert isinstance(security_event.timestamp, datetime)


def test_optional_fields_can_be_omitted():
    security_event = SecurityEvent(
        event_id="12345",
        timestamp="2023-10-01T12:34:56Z",
        user_id="user_001",
        device_id="device_001",
        event_type="login",
        success=True,
        source_ip="192.168.1.1",
        country="US",
        user_agent="Mozilla/5.0",
    )
    assert security_event.resource is None
    assert security_event.session_id is None


def test_event_id_is_required():
    with pytest.raises(ValidationError):
        SecurityEvent(
            timestamp="2023-10-01T12:34:56Z",
            user_id="user_001",
            device_id="device_001",
            event_type="login",
            success=True,
            source_ip="192.168.1.1",
            country="US",
            user_agent="Mozilla/5.0",
        )
