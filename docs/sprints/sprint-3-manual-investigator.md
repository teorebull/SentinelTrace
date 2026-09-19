# Sprint 3: Deterministic Manual Investigator

## Purpose

Sprint 3 connects the deterministic Python components built in the earlier
sprints into one investigation workflow. It deliberately does not use an LLM.

The workflow proves that SentinelTrace can gather relevant evidence and compare
current activity with a user's historical behavior before an agent is added.

## What was built

The investigation accepts:

- validated authentication events,
- a target user,
- a historical time window,
- and a current investigation time window.

It then:

1. Selects historical events for the baseline period.
2. Selects current events for the investigation period.
3. Filters current events to the target user.
4. Finds failed authentication attempts.
5. Finds successful authentication attempts.
6. Builds a chronological timeline.
7. Builds a baseline from successful historical logins.
8. Compares current successful logins with that baseline.
9. Returns structured investigation results.

The result contains evidence rather than a security conclusion:

```text
user_id
failed_logins
successful_logins
timeline
baseline
baseline_comparisons
```

## Module responsibilities

### `data/loaders.py`

Reads the JSON dataset and validates each dictionary as a `SecurityEvent`.

### `data/repository.py`

Filters validated events by user, time window, and source IP.

### `analysis/authentication.py`

Separates failed and successful authentication events. It checks both the event
type and the `success` value so that successful resource access is not mistaken
for a successful login.

### `analysis/timelines.py`

Returns events ordered by their parsed timestamp. Chronological order is
important for recognizing sequences such as failures followed by a success and
post-login administrative access.

### `analysis/baselines.py`

Summarizes historical successful login behavior using known IPs, countries,
devices, and login hours. It compares current events with that summary and
returns boolean anomaly signals.

### `investigation.py`

Orchestrates the preceding functions into one deterministic investigation.

## Example interpretation

For `john.martinez`, historical events from January 1 through January 6 show:

```text
Known country: ES
Known IP: 198.51.100.19
Known device: dev-b70efe40f3
Usual login hour: 08:00 UTC
```

The January 7 activity contains:

```text
Repeated failures from 203.0.113.77
Successful login from the same IP
Country: RU
Device: device-999
Login hour: 03:00 UTC
Post-login access to administrative resources
```

Python can therefore report deterministic observations such as:

```text
new_ip: true
new_country: true
new_device: true
unusual_login_hour: true
```

These are signals and observations, not proof that an account was compromised.
The eventual report must distinguish observations from inferences and
recommendations.

## Why this matters for the final agentic system

The future LLM agent should decide which evidence to gather and in what order.
It should not read the raw dataset and invent facts or perform unreliable
calculations.

This sprint establishes the deterministic tools that the future agent will
call. It also provides a reference workflow against which the agent can later
be evaluated:

```text
Manual deterministic workflow
            ↓
LLM selects the same bounded tools
            ↓
Compare accuracy, evidence quality, and efficiency
```

The manual investigator is therefore not throwaway code. It is the baseline
implementation and the foundation for tool calling, evidence grounding, and
later evaluation.

## Current limitations

- The workflow is fixed rather than agent-controlled.
- Baseline comparisons are simple signals, not risk scores.
- Findings are not yet represented as dedicated evidence-backed report models.
- There is no external threat-intelligence enrichment.
- There is no LLM, LangGraph, API, or cloud deployment yet.

These limitations are intentional. The deterministic behavior should be
understood and tested before probabilistic reasoning is introduced.

## Next sprint

Sprint 4 introduces basic LLM tool calling with a small tool set. The LLM will
choose tools, Python will execute them, and bounded structured results will be
returned to the model.
