# 74 - M1 Relation V2 500-Fact Scale Plan

Last updated: 2026-07-12

## Decision

Scale the accepted clean Relation V2 direct-aware acquisition recipe to 100 subjects and 500
facts. Do not carry either the failed paired-city CLM control or the metric-neutral hard-negative
continuation into this run.

## Frozen Relations

- `profession`;
- `born_in`;
- `lives_in`;
- `field_of_study`;
- `works_in_industry`.

`born_in` and `lives_in` are permanent and continue sharing the complete city inventory. Their
confusion is an intended relation-binding diagnostic, not a reason for replacement.

## Dataset Contract

- subjects: 100;
- facts: 500;
- facts per relation: 100;
- train rows per fact: 7;
- train rows: 3,500;
- composition per fact: three declarative, two QA, two scaffold-free direct;
- held-out QA rows: 500;
- exact-prefix probes: 500;
- selection seed: 42;
- nesting: all ten subjects from the completed 50-fact gate must be included;
- branch/name allocation: 25 subjects in each branch x name-type cell;
- historical `studied_at` and `works_at`: absent.

## Matched Training Budget

- base model: SmolLM2-360M;
- start: base model, not a 10-subject checkpoint;
- objective: answer-only CLM;
- learning rate: `1e-4`;
- epochs: 36;
- micro-batch: 50;
- gradient accumulation: 10;
- effective batch: 500;
- optimizer updates: 252;
- scheduler: constant with warmup;
- weight decay: 0;
- checkpoint interval: 25 updates.

This preserves 36 exposures per row and the 252-update budget used at the 50-fact level.

## Precommitted Aggregate Gate

- exact-prefix top-1 at least 450/500;
- held-out direct top-1 at least 400/500;
- held-out QA top-1 at least 400/500;
- direct/QA overlap at least 350/500.

Evaluate checkpoints 25, 50, and 75 first. Continue the checkpoint wave only if the curve is
still improving or a gate boundary is plausible. Report every relation separately, including
both directions of same-subject city swaps. City confusion remains visible but does not authorize
relation removal or substitution.

## Implementation And Launch

- synthetic-data-generation commit: `b33aa8b`;
- transfer-vs-relearning commit: `062a90a`;
- synthetic full suite: 58/58 passed;
- transfer focused local suite: 37/37 passed;
- HU focused preflight: 37/37 passed;
- nesting audit: passed;
- Slurm training job: `391918`;
- initial state: `PENDING`;
- resource: one A100 80GB;
- expected runtime: approximately ten minutes, safe range eight to fifteen minutes;
- monitoring: no sleep process is active.

Frozen hashes:

```text
1314417fe8a01afa6e1d7efbf18db082e7ca039dbab2acd0bece0b6fd2f20ff0  train.jsonl
9b1fcae2565fbf0d9c624a2c229c8173a59ca00064db1a017b0f2a5c0c749289  validation.jsonl
1644288d0d62c51c56ceaae71b9eef7225b88326267281c8df8aeef9d7619c8e  exact_prefix_probes_en.csv
```

## Training Result And Initial Evaluation Wave

Training job `391918` completed successfully:

- optimizer updates: 252/252;
- runtime: 575.4 seconds (9.6 minutes);
- aggregate training loss: 0.6418;
- final held-out validation loss: 0.3910;
- OOM/runtime errors: none;
- canonical run timestamp: `20260712T082510Z`.

The precommitted first checkpoint wave was submitted:

| Checkpoint | Evaluation job | Initial state |
| ---: | ---: | --- |
| 25 | 391922 | RUNNING |
| 50 | 391923 | RUNNING |
| 75 | 391924 | PENDING |

Each job evaluates 500 exact-prefix, 500 held-out direct, and 500 QA-matched probes. Expected
parallel wall time is approximately six minutes, with a safe six-to-nine minute range including
queue delay. No sleep monitor is active.

## Initial Checkpoint Results

All three initial evaluation jobs completed without failures:

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 25 | 21 | 21 | 20 | 11 | 6 | fail |
| 50 | 79 | 62 | 66 | 42 | 25 | fail |
| 75 | 307 | 224 | 234 | 176 | 148 | fail |

The curve is far below the final gate at checkpoint 75 but is rising sharply, especially exact
storage (21 to 79 to 307) and direct/QA overlap (11 to 42 to 176). Under the precommitted rule,
the next checkpoint wave is warranted. The nested original ten subjects reach 29 exact, 24 direct,
23 QA, 18 overlap, and 15 triple at checkpoint 75; this is an interim scale-interference measure,
not a final regression decision.

Second-wave jobs:

| Checkpoint | Evaluation job | Initial state |
| ---: | ---: | --- |
| 100 | 391930 | PENDING |
| 125 | 391931 | PENDING |
| 150 | 391932 | PENDING |

Expected parallel wall time remains approximately six minutes, with a safe six-to-nine minute
range. No sleep monitor is active.

## Late Checkpoint Results

Jobs `391937` through `391939` completed without evaluation failures:

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 175 | 500 | 377 | 373 | 326 | 326 | fail |
| 200 | 500 | 374 | 374 | 325 | 325 | fail |
| 225 | 500 | 377 | 375 | 328 | 328 | fail |

Checkpoint 225 is the strongest result so far. Its relation-level triple counts are profession
97, born_in 69, lives_in 43, field_of_study 78, and works_in_industry 41. Exact storage remains
perfect, while direct/QA overlap is 22 facts below the 350 progression threshold.

The final checkpoint-250/252 evaluation launcher is prepared locally. Its first submit attempt
did not execute because the Codex external-action usage limit was reached; no final evaluation
job IDs were created. The final gate decision remains pending those two checkpoints. No sleep
monitor is active.

After the limit cleared, checkpoint 250 and 252 were submitted as jobs `392003` and `392004`.
Both were initially `PENDING`. Expected parallel wall time is approximately six minutes, with a
safe six-to-nine minute range. No sleep monitor is active.

Both final jobs completed without evaluation failures. Checkpoint 250 reached 500 exact, 378
direct, 377 QA, and 329 overlap/triple; checkpoint 252 reached 500/377/373/328/328. Checkpoint 250
is the final analysis checkpoint. The 450/400/400/350 gate fails by 0/22/23/21 facts, so 2,500-fact
scaling is blocked. Full results are in `75_M1_RELATION_V2_500_FACT_EVALUATION_REPORT.md`.

## Middle Checkpoint Results

Jobs `391930` through `391932` completed without evaluation failures:

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 100 | 475 | 333 | 340 | 283 | 277 | fail |
| 125 | 500 | 375 | 367 | 324 | 324 | fail |
| 150 | 500 | 371 | 369 | 320 | 320 | fail |

Storage reaches 500/500 by checkpoint 125. Prompt robustness peaks at checkpoint 125 in this
wave and then changes only slightly. At checkpoint 125, relation-level triple counts are:

```text
profession 97, born_in 67, lives_in 43, field_of_study 78, works_in_industry 39
```

The current gap is therefore extraction/binding rather than storage, concentrated especially in
`lives_in` and `works_in_industry`. A late checkpoint wave is required to distinguish a temporary
plateau from a final one.

| Checkpoint | Evaluation job | Initial state |
| ---: | ---: | --- |
| 175 | 391937 | PENDING |
| 200 | 391938 | PENDING |
| 225 | 391939 | PENDING |

Expected parallel wall time remains approximately six minutes, with a safe six-to-nine minute
range. No sleep monitor is active.
