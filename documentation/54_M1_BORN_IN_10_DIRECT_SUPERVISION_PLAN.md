# 54 - M1 Born-In 10-Fact Direct-Supervision Plan

Last updated: 2026-07-10

## Decision

The direct-aware single-fact control passed exact, direct, and QA evaluation from its first
checkpoint. The next level tests whether the same format coverage works across ten distinct
bindings without introducing relation interference.

## Controlled Scope

- subjects: the same 10 diagnostic subjects
- relation: `born_in` only
- facts: 10
- candidates: complete city inventory
- model: base SmolLM2-360M, not the single-fact checkpoint
- rows per fact: 7
- total train rows: 70
- held-out direct rows: 10

Each fact has three declarative, two QA, and two direct-format training rows. Its held-out
direct paraphrase is absent from training.

## Matched Budget

- epochs: 36
- batch size: 10
- optimizer steps: 252
- learning rate: `1e-4`
- scheduler: constant with warmup
- answer-only loss
- no weight decay

This preserves the single-fact direct-aware run's optimizer-update count and per-row exposure
while increasing the number of bindings from one to ten.

## Precommitted Gate

A checkpoint passes only if all conditions hold:

- exact-prefix top-1 at least 9/10;
- held-out direct top-1 at least 8/10;
- held-out QA top-1 at least 8/10;
- direct/QA top-1 overlap at least 7/10.

Select the earliest passing checkpoint. Do not launch the 50-fact or 100-subject levels if
no checkpoint passes.

Interpretation:

- pass: format-aware extraction scales within one relation; next test the five-relation
  50-fact diagnostic with the same format contract;
- exact succeeds but direct/QA fail: extraction interference appears as bindings increase;
- exact also fails: storage capacity or optimization interference appears by ten bindings.

## Implementation Status

Local implementation completed on 2026-07-10.

- commit: `6ea6136` (`Add ten-fact direct-supervision control`)
- generated train rows: 70
- generated held-out validation rows: 10
- facts: 10 distinct `born_in` bindings
- rows per fact: 7
- expected optimizer steps: 252
- local full test suite: passed
- shell helper syntax checks: passed

The initial GitHub push request was rejected by the Codex external execution service because
its usage window was exhausted until 2026-07-11 03:23 CEST. Execution resumed afterward:

- push: successful;
- HU pull/build/tests: successful;
- training job: `391048`, completed;
- evaluation jobs: `391049` through `391059`, completed;
- gate: passed from checkpoint 50 onward.

See `55_M1_BORN_IN_10_DIRECT_SUPERVISION_REPORT.md` for final metrics.
