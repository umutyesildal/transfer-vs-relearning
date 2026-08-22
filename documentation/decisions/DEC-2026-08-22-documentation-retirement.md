# Documentation Retirement and Agent Reading Boundary

**Status:** accepted

**Date:** 2026-08-22

## Decision

The chronological Markdown record is preserved in place but retired from the default agent reading
set. Retirement means “do not read unless a current task cites it”; it does not mean deletion,
rewriting, loss of authority metadata, or removal from Git history.

The default agent context is now:

1. root `AGENTS.md`;
2. `documentation/current/START_HERE.md`;
3. `documentation/current/AGENT_BRIEF.yaml`;
4. the user's current instruction or one bounded task packet.

The full `documentation/current/PROJECT_STATE.yaml` remains the canonical machine ledger. It is
required for scientific/external execution, authority disputes, or when the brief explicitly
points to a detailed ledger entry. The brief is a hash-bound projection and may not contradict or
expand the full state.

## Default-retired material

- root `LUNA_WORKER_CURRENT_HANDOFF.md`;
- `documentation/00_DOCUMENTATION_INDEX.md`;
- `documentation/01_PROJECT_STATUS_AND_NEXT_STEPS.md`;
- `documentation/02_AGENT_ROSTER.md`;
- `documentation/03_INITIAL_AGENT_REPORTS.md`;
- `documentation/PROJECT_HANDOFF_AND_COMPLETE_PROGRESS_OVERVIEW.md`;
- all root-level numbered `documentation/*.md` records;
- `.agents/task-packets/study-v1/` after the eval-v2 packet set is generated.

These remain available for targeted historical investigation. Their old claims never override the
current brief, full state, active contract, or current user instruction.

## Safety and verification

- no Markdown record is deleted or physically moved;
- retired gateway files receive a short top-of-file retirement banner while their prior bodies are
  preserved;
- `documentation/current/READING_PROFILE.yaml` is the machine-readable routing policy;
- tests verify that the default set is small, contains no numbered document or legacy handoff, and
  that the brief matches selected full-state fields;
- task packets are versioned by study protocol so stale eval-v1 packets cannot be mistaken for the
  active eval-v2 packet set.

## Consequence

A new agent can begin with a few small files and load historical evidence only by citation. This
reduces context drift without erasing failed runs, superseded contracts, paper notes, or scientific
provenance.
