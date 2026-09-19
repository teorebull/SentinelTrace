import pandas as pd

from sentineltrace.agent import SYSTEM_PROMPT, run_agent
from sentineltrace.data.loaders import load_events


# Read the data
events = load_events("../datasets/authentication_events.json")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", 
     "content": "Investigate the user john.martinez and his authentication events and provide possible candidates who may be a cyberthreat and why. Ground your answers based on metadata."},
]

call_agent = run_agent(events=events, question=messages[1]["content"], model="qwen3", max_tool_calls=5)
print(call_agent.content)