# DEC-2026-08-15 — Publish the monorepo and fast-forward main

**Status:** `accepted` | **Date:** 2026-08-15

## Context

The lossless migration, documentation control plane, generated-output history sanitization, tests,
and remote ancestry checks had passed. The monorepo branch was 247 commits ahead of `origin/main`
and zero commits behind; `origin/main` was its direct ancestor.

## Decision

Publish `migration/monorepo-v1`, fast-forward `main` without a merge commit or force push, and open
`agent/eval-harness` from the resulting main commit for the evaluation-foundation work.

## Consequences

- GitHub `main` is now the canonical monorepo.
- `.agents` is visible and tracked at repository root.
- `.migration` private inventories and recovery bundle remain local-only.
- `migration/monorepo-v1`, `main`, and the initial `agent/eval-harness` branch point at the verified
  cutover commit before this state-alignment follow-up.
- Remote main/eval histories contain zero reachable blobs at or above 10 MiB.
- Future evaluation work belongs on `agent/eval-harness` and still requires a bounded task.

## Evidence

- [`../migration/REPOSITORY_MIGRATION_V1.md`](../migration/REPOSITORY_MIGRATION_V1.md)
- [`../current/PROJECT_STATE.yaml`](../current/PROJECT_STATE.yaml)
- [`../migration/GENERATED_OUTPUT_HISTORY_SANITIZATION.md`](../migration/GENERATED_OUTPUT_HISTORY_SANITIZATION.md)

## Authority boundary

This decision records the completed cutover. It does not create standing authority for additional
pushes, branch deletion, external execution, evaluation, corpus access, or training.
