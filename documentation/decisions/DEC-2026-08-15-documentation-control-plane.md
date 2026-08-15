# DEC-2026-08-15 — Layered documentation control plane

**Status:** `accepted` | **Date:** 2026-08-15
**Owners:** project owner and repository maintainer

## Context

The workspace accumulated 178 chronological scientific documents, a large live `AGENTS.md`, a
stale root README, repeated authority summaries, and a 1,147-line orchestration manual. New agents
had to consume a large historical context before discovering the current gate. Live state,
operating rules, plans, contracts, and evidence were mixed together, increasing stale-context and
silent-authority risks.

At the same time, the complete history is scientifically valuable and must not be discarded or
rewritten.

## Decision

Use a layered documentation control plane:

```text
README.md                              repository map
AGENTS.md                              stable rules
documentation/current/PROJECT_STATE   live machine state
documentation/current/STATUS          live human synthesis
documentation/contracts               prospective frozen protocols
documentation/decisions               durable rationale
documentation/records + numbered docs immutable history/evidence
machine manifests/tables              exact run identity and results
```

The minimum new-agent context is `AGENTS.md`, `PROJECT_STATE.yaml`, and one bounded task packet.
Task-specific contracts and evidence are loaded only when named.

The existing Documents 00–178 remain at their current paths during V1. New routine work will not
extend the global number sequence.

## Alternatives

- Continue expanding `AGENTS.md`: rejected because stable rules and fast-changing state have
  different lifecycles and context costs.
- Replace all numbered documents with a wiki: rejected because it risks link breakage and loss of
  chronological evidence.
- Move every historical file immediately: deferred because safe relocation needs a citation/link
  map and provides little benefit to the active context boundary.
- Use chat history as state: rejected because fresh agents and reproducibility cannot depend on
  inherited conversation memory.

## Consequences

- `AGENTS.md` stays under a tested 250-line budget.
- The live state is explicit, fail-closed, and machine-readable.
- Historical guidance remains byte-identical under `documentation/records/workspace-guidance/`.
- Documentation links, state invariants, context budgets, and preservation hashes are tested.
- Every future state change must update the owning layer rather than copy prose across files.
- Agent prompts and repository snapshots use the single monorepo and micro-context read set.

## Evidence and links

- [`../current/PROJECT_STATE.yaml`](../current/PROJECT_STATE.yaml)
- [`../current/AUTHORITY.md`](../current/AUTHORITY.md)
- [`../records/workspace-guidance/LEGACY_GUIDANCE_MANIFEST.json`](../records/workspace-guidance/LEGACY_GUIDANCE_MANIFEST.json)
- [`../migration/REPOSITORY_MIGRATION_V1.md`](../migration/REPOSITORY_MIGRATION_V1.md)

## Supersession

A later accepted decision may change the layering or physically archive numbered documents. It
must preserve this decision, map old links, verify citations, and update the live state.
