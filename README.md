# SentinelTrace — Agentic Threat Investigator

SentinelTrace is a **Python-first, agentic cybersecurity investigation project** designed to explore where LLM agents add real value beyond simply sending logs to a model.

The system investigates suspicious **authentication activity** by combining deterministic Python analysis with an LLM that decides what evidence to gather next. The goal is not to build a full SIEM, antivirus product, or autonomous SOC platform. The goal is to build a small, understandable, testable AI engineering system that can be developed by someone actively improving their **Python and Generative AI skills**.

> **Core design rule:** Python computes facts. The LLM plans the investigation and explains the evidence.

---

## Why this project exists

A security alert rarely contains enough context to make a useful decision.

For example:

```text
User: john@company.com
47 failed logins from 185.x.x.x
Successful login 90 seconds later
```

A useful investigation may need to answer:

- Has this user logged in from this IP before?
- Is the country unusual for this user?
- Was the successful login from the same IP as the failed attempts?
- Was the device new?
- What happened immediately after the successful login?
- Has the same IP targeted other users?
- Does an external threat-intelligence source report previous abuse?
- Could the activity be explained by a corporate VPN or another benign condition?

A normal LLM prompt could try to reason over a sample of logs, but that approach has important limitations: large logs are expensive to send, numerical reasoning can be unreliable, evidence can be missed, and the model can make unsupported claims.

SentinelTrace instead gives the model access to **small, deterministic Python tools** that query and analyze the data. The model decides which tool to call next, but the underlying facts come from code.

---

## Learning goals

This is first and foremost an **AI engineering learning project**.

The project should help practise:

### Python

- Project/package structure
- Type hints
- Pydantic models
- Pandas data manipulation
- File loading and validation
- Functions and modules
- Error handling
- Unit testing with `pytest`
- API clients with `httpx`
- Configuration and environment variables
- Later: async I/O where it provides a real benefit

### Generative AI

- LLM tool calling
- Structured outputs
- Prompt design
- Agent state and control flow
- LangGraph
- Evidence grounding
- Hallucination reduction
- Cost/token awareness
- Model-provider abstraction
- Evaluation of agentic systems
- Later: RAG for internal context

### AI / software engineering

- Separating deterministic logic from probabilistic reasoning
- Designing clean tool interfaces
- Building reproducible evaluations
- Docker
- FastAPI
- Basic cloud deployment
- Logging and observability
- CI/testing

The aim is **not** to hide these concepts behind frameworks. The project should introduce abstractions only after the underlying mechanics are understood.

---

# Product definition

## What SentinelTrace does

Given authentication logs and a suspicious user, IP, or time window, SentinelTrace gathers relevant evidence and produces a structured investigation report.

A mature investigation might look like this:

```text
Alert / Question
      |
      v
LLM Investigator
      |
      +--> get_failed_logins()
      |
      +--> get_successful_logins()
      |
      +--> get_user_baseline()
      |
      +--> get_ip_usage()
      |
      +--> get_post_login_activity()
      |
      +--> lookup_ip_reputation()
      |
      v
Evidence-backed report
```

The LLM should **not** receive the full raw dataset by default.

It should receive:

- the investigation question,
- the available tools,
- the current investigation state,
- and bounded evidence returned by those tools.

---

## What SentinelTrace is NOT

Version 1 is intentionally limited.

SentinelTrace is **not**:

- a production SIEM,
- an antivirus product,
- a malware-analysis platform,
- a vulnerability scanner,
- an offensive-security tool,
- an autonomous incident-response system,
- a system that blocks users or IPs automatically,
- a large multi-agent platform,
- or a replacement for a security analyst.

The first version focuses only on **authentication-log investigations**.

Keeping the scope narrow is deliberate. The important part of the project is learning to build and evaluate the investigation workflow properly.

---

# Core principle: deterministic facts, probabilistic reasoning

The project should clearly separate four concepts.

## 1. Observation

A fact directly supported by the data.

```text
47 failed login events originated from 185.23.10.12.
```

This should be computed by Python.

## 2. Inference

An interpretation of one or more observations.

```text
The sequence is consistent with a possible account-compromise attempt.
```

The LLM can help make this inference.

## 3. Unknown

Information the system does not have.

```text
MFA telemetry is unavailable.
```

Unknown information must remain unknown. The model should never invent missing telemetry.

## 4. Recommendation

A suggested next action.

```text
Verify the login with the account owner.
```

These categories should remain clearly separated in the final report.

---

# Example investigation

