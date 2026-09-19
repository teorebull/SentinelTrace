from datetime import UTC, datetime
from pathlib import Path

from sentineltrace.data.loaders import load_events
from sentineltrace.investigation import investigate


def test_john_investigation_finds_suspicious_activity():
    dataset_path = Path(__file__).parents[1] / "datasets" / "authentication_events.json"

    events = load_events(dataset_path)

    result = investigate(
        events=events,
        user_id="john.martinez",
        history_start=datetime(2026, 1, 1, tzinfo=UTC),
        investigation_start=datetime(2026, 1, 7, tzinfo=UTC),
        investigation_end=datetime(2026, 1, 8, tzinfo=UTC),
    )

    assert result["user_id"] == "john.martinez"
    assert len(result["failed_logins"]) == 20
    assert len(result["successful_logins"]) == 2

    comparisons = result["baseline_comparisons"]

    assert any(
        comparison["new_ip"]
        and comparison["new_country"]
        and comparison["new_device"]
        and comparison["unusual_login_hour"]
        for comparison in comparisons
    )
