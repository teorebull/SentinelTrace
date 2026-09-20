# Sprint 5: Bounded LangGraph Investigation Workflow

## Purpose

Sprint 5 replaces the hand-written agent loop with an explicit LangGraph
workflow. The graph makes model decisions, tool execution, message history,
and stopping behavior visible and testable.

## What was built

### Shared state

`MessagesState` stores the information passed between graph nodes:

- conversation messages,
- validated security events,
- executed tool count,
- final response text.

Messages use a reducer so each node can return new messages while LangGraph
preserves the existing conversation history.

### Model node

`call_model` sends the current conversation and tool definitions to Ollama. It
converts the returned assistant message into the dictionary format used by the
graph state.

The message may contain either normal content or tool calls.

### Tool node

`execute_tools` reads tool calls from the latest assistant message, executes
the approved deterministic Python tools, serializes their results, and adds
tool messages to the conversation.

The node enforces a maximum of five executed tool calls.

### Routing

The graph uses two routing decisions:

```text
after model:
    tool calls → execute_tools
    no tool calls → END
    budget already reached → finalize_model

after tools:
    budget available → call_model
    budget reached → finalize_model
```

### Finalization node

`finalize_model` calls Ollama without tools when the budget is exhausted. It
asks the model to synthesize the evidence already collected instead of
requesting additional tools.

## Graph structure

```text
START
  ↓
call_model
  ↓
route_after_model
  ├── execute_tools ──→ route_after_tools ──→ call_model
  │                              │
  │                              └── finalize_model
  ├── finalize_model
  └── END
```

The finalization node always leads to `END`.

## Why this matters for the final goal

The graph is the foundation for a bounded agentic investigation. It makes the
agent's control flow explicit instead of hiding it inside a `while` loop.

This provides:

- predictable stopping behavior,
- a clear tool budget,
- inspectable conversation history,
- separate model and tool responsibilities,
- a structure that can later support persistence and evaluation.

The LLM still chooses what to investigate, while Python continues to execute
approved tools and calculate deterministic evidence.

## Safety and reliability boundaries

- Unknown tool names are rejected by the dispatcher.
- The graph limits executed tool calls.
- Finalization disables tools.
- Tool results are serialized before being returned to the model.
- Graph tests use mocked model responses and do not require Ollama.

## Verification

The graph tests verify that:

- a tool call is executed,
- tool results are added to message history,
- a final assistant response is returned,
- reaching exactly five tool calls triggers finalization,
- starting above the tool budget also triggers finalization.

The workflow has been manually verified with a local Ollama model and the
synthetic authentication dataset.

## Current limitations

- Conversation state is not persisted between separate graph runs.
- Tool calls are executed sequentially.
- Model responses are not yet validated against a structured report schema.
- Evidence-grounding quality still depends partly on the model prompt.
- No evaluation metrics have been collected yet.

These are planned improvements, not reasons to expand this sprint.

## Next sprint

Sprint 6 focuses on evaluation. It will compare the tool-using investigator with
a direct-LLM baseline using known synthetic ground truth.