Imagine this synthetic scenario:

```text
Normal behaviour for john@company.com
-------------------------------------
Country: Spain
Typical hours: 09:00–18:00
Known device: device_123
Known IP ranges: normal residential/company addresses

Suspicious activity
-------------------
03:12 failed login — 185.23.10.12 — Russia — device_999
03:13 failed login — 185.23.10.12 — Russia — device_999
03:14 failed login — 185.23.10.12 — Russia — device_999
...
03:17 successful login — 185.23.10.12 — Russia — device_999
03:21 access /admin/customers
```

SentinelTrace should eventually be capable of discovering that:

- repeated failures occurred,
- a successful login followed,
- the same IP was involved,
- the IP was new for the user,
- the country was new,
- the device was new,
- and unusual resource access followed the login.

The important part is that these facts are produced by deterministic tools, not guessed by the LLM.

---

# Architecture

The target architecture is deliberately simple.

```text
CLI / FastAPI later
        |
        v
Investigation Service
        |
        v
   Agent / LangGraph
    /      |       \
   v       v        v
Log     Baseline   Threat Intel
Tools    Tools       Tools
   \       |        /
    \      |       /
       Evidence
          |
          v
 Structured Report
```

The architecture should evolve gradually. Do not build every layer at the beginning.

---

# Recommended project structure

```text
sentineltrace/
├── pyproject.toml
├── README.md
├── src/
│   └── sentineltrace/
│       ├── cli.py
│       ├── config.py
│       │
│       ├── models/
│       │   ├── events.py
│       │   ├── evidence.py
│       │   └── reports.py
│       │
│       ├── data/
│       │   ├── loaders.py
│       │   └── repository.py
│       │
│       ├── analysis/
│       │   ├── authentication.py
│       │   ├── baselines.py
│       │   ├── timelines.py
│       │   └── anomalies.py
│       │
│       ├── tools/
│       │   ├── log_tools.py
│       │   ├── user_tools.py
│       │   ├── threat_intel.py
│       │   └── knowledge.py
│       │
│       ├── agent/
│       │   ├── state.py
│       │   ├── graph.py
│       │   ├── prompts.py
│       │   └── policies.py
│       │
│       ├── evaluation/
│       │   ├── cases.py
│       │   ├── metrics.py
│       │   └── runner.py
│       │
│       └── api/
│           └── main.py
│
├── datasets/
├── tests/
└── knowledge/
```

This is the **target structure**, not the day-one structure.

At the beginning, create only the modules currently needed.

---

# Technology choices

The project should stay inexpensive and Python-heavy.

| Area | Initial choice | Reason |
|---|---|---|
| Language | Python 3.12+ | Main learning goal |
| Dependency management | `uv` | Fast and simple |
| Data validation | Pydantic | Explicit schemas and structured outputs |
| Data analysis | Pandas | Good for portfolio-scale logs |
| Testing | pytest | Standard Python testing workflow |
| Lint / formatting | Ruff | Fast and simple |
| HTTP | httpx | Threat-intelligence/API calls later |
| Agent orchestration | LangGraph | Added only after the manual loop is understood |
| API | FastAPI | Added after the core works |
| Containerization | Docker | Deployment and reproducibility |
| Cloud | AWS, serverless-first | Cheap deployment practice |
| Local LLM option | Ollama | Free local development where practical |
| Hosted LLM | Low-cost provider/model | Evaluation and demo when better quality is useful |

Avoid adding technologies simply because they are fashionable.

Every dependency should solve a problem that already exists.

---

# Data model

Version 1 focuses on authentication/security events.

A first `SecurityEvent` model can contain fields such as:

```text
timestamp
user_id
event_type
success
source_ip
country
device_id
resource
user_agent
session_id
event_id
```

Example:

```json
{
  "event_id": "evt-1042",
  "timestamp": "2026-09-17T03:17:24Z",
  "user_id": "john@company.com",
  "event_type": "authentication",
  "success": true,
  "source_ip": "185.23.10.12",
  "country": "RU",
  "device_id": "device_999",
  "resource": null,
  "user_agent": "Mozilla/5.0",
  "session_id": "session_42"
}
```

The exact model can evolve as the project develops.

---

# Synthetic data first

Do **not** start with real employer logs.

The repository should use synthetic or deliberately anonymized data.

Synthetic data is useful because the project needs **known ground truth** for evaluation.

Useful scenarios include:

