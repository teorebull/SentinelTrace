from pathlib import Path

from sentineltrace.data.loaders import load_events
from sentineltrace.models.events import SecurityEvent


def test_load_events_returns_security_events():
    dataset_path = Path(__file__).parents[1] / "datasets" / "authentication_events.json"

    events = load_events(dataset_path)

    assert isinstance(events, list)
    assert len(events) > 0
    assert all(isinstance(event, SecurityEvent) for event in events)
