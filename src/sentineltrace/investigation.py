from sentineltrace.analysis.authentication import (
    get_failed_logins,
    get_successful_logins,
)
from sentineltrace.analysis.baselines import (
    compare_event_to_baseline,
    get_user_baseline,
)
from sentineltrace.analysis.timelines import build_timeline
from sentineltrace.data.repository import get_date_range_events, get_user_events


def investigate(events, user_id, history_start, investigation_start, investigation_end):
    """
    Run a deterministic authentication investigation for one user.

    Historical events are used to build the user's normal behavior baseline.
    Events in the investigation window are analyzed for failed logins,
    successful logins, timeline activity, and deviations from the baseline.

    Time boundaries use this convention:
        start <= timestamp < end

    Args:
        events: Validated SecurityEvent objects.
        user_id: User being investigated.
        history_start: Beginning of the historical baseline period.
        investigation_start: Beginning of the investigation period.
        investigation_end: End of the investigation period.

    Returns:
        A dictionary containing:
            user_id
            failed_logins
            successful_logins
            timeline
            baseline
            baseline_comparisons
    """
    # Get historical events in a definite time period
    historical_events = get_date_range_events(
        events=events, initial_date=history_start, final_date=investigation_start
    )
    # Get events in a definite time period relevant to the investigation
    investigation_events = get_date_range_events(
        events=events, initial_date=investigation_start, final_date=investigation_end
    )
    # Get user events in the period of the investigation
    user_events = get_user_events(events=investigation_events, user_id=user_id)

    # Find failed logins in the investigation period
    failed_logins = get_failed_logins(events=user_events)

    # Find successful logins in the investigation period
    successful_logins = get_successful_logins(events=user_events)

    # Build a timeline of events in the investigation period
    timeline = build_timeline(events=user_events)

    # Build the baseline from the historical period
    baseline = get_user_baseline(
        historical_events=historical_events,
        user_id=user_id,
        initial_date=history_start,
        final_date=investigation_start,
    )

    # Compare current successful login events to the baseline
    events_comparison = []
    for successful_login in successful_logins:
        events_comparison.append(compare_event_to_baseline(successful_login, baseline))

    # Return dictionary with all the necessary information for the investigation
    investigation_results = {
        "user_id": user_id,
        "failed_logins": failed_logins,
        "successful_logins": successful_logins,
        "timeline": timeline,
        "baseline": baseline,
        "baseline_comparisons": events_comparison,
    }

    return investigation_results