- normal user activity,
- repeated failed logins,
- failures followed by a successful login,
- new-country login,
- new-device login,
- suspicious post-login resource access,
- benign corporate VPN false positive,
- legitimate unusual travel,
- one IP targeting several accounts.

Each scenario should eventually contain ground-truth information describing:

```text
scenario_id
suspicious_user
suspicious_ip
important_event_ids
expected_findings
benign_or_malicious_simulation
explanation
```

Start with one scenario. Add complexity only when the existing scenario works.

---

# Deterministic investigation tools

The first useful version of SentinelTrace should contain **no agent at all**.

Start with ordinary Python functions.

Possible tools:

### `load_events()`

Loads and validates a dataset.

### `get_user_events()`

Returns bounded events for a specific user and time period.

### `get_failed_logins()`

Returns failed authentication attempts and deterministic counts.

### `get_successful_logins()`

Returns successful authentication events.

### `build_timeline()`

Returns relevant events ordered by timestamp.

### `get_user_baseline()`

Summarizes typical behaviour such as:

- countries,
- IPs,
- devices,
- login hours,
- normal failure rate.

### `compare_to_baseline()`

Computes differences between current activity and historical behaviour.

### `get_ip_usage()`

Finds other events/users associated with an IP.

### `get_post_login_activity()`

Returns actions occurring after a successful authentication.

### `lookup_ip_reputation()`

Later, queries an authorized threat-intelligence API.

Tools should return **structured data**, not narrative prose.

Good:

```json
{
  "failed_attempts": 47,
  "source_ips": ["185.23.10.12"],
  "first_failure": "2026-09-17T03:12:02Z",
  "last_failure": "2026-09-17T03:16:49Z"
}
```

Avoid:

```text
The login activity looks highly suspicious.
```

Interpretation belongs later in the reasoning/reporting layer.

---

# Development strategy

SentinelTrace should be built in layers.

## Phase 0 — Python project setup

Goal: create a clean, runnable Python package.

Build:

- `uv` project
- basic package structure
- Ruff
- pytest
- CLI skeleton
- initial models

No AI is needed.

---

## Phase 1 — Log analysis engine

Goal: prove that Python can retrieve and compute the required evidence.

Build:

- synthetic log generator
- loader
- repository/query layer
- authentication filters
- timelines
- simple user baselines
- tests

Expected result:

```text
=== SentinelTrace Investigation ===

User: john@company.com

Failed logins: 47
Source IP: 185.23.10.12
Successful login: 03:17:24
New device: yes
New country: yes
```

Still no LLM.

---

## Phase 2 — Manual investigator

Goal: understand the investigation workflow before automating it with an agent.

Write ordinary Python orchestration that calls the tools in a fixed order.

For example:

```text
load events
    ↓
find failed logins
    ↓
find successful login
    ↓
compare user baseline
    ↓
inspect IP
    ↓
inspect post-login activity
    ↓
generate simple report
```

This stage is important because it teaches what the later agent is replacing.

---

## Phase 3 — First LLM tool calling

Goal: allow the model to choose between a small number of tools.

Start with only 2–3 tools.

Example:

```text
Question:
Investigate suspicious login activity for john@company.com.

Available tools:
- get_failed_logins
- get_successful_logins
- build_timeline
```

The model selects a tool, Python executes it, and the result returns to the model.

Do not introduce LangGraph immediately.

First understand the basic loop:

```text
LLM decides
    ↓
Python executes tool
    ↓
result returned to LLM
    ↓
LLM decides again
```

---

## Phase 4 — LangGraph agent

Goal: turn the manual tool loop into an explicit, bounded agent workflow.

Possible investigation state:

```text
question
target entities
time window
evidence
hypotheses
tool-call history
unresolved questions
tool-call budget
cost/token budget
final report
```

Conceptually:

```text
START
  |
  v
Understand question
  |
  v
Choose next action
  |
  +----> call tool ----> collect evidence ---+
  |                                          |
  +<-----------------------------------------+
  |
  +----> enough evidence / budget reached
  |
  v
Validate claims
  |
  v
Generate report
  |
 END
```

Stopping rules are required.

The agent should have limits such as:

- maximum number of tool calls,
- maximum duration,
- maximum model/token cost,
- protection against repeating identical calls forever.

---

## Phase 5 — Evaluation

Evaluation is part of the core project, not optional polish.

Create a simple baseline:

> Give an LLM a bounded sample of logs directly and ask it to investigate.

Then compare that with SentinelTrace's tool-using agent.

Possible metrics:

