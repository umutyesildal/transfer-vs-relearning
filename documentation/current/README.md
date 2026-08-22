# Current control plane

This directory is the small live entrypoint for humans and agents.

- [`START_HERE.md`](START_HERE.md) is the default agent reading router.
- [`AGENT_BRIEF.yaml`](AGENT_BRIEF.yaml) is the small hash-bound current projection.
- [`READING_PROFILE.yaml`](READING_PROFILE.yaml) classifies default and retired reads.
- [`PROJECT_STATE.yaml`](PROJECT_STATE.yaml) is the canonical machine-readable state.
- [`STATUS.md`](STATUS.md) explains that state for humans.
- [`AUTHORITY.md`](AUTHORITY.md) defines which additional files a task must read.
- [`ROADMAP.md`](ROADMAP.md) orders future work without authorizing it.

Agents read the brief by default; scientific/external execution must also read the full state.
Exact run rows, logs and long history belong in manifests, contracts, decisions, or records.
