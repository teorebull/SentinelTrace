# Sprint 2: Loading and Repository Queries

## Purpose

Sprint 2 made the event data usable by application code. It loads JSON into
validated `SecurityEvent` objects and provides simple query functions over
those objects.

## What was built

### `data/loaders.py`

The loader:

1. Opens the JSON dataset.
2. Parses it into Python dictionaries.
3. Validates every event with Pydantic.
4. Returns `list[SecurityEvent]`.

Invalid event data fails validation instead of silently entering the analysis
pipeline.

### `data/repository.py`

The repository provides queries for:

- events belonging to a user,
- events inside a time window,
- events associated with a source IP.

Time windows use a start-inclusive, end-exclusive convention:

```text
start <= timestamp < end
```

This avoids overlapping adjacent windows and handles boundaries consistently.

## Why it matters

Analysis functions should not read files or know how JSON is structured. They
should receive validated events and work with simple query results.

This separation also means the storage mechanism can later change from JSON to
a database without rewriting the authentication analysis logic.

## Verification

The loader and query behavior are covered by tests for:

- successful loading,
- Pydantic event objects,
- user filtering,
- time-window filtering,
- IP filtering,
- timezone-aware timestamps.

## Relationship to the final goal

These functions become deterministic tools for the future investigator agent.
The LLM will eventually choose which query or analysis tool to call, but Python
will continue to perform the actual filtering and validation.

## Deliberate limitations

The repository is currently in-memory and file-backed. No database, caching,
search engine, or framework abstraction is needed at this scale.
