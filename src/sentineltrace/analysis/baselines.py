from datetime import datetime

from sentineltrace.analysis.authentication import get_successful_logins
from sentineltrace.data.repository import get_date_range_events
from sentineltrace.models.events import SecurityEvent


def get_user_baseline(
    historical_events: list[SecurityEvent],
    user_id: str,
    initial_date: datetime,
    final_date: datetime,
) -> dict:
    if initial_date and final_date:
        historical_events = get_date_range_events(
            historical_events, initial_date, final_date
        )

    successful_events = get_successful_logins(historical_events)
    user_successful_events = [
        event for event in successful_events if event.user_id == user_id
    ]
    baseline = {
        "user_id": user_id,
        "known_ips": set(),
        "known_countries": set(),
        "known_devices": set(),
        "usual_login_hours": set(),
    }

    for event in user_successful_events:
        baseline["known_ips"].add(event.source_ip)
        baseline["known_countries"].add(event.country)
        baseline["known_devices"].add(event.device_id)
        baseline["usual_login_hours"].add(event.timestamp.hour)
    return baseline


def compare_event_to_baseline(event: SecurityEvent, baseline: dict) -> dict:
    event_values = [
        event.source_ip,
        event.country,
        event.device_id,
        event.timestamp.hour,
    ]

    baseline_values = [
        baseline["known_ips"],
        baseline["known_countries"],
        baseline["known_devices"],
        baseline["usual_login_hours"],
    ]

    results = []
    comparison_results = {
        "new_ip": bool(),
        "new_country": bool(),
        "new_device": bool(),
        "unusual_login_hour": bool(),
    }

    for event_value, baseline_value in zip(event_values, baseline_values):
        results.append(event_value not in baseline_value)

    comparison_results["new_ip"] = results[0]
    comparison_results["new_country"] = results[1]
    comparison_results["new_device"] = results[2]
    comparison_results["unusual_login_hour"] = results[3]

    return comparison_results
