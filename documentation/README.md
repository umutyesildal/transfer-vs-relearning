# Documentation

This directory separates live state, future contracts, durable decisions, and historical evidence
so agents do not need to load the complete project history for every task.

## Read by purpose

| Need | Read |
|---|---|
| Current human summary | [`current/STATUS.md`](current/STATUS.md) |
| Machine-readable current state | [`current/PROJECT_STATE.yaml`](current/PROJECT_STATE.yaml) |
| Authority and minimum reading set | [`current/AUTHORITY.md`](current/AUTHORITY.md) |
| Ordered next work | [`current/ROADMAP.md`](current/ROADMAP.md) |
| Prospective protocol/execution rules | [`contracts/README.md`](contracts/README.md) |
| Durable rationale | [`decisions/README.md`](decisions/README.md) |
| Historical/scientific evidence | [`records/README.md`](records/README.md) and numbered docs |
| Repository migration evidence | [`migration/REPOSITORY_MIGRATION_V1.md`](migration/REPOSITORY_MIGRATION_V1.md) |

## Existing numbered documents

Documents 00–178 remain in this directory at their existing paths. They are the chronological
scientific record and include failures, superseded contracts, results, and corrections. They are
not the default onboarding set.

No new routine progress report should extend the global number sequence. New information belongs
in the live state, a scoped contract, a decision record, or an immutable result artifact.

## Update rule

Change only the owning layer:

- state changed → `current/PROJECT_STATE.yaml` and, if human-relevant, `current/STATUS.md`;
- future protocol changed → a versioned contract;
- rationale changed → a decision record;
- a wave completed → immutable result manifest/report, then update current state;
- an old statement was wrong → append-only correction or new superseding record.

Avoid copying the same status paragraph across several Markdown files.
