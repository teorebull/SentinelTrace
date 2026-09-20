# Sprint 4: First Ollama Tool-Calling Loop

## Purpose

Sprint 4 introduces the first probabilistic component into SentinelTrace: a
local LLM that can choose deterministic Python tools.

The LLM does not receive the entire dataset or calculate security facts
directly. Python remains responsible for filtering, counting, ordering, and
serializing event evidence.

## What was built

### Ollama client

`llm.py` provides a small client wrapper around the Ollama Python library. It
sends conversation messages and tool definitions to a local Ollama model and
returns the complete model response.

The complete response is preserved because it may contain either normal text or
tool calls.

### Tool wrappers

`tools.py` wraps existing deterministic analysis functions:

- `get_failed_logins`
- `get_successful_logins`
- `build_timeline`

The wrappers filter events for the requested user, call the existing analysis
function, and serialize `SecurityEvent` objects into JSON-compatible data.

Tool results also include deterministic summaries:

```text
count
event_ids
```

The count is calculated by Python so the model does not need to count raw
events itself.

### Tool definitions and dispatcher

The LLM-facing schemas describe the tools and expose only the `user_id`
argument. The event list remains internal to Python.

The dispatcher maps an approved tool name to its Python implementation and
rejects unknown tools. This prevents arbitrary function execution.

### Agent loop

`agent.py` implements the basic tool-calling workflow:

```text
send question and tool definitions to Ollama
        ↓
receive assistant response
        ↓
if tool calls exist
        ↓
execute approved Python tools
        ↓
append serialized tool results
        ↓
ask Ollama again
        ↓
return final response when no tool call remains
```

The loop has a maximum tool-call limit to prevent infinite execution.

## Why this matters for the final goal

This sprint demonstrates the central SentinelTrace architecture:

```text
LLM chooses what to investigate
Python computes trustworthy evidence
LLM explains the evidence
```

The existing deterministic functions are not replaced. They become tools that
an agent can select. This makes the system more flexible while preserving
testable security logic.

## What is intentionally not solved yet

The model can still:

- misinterpret evidence,
- omit event IDs,
- make unsupported inferences,
- recommend actions based on unavailable telemetry,
- produce repetitive or overly confident reports.

These are known limitations for this sprint. The current goal is to verify that
the basic tool-calling mechanics work. Evidence grounding, structured report
validation, and evaluation will be improved in later sprints.

## Verification

The deterministic tools and dispatcher are tested without requiring an LLM.
The Ollama loop is manually verified with a local model because live model
calls are unsuitable for the normal unit-test suite.

## Next sprint

Sprint 5 will make the workflow more explicit and bounded using LangGraph. It
will represent model decisions, tool execution, evidence, stopping conditions,
and final reporting as graph state rather than a hand-written loop.
