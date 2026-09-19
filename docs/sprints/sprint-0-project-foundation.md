# Sprint 0: Project Foundation

## Purpose

Sprint 0 created a clean, runnable Python project before adding security
analysis or AI behavior.

## What was built

- Python project configuration in `pyproject.toml`.
- Python 3.12 requirement.
- `src` package layout.
- Runtime dependencies for Pydantic and Pandas.
- Development dependencies for pytest and Ruff.
- A packaged CLI entry point named `sentineltrace`.
- A smoke test proving that the package can be imported.

## Why it matters

The project needs a reliable foundation before domain logic is added. The
configuration makes installation, imports, testing, formatting, and linting
repeatable for both local development and future deployment.

The `src/sentineltrace` package layout also prevents accidental imports from
the repository root and keeps application code separate from tests and data.

## Verification

The project can be checked with:

```text
uv run pytest
uv run ruff check .
uv run sentineltrace
```

## Relationship to the final goal

The final agentic investigator must be runnable, testable, and installable.
Sprint 0 provides the engineering foundation for the deterministic analysis
engine and the future LLM tool-calling workflow.

## Deliberate limitations

No investigation logic, LLM, database, API, Docker, or cloud infrastructure
was added. Those components would make the project harder to understand before
the basic Python workflow exists.
