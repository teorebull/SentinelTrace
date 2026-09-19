from sentineltrace.models.events import SecurityEvent


def build_timeline(events: list[SecurityEvent]) -> list[SecurityEvent]:
    sorted_events = sorted(events, key=lambda event: event.timestamp)
    return sorted_events
