from sentineltrace.models.events import SecurityEvent


def get_failed_logins(events: list[SecurityEvent]) -> list[SecurityEvent]:
    failed_logins = []
    for event in events:
        if event.event_type == "authentication" and not event.success:
            failed_logins.append(event)
    return failed_logins


def get_successful_logins(events: list[SecurityEvent]) -> list[SecurityEvent]:
    successful_logins = []
    for event in events:
        if event.event_type == "authentication" and event.success:
            successful_logins.append(event)
    return successful_logins
