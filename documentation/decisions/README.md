# Decisions

Decision records capture durable “why” without becoming run logs.

## Naming and status

Use:

```text
DEC-YYYY-MM-DD-short-slug.md
```

Each record has one status: `proposed`, `accepted`, `superseded`, or `rejected`. If a decision is
replaced, preserve it and link both directions.

## Appropriate decisions

- why the repository uses a monorepo;
- why one evaluation metric is primary and another is sensitivity-only;
- why M2-A/M2-B use a matched replacement design;
- why a result schema or artifact retention class was chosen;
- why a protocol change requires `eval-v2`.

Run IDs, job progress, large evidence tables, and temporary plans do not belong here. Use an
immutable result record, current state, or a task plan instead.

Use [`../templates/DECISION_TEMPLATE.md`](../templates/DECISION_TEMPLATE.md).

## Current decisions

- [`DEC-2026-08-15-hybrid-evaluation-architecture.md`](DEC-2026-08-15-hybrid-evaluation-architecture.md)
  keeps standard harness tasks, project factual estimands and normalization as separate lanes.
