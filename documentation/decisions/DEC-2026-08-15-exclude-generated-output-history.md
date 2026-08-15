# DEC-2026-08-15 — Exclude generated output paths from monorepo history

**Status:** `accepted` | **Date:** 2026-08-15

## Context

The lossless subtree import preserved generated output files that were already tracked in source
history. A reachable-object audit found eight blobs at or above 10 MiB, totaling 360,973,310 bytes.
Ignore rules protect new files but do not remove existing Git objects.

## Decision

After explicit user approval, filter `output/` and `tools/synthetic-data/output/` from the local
migration branch's complete reachable history. Preserve the exact pre-filter branch as a verified
private Git bundle and retain both original worktrees.

## Consequences

- reachable blobs at or above 10 MiB fall from eight to zero;
- generated output files do not become part of a future monorepo push;
- commit IDs in rewritten history differ from the exact source history;
- topology is not squashed;
- exact pre-filter and source histories remain recoverable outside the sanitized branch;
- push and cutover remain separately unauthorized.

## Evidence

- [`../migration/GENERATED_OUTPUT_HISTORY_SANITIZATION.md`](../migration/GENERATED_OUTPUT_HISTORY_SANITIZATION.md)
- [`../migration/GENERATED_OUTPUT_HISTORY_SANITIZATION.json`](../migration/GENERATED_OUTPUT_HISTORY_SANITIZATION.json)

## Supersession

Any later history or Git LFS rewrite requires a new decision and must preserve or supersede the
documented recovery bundle deliberately.
