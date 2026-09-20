import operator

from typing_extensions import Annotated, TypedDict

from sentineltrace.models.events import SecurityEvent


class MessagesState(TypedDict):
    messages: Annotated[list[dict], operator.add]
    events: list[SecurityEvent]
    tool_call_count: int
    final_response: str | None