| Metric | Question |
|---|---|
| Incident detection | Did it identify the important suspicious entity/activity? |
| Evidence precision | Do cited events actually support the findings? |
| Evidence recall | Did it retrieve the important ground-truth events? |
| Hallucination rate | Did it invent unsupported facts? |
| Tool efficiency | How many tool calls were required? |
| Latency | How long did the investigation take? |
| LLM cost | How much model usage did the investigation require? |

The interesting question is not simply:

> "Does the agent work?"

It is:

> **"When does the agent + deterministic tools perform better than directly prompting an LLM?"**

That is one of the main engineering questions behind SentinelTrace.

---

## Phase 6 — Threat intelligence and optional RAG

Only after the core investigator works.

Threat intelligence can enrich suspicious IP addresses using permitted APIs.

Possible future RAG material:

- corporate VPN ranges,
- authentication policies,
- known false-positive patterns,
- incident-response runbooks,
- previous synthetic investigation reports.

RAG should provide **organizational context**, not generic cybersecurity knowledge that the LLM already broadly understands.

---

## Phase 7 — API and Docker

Once the local investigator is stable:

- expose the investigation service with FastAPI,
- containerize it with Docker,
- keep domain logic independent from the HTTP layer.

Example future endpoint:

```text
POST /investigations
```

with input such as:

```json
{
  "user_id": "john@company.com",
  "around": "2026-09-17T03:15:00Z"
}
```

---

## Phase 8 — Cheap cloud deployment

Deployment is a learning goal, but not an early requirement.

A small deployment may eventually use:

```text
Client
  |
API Gateway (optional)
  |
AWS Lambda
  |
  +--> S3
  +--> LLM API / Bedrock
  +--> Threat Intelligence API
  |
CloudWatch
```

The project should prefer serverless/on-demand infrastructure over permanently running services.

Cloud resources should be added only after the application works locally.

---

# First milestone

The first meaningful milestone contains **no GenAI**.

Given a suspicious user and time window, Python should deterministically find:

- repeated failed logins,
- relevant source IPs,
- a subsequent successful login,
- whether the IP is new,
- whether the country is new,
- whether the device is new,
- and suspicious post-login activity.

For example:

```text
$ sentinel investigate --user john@company.com

=== SentinelTrace Investigation ===

Window:
2026-09-17 03:00 → 04:00 UTC

Authentication
--------------
Failed attempts: 47
Primary source IP: 185.23.10.12
Successful login afterwards: yes

Baseline comparison
-------------------
Previously seen IP: no
Previously seen country: no
Previously seen device: no

Post-login activity
-------------------
03:21 /admin/customers
```

Once this works reliably and is tested, adding an LLM becomes valuable.

---

# Recommended first coding session

Do not try to build the entire system immediately.

A good first session is:

1. Create the repository.
2. Initialize the Python project with `uv`.
3. Add `pandas`, `pydantic`, `pytest`, and `ruff`.
4. Create the initial package folders.
5. Define `SecurityEvent`.
6. Write a small synthetic authentication-log generator.
7. Generate normal activity plus **one known suspicious scenario**.
8. Implement `load_events()`.
9. Implement `get_user_events()`.
10. Implement `get_failed_logins()`.
11. Implement `build_timeline()`.
12. Write unit tests.
13. Run the investigation manually from Python.

If this works, the session was successful.

Do not add LangGraph, RAG, Docker, AWS, or a database yet.

---

# Learning rules

Because this repository is intended to improve Python and GenAI engineering skills, **how the project is built matters**.

## Write the important Python yourself

For core logic, first attempt the implementation manually.

Useful places to practise include:

- filtering DataFrames,
- manipulating timestamps,
- validating schemas,
- computing baselines,
- building timelines,
- defining clean function interfaces,
- handling errors,
- writing tests.

AI can be used for:

- explanations,
- hints,
- architecture discussion,
- debugging,
- code review,
- test suggestions,
- documentation.

Avoid asking AI to generate the entire project in one step.

---

## Understand abstractions before adding frameworks

Before adding LangGraph, understand the manual agent loop.

Before adding a database, understand why CSV/in-memory storage is insufficient.

Before adding async Python, identify real concurrent I/O that benefits from it.

Before adding RAG, identify information the model genuinely needs to retrieve.

Before adding cloud infrastructure, make the system work locally.

---

## Prefer simple implementations

When choosing between:

```text
simple function
```

and

```text
factory + abstract base class + registry + dependency container
```

prefer the simple function until complexity actually requires something more sophisticated.

