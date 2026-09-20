from sentineltrace.agent import SYSTEM_PROMPT, run_agent
from sentineltrace.data.loaders import load_events

# Read the data
events = load_events("../datasets/authentication_events.json")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {
        "role": "user",
        "content": (
            "Investigate john.martinez's authentication events and identify "
            "possible threats. Ground your answer in the event metadata."
        ),
    },
]

call_agent = run_agent(
    events=events,
    question=messages[1]["content"],
    model="qwen3",
    max_tool_calls=5,
)
print(call_agent.message.content)
