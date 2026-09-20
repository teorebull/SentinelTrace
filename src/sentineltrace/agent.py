import json

from ollama import ChatResponse

from sentineltrace.llm import ask_model
from sentineltrace.models.events import SecurityEvent
from sentineltrace.tools import TOOL_DEFINITIONS, execute_tool

SYSTEM_PROMPT = """
You are a defensive authentication-log investigator.

Use Python-provided count fields instead of recounting events yourself.

Every factual claim must be supported by returned evidence and should cite
event IDs when available.

Separate your response into:
- Observations: directly supported facts
- Inferences: conclusions derived from observations
- Unknowns: information not present in the telemetry
- Recommendations: suggested next actions

Do not claim MFA status unless MFA telemetry is provided.
Treat new IPs, countries, devices, anomaly signals, and threat-intelligence
results as signals rather than proof.
Do not invent missing facts.
"""


def run_agent(
    events: list[SecurityEvent],
    question: str,
    model: str = "qwen3",
    max_tool_calls: int = 5,
) -> ChatResponse:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {"role": "user", "content": question},
    ]
    for _ in range(max_tool_calls):
        response = ask_model(messages=messages, tools=TOOL_DEFINITIONS, model=model)
        messages.append(response.message)

        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                tool_result = execute_tool(
                    tool_name=tool_name, arguments=tool_args, events=events
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": json.dumps(tool_result),
                    }
                )

        else:
            return messages[-1]
    return response