The goal is not to demonstrate the maximum number of design patterns.

The goal is to understand the system deeply.

---

# Evidence model

Final claims should eventually reference concrete evidence.

A future finding might look like:

```python
Finding(
    statement="Successful login followed repeated failures from the same IP",
    severity="high",
    evidence_ids=["evt-8161", "evt-8168"],
    confidence=0.91,
    status="supported",
)
```

Important rules:

- numerical facts come from Python/tool results,
- claims should cite evidence IDs,
- external intelligence should cite its source,
- missing information must remain unknown,
- threat-intelligence reputation is a signal, not proof,
- anomaly scores are signals, not proof,
- the final report should distinguish fact, inference, uncertainty, and recommendation.

---

# Testing philosophy

Deterministic components should be independently testable without an LLM.

Examples:

```text
test_load_events_parses_timestamps

test_get_failed_logins_returns_only_failures

test_get_user_events_filters_correct_user

test_timeline_is_chronological

test_baseline_detects_new_country

test_ip_usage_finds_multiple_targeted_users
```

LLM behaviour should be evaluated separately from deterministic correctness.

This separation makes debugging much easier.

---

# Cost philosophy

The project should be effectively free during most development.

Preferred approach:

```text
Local Python              free
Synthetic datasets         free
Pandas / Pydantic          free
pytest / Ruff              free
Docker                     free
GitHub                     free within normal usage
Ollama                     local compute only
Hosted LLM                 only when useful
Threat-intelligence APIs   free tier where permitted
AWS                        small/demo deployments only
```

Avoid always-on cloud infrastructure during development.

Set usage/budget limits before experimenting with paid model or cloud services.

---

# Security and ethics

SentinelTrace is a defensive project.

Use only:

- synthetic data,
- public-safe datasets,
- anonymized data,
- or data you are explicitly authorized to analyze.

Do not add capabilities for:

- credential attacks,
- exploit execution,
- persistence,
- evasion,
- malware deployment,
- destructive remediation.

Do not upload real employer telemetry, credentials, confidential logs, or personal information to public model APIs.

---

# Definition of done

SentinelTrace is portfolio-ready when:

- a clean clone can be installed and run from documented commands,
- several synthetic incidents exist with known ground truth,
- core log-analysis tools are deterministic and unit-tested,
- the agent autonomously selects useful tools,
- investigations are bounded by stopping rules,
- final findings reference concrete evidence,
- the system is evaluated against a direct-LLM baseline,
- latency and approximate model cost are reported,
- the application is containerized,
- at least one inexpensive cloud deployment has been demonstrated,
- and the architecture and trade-offs can be explained without relying on generated explanations.

---

# Suggested development roadmap

```text
Phase 0
Python setup
    ↓
Phase 1
Deterministic log engine
    ↓
Phase 2
Manual investigator
    ↓
Phase 3
Basic LLM tool calling
    ↓
Phase 4
LangGraph agent
    ↓
Phase 5
Evaluation
    ↓
Phase 6
Threat intelligence / RAG
    ↓
Phase 7
FastAPI + Docker
    ↓
Phase 8
Cheap AWS deployment
    ↓
Phase 9 (optional)
ML anomaly detection
```

The project is already valuable after Phase 5.

Everything after that should be treated as an extension rather than a requirement for proving the main idea.

---

# Possible future extensions

Only after the core project is complete:

- Isolation Forest or another simple anomaly detector
- RAG over security policies and known VPN ranges
- parallel threat-intelligence enrichment with `asyncio`
- PostgreSQL / pgvector
- SQS-based asynchronous investigations
- Bedrock model provider
- OpenTelemetry tracing
- small Streamlit interface
- additional event types such as API-key abuse or privilege changes

These are stretch goals, not starting requirements.

---

# Final project story

The central question behind SentinelTrace is:

> **Can a tool-using AI investigator produce more accurate, traceable, and efficient security investigations than simply giving logs directly to an LLM?**

The project answers that question by building:

1. deterministic Python analysis tools,
2. a manual investigation workflow,
3. an LLM capable of choosing those tools,
4. a bounded LangGraph investigation loop,
5. evidence-backed reports,
6. and an evaluation against a simpler direct-LLM baseline.

That progression is intentional.

The strongest version of SentinelTrace is not the version with the most agents, AWS services, databases, frameworks, or dashboards.

It is the version where every component has a clear reason to exist, the important Python code is understood, and there is evidence that the agent actually improves the investigation workflow.
