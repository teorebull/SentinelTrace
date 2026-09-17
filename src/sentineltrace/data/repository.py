from datetime import datetime

from sentineltrace.models.events import SecurityEvent


def get_user_events(events: list[SecurityEvent], user_id: str) -> list[SecurityEvent]:
    """
    Get all events for a specific user.

    Args:
        events (list[SecurityEvent]): List of events.
        user_id (str): User ID to filter events.

    Returns:
        list[SecurityEvent]: List of events for the specified user.
    """
    user_id_events = []
    for event in events:
        if event.user_id.lower() == user_id.lower():
            user_id_events.append(event)
    return user_id_events


def get_date_range_events(
    events: list[SecurityEvent], initial_date: datetime, final_date: datetime
) -> list[SecurityEvent]:
    """
    Get all events for a specific time range.

    Args:
        events (list[SecurityEvent]): List of events.
        initial_date (datetime): Initial date of the time range.
        final_date (datetime): Final date of the time range.

    Returns:
        list[SecurityEvent]: List of events for the specified user.
    """
    time_range_events = []
    for event in events:
        if initial_date <= event.timestamp <= final_date:
            time_range_events.append(event)
    return time_range_events


def get_ip_events(events: list[SecurityEvent], source_ip: str) -> list[SecurityEvent]:
    """
    Get all events for a specific source IP.

    Args:
        events (list[SecurityEvent]): List of events.
        source_ip (str): Source IP to filter events.

    Returns:
        list[SecurityEvent]: List of events for the specified user.
    """
    source_ip_events = []
    for event in events:
        if event.source_ip == source_ip:
            source_ip_events.append(event)
    return source_ip_events
