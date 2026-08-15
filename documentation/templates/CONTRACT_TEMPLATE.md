# <Contract name and version>

**Status:** `draft` | **Owner:** `<owner>` | **Created:** YYYY-MM-DD
**Supersedes:** none

## Purpose and estimand

State the exact question and comparison.

## Scope and prohibitions

List allowed and forbidden actions. State explicitly that preparation does not grant execution
authority.

## Immutable identities

Record code commit, model/tokenizer revisions, datasets/corpora, task implementation revisions,
environment/lock identity, seeds, and input hashes.

## Protocol

Freeze preprocessing, objective, budgets, prompts, metrics, aggregation, checkpoint grid, and
comparison matching.

## Inputs, outputs, and schemas

Define fresh namespaces, file schemas, manifest fields, retention classes, and atomic-write rules.

## Gates and missingness

Define metric direction, denominator, threshold, uncertainty, failure classes, partial output
handling, and `NOT_RUN` semantics.

## Preflight, resume, and rollback

Define identity/storage/runtime checks, idempotency, allowed resume behavior, and preservation.

## Verification

List exact tests and completion evidence.

## Authority boundary

State the exact separate authorization required and actions this document does not authorize.

## Change policy

Identify which changes require a new version and which implementation-only corrections may be
append-only.
