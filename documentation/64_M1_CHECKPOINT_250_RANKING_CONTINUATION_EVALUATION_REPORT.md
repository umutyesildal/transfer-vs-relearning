# 64 - M1 Checkpoint-250 Ranking Continuation Evaluation Report

Last updated: 2026-07-11

## Status

The first preselected external evaluation wave completed without runtime errors. No
checkpoint passed the gate, and metrics worsened after checkpoint 35. Later checkpoints are
not being evaluated.

## Evaluated Checkpoints

- checkpoint 35: job `391088`;
- checkpoint 70: job `391089`;
- checkpoint 105: job `391090`.

Each job evaluates the same 500 English facts under three views:

1. exact-prefix;
2. held-out direct;
3. QA-matched.

All three jobs entered the running state on `gruenau9`, each with one A100 80GB. Startup
logs show the correct ranking-continuation model manifests and no errors.

## Results

| Checkpoint | Exact | Direct | QA | D/QA overlap | Triple robust | Mean ranks E/D/Q | Gate |
|---|---:|---:|---:|---:|---:|---|---|
| baseline cp250 | 451 | 317 | 349 | 277 | 265 | 1.27 / 3.64 / 2.40 | fail |
| ranking cp35 | 452 | 321 | 343 | 277 | 264 | 1.24 / 3.59 / 2.45 | fail |
| ranking cp70 | 450 | 317 | 345 | 275 | 262 | 1.27 / 3.60 / 2.44 | fail |
| ranking cp105 | 451 | 315 | 340 | 268 | 256 | 1.27 / 3.62 / 2.46 | fail |

Checkpoint 35 gives a four-fact direct improvement but loses six QA facts and one
triple-robust fact. The direct/QA overlap does not improve. Checkpoints 70 and 105 regress
further, so the continuation curve does not justify later evaluation.

## Checkpoint-35 Relation Audit

| Relation | Exact | Direct | QA | Triple robust | Baseline triple |
|---|---:|---:|---:|---:|---:|
| `profession` | 100 | 90 | 90 | 84 | 85 |
| `born_in` | 100 | 65 | 67 | 54 | 53 |
| `lives_in` | 100 | 77 | 86 | 73 | 74 |
| `studied_at` | 82 | 47 | 54 | 29 | 29 |
| `works_at` | 70 | 42 | 46 | 24 | 24 |

The two targeted weak relations show no triple-robust improvement.

Candidate collapse also remains:

- `studied_at` direct: `19 Mayis Universitesi` in 48 failures;
- `studied_at` QA: `19 Mayis Universitesi` in 43 failures;
- `works_at` direct: `3M` in 45 failures;
- `works_at` QA: `3M` in 51 failures.

Balanced negative coverage by itself therefore did not remove the relation-level prior.

## Timing

- expected average: approximately 6 minutes;
- safe range: 6-9 minutes;
- no local sleep monitor is active.

## Decision Contract

The unchanged gate is:

- exact-prefix at least 450/500;
- held-out direct at least 400/500;
- QA-matched at least 400/500;
- direct/QA overlap at least 350/500.

## Final Decision

Do not promote the ranking continuation. Do not evaluate checkpoints 140-350. The best
analysis checkpoint remains the original acquisition checkpoint 250 with 265/500 strict
triple-robust facts. The 2,500-fact scale-up remains blocked.

This result rejects the tested hypothesis in its current form: a low-LR continuation with 15
deterministic balanced negatives does not materially strengthen subject-object binding after
acquisition. The next intervention must change more than negative coverage or continued
exposure.
