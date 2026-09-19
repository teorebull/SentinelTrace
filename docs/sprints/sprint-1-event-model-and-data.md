# Sprint 1: Event Model and Synthetic Data

## Purpose

Sprint 1 defined the shape of an authentication event and created synthetic
data with known behavior.

## What was built

### `models/events.py`

The `SecurityEvent` Pydantic model validates fields such as:

- event ID,
- timestamp,
- user ID,
- event type,
- authentication result,
- source IP,
- country,
- device ID,
- user agent,
- resource,
- session ID.

Pydantic parses timestamp strings into Python `datetime` values and rejects
missing or invalid required fields.

### Synthetic dataset

The dataset contains mostly normal activity plus deliberately constructed
security scenarios, including:

- repeated failed logins,
- a successful login after failures,
- a new IP, country, and device,
- suspicious post-login resource access,
- one IP targeting multiple users,
- a benign corporate VPN pattern,
- omitted optional fields.

### Ground truth

`ground_truth.json` records the expected findings for the synthetic scenarios.
It is kept separate from the event data because it represents the known answer
used for later evaluation, not telemetry available to the investigator.

## Why it matters

The model creates a reliable contract between data loading, analysis tools, and
future LLM tools. Synthetic data is safe to use and gives the project known
answers for measuring accuracy, evidence recall, false positives, and
hallucinations.

## Relationship to the final goal

The final system must let Python compute trustworthy facts while the agent
reasons over those facts. This sprint establishes the validated facts and the
evaluation reference needed for that separation.

## Deliberate limitations

The data is synthetic and the event model is intentionally small. It does not
represent a production SIEM schema or real employer telemetry.
