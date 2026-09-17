import json

from sentineltrace.models.events import SecurityEvent


# Read json file
def load_events(file_path: str) -> list[SecurityEvent]:
    with open(file_path, "r") as f:
        data = json.load(f)
        validated_events = validate_events(data)
    return validated_events

# Validate using pydantic
def validate_events(raw_events: list[dict]) -> list[SecurityEvent]:
    validated_events = []
    for event in raw_events:
        validated_event = SecurityEvent.model_validate(event)
        validated_events.append(validated_event)
    return validated_events