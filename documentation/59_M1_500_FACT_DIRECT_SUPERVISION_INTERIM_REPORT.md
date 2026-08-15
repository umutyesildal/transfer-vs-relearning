# 59 - M1 500-Fact Direct-Supervision Interim And Final Report

Last updated: 2026-07-11

## Current Status

The 500-fact training and all precommitted checkpoint evaluations completed successfully.
Exact-prefix storage reached the required threshold, but held-out direct and QA extraction
plateaued below their thresholds. The complete 500-fact progression gate therefore failed,
and the 2,500-fact scale-up is blocked under the frozen roadmap.

## Reproducible Setup

- implementation commit: `bfc8d9b`
- subjects: 100
- facts: 500
- train rows: 3,500
- held-out direct rows: 500
- rows per fact: 7
- micro-batch: 50
- gradient accumulation: 10
- effective batch: 500
- epochs: 36
- optimizer updates: 252
- base model: SmolLM2-360M
- objective: answer-only

## Training Run

- Slurm job: `391072`
- node: `gruenau9`
- GPU: one A100 80GB
- runtime: 604.3 seconds
- aggregate train loss: 0.5019
- final held-out direct eval loss: approximately 0.2281
- status: completed without OOM or runtime errors

Run directory:

```text
runs/training/m1_smollm2_360m_acquisition_100_subjects_500_facts_direct/
20260711T070338Z_m1_smollm2_360m_acquisition_100_subjects_500_facts_direct_lr1e-4_ep36_15b8eecb
```

## Initial Evaluation Wave

- checkpoint 25: job `391073`
- checkpoint 50: job `391074`
- checkpoint 75: job `391075`
- status: all completed without errors

| Checkpoint | Exact | Direct | QA | Overlap | Mean ranks E/D/Q | Gate |
|---|---:|---:|---:|---:|---|---|
| 25 | 15 | 15 | 16 | 11 | 56.61 / 55.73 / 55.23 | fail |
| 50 | 44 | 35 | 38 | 29 | 27.10 / 31.15 / 29.85 | fail |
| 75 | 197 | 149 | 143 | 106 | 6.98 / 12.61 / 10.97 | fail |

The gate is 450 exact, 400 direct, 400 QA, and 350 overlap. No initial checkpoint passes.

Checkpoint 75 relation-level top-1 counts:

| Relation | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| `profession` | 67 | 50 | 53 | 42 |
| `born_in` | 34 | 30 | 25 | 18 |
| `lives_in` | 47 | 33 | 34 | 24 |
| `studied_at` | 21 | 15 | 16 | 9 |
| `works_at` | 28 | 21 | 15 | 13 |

The curve is strongly increasing rather than flat, so checkpoint 75 does not establish a
final failure. Profession learns fastest; studied-at and works-at lag.

## Second Evaluation Wave

Submitted and completed without errors:

- checkpoint 100: job `391076`
- checkpoint 125: job `391077`
- checkpoint 150: job `391078`
- node: `gruenau9`, one A100 80GB per job

| Checkpoint | Exact | Direct | QA | Overlap | Mean ranks E/D/Q | Gate |
|---|---:|---:|---:|---:|---|---|
| 100 | 407 | 256 | 267 | 201 | 1.58 / 5.61 / 3.95 | fail |
| 125 | 445 | 298 | 313 | 246 | 1.33 / 4.13 / 2.72 | fail |
| 150 | 444 | 315 | 337 | 266 | 1.27 / 3.75 / 2.52 | fail |

At checkpoint 150, exact storage is near the 450/500 gate. Direct and QA extraction continue
to improve but remain below 400/500. Profession is strongest; studied-at and works-at remain
the slowest relations.

## Third Evaluation Wave

Submitted:

- checkpoint 175: job `391079`, initially running;
- checkpoint 200: job `391080`, initially pending;
- checkpoint 225: job `391081`, initially pending.

Expected wall-clock duration based on the completed 500-fact waves:

- average: approximately 6 minutes;
- safe range: 6-8 minutes;
- jobs run in parallel when all three A100s are allocated.

The second queue confirmation was unavailable because the external execution usage window
was exhausted until 13:18 CEST. No workaround or sleep monitor was started.

## Third Wave Results

Jobs `391079` through `391081` completed without runtime errors.

| Checkpoint | Exact | Direct | QA | Overlap | Mean ranks E/D/Q | Gate |
|---|---:|---:|---:|---:|---|---|
| 175 | 449 | 315 | 338 | 272 | 1.26 / 3.70 / 2.51 | fail |
| 200 | 450 | 318 | 338 | 273 | 1.27 / 3.65 / 2.50 | fail |
| 225 | 451 | 320 | 337 | 274 | 1.25 / 3.68 / 2.50 | fail |

Exact storage reaches its 450/500 gate at checkpoint 200. Direct, QA, and overlap remain
below gate and are nearly flat from checkpoint 150 through 225. The strongest relations are
profession and the two city relations; studied-at and works-at remain the main bottlenecks.

## Final Checkpoint Wave

Per the roadmap, only the final checkpoints were submitted and completed:

- checkpoint 250: job `391083`;
- checkpoint 252: job `391084`.

Expected duration:

- average: approximately 6 minutes;
- safe range: 6-8 minutes.

Both jobs ran on `gruenau9` with one A100 80GB each and completed without runtime errors.
The stderr logs contain only the non-fatal Transformers `torch_dtype` deprecation warning.

| Checkpoint | Exact | Direct | QA | Overlap | Mean ranks E/D/Q | Gate |
|---|---:|---:|---:|---:|---|---|
| 250 | 451 | 317 | 349 | 277 | 1.27 / 3.64 / 2.40 | fail |
| 252 | 450 | 320 | 344 | 276 | 1.26 / 3.64 / 2.46 | fail |

Checkpoint 250 has the best robust overlap and QA score. Checkpoint 252 has the best direct
score, but neither checkpoint passes the complete gate.

Checkpoint 250 relation-level top-1 counts:

| Relation | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| `born_in` | 100 | 64 | 67 | 53 |
| `lives_in` | 100 | 77 | 87 | 74 |
| `profession` | 100 | 90 | 92 | 85 |
| `studied_at` | 82 | 47 | 56 | 36 |
| `works_at` | 69 | 39 | 47 | 29 |

## Final Decision

The precommitted gate was 450 exact, 400 direct, 400 QA, and 350 direct/QA overlap. The
earliest exact-prefix pass was checkpoint 200, but no checkpoint passed all four conditions.
The curve from checkpoint 150 through 252 is effectively flat for direct, QA, and overlap,
so additional checkpoints or unchanged exposure are not justified.

Interpretation:

- the recipe can store most of the 500 facts in an exact-prefix context;
- the remaining failure is prompt-robust extraction and relation binding at this scale;
- `profession` is robust, while `studied_at` and `works_at` are the dominant bottlenecks;
- the result is a major improvement over the historical 5/500 robust-overlap baseline, but
  it is not sufficient to promote this recipe to the 2,500-fact level.

Action:

- do not launch the 2,500-fact run;
- retain checkpoint 250 as the analysis checkpoint because it has the highest final robust
  overlap and QA score;
- retain the frozen and audited checkpoint-250 triple-robust subset as the analysis set;
- design the next controlled 500-fact intervention around prompt transfer and the two weak
  relations before reconsidering scale-up.

The completed triple-robust freeze contains 265/500 facts. The difference from the 277/500
direct/QA overlap is 12 facts that pass both held-out prompt views but fail exact-prefix rank
1. Full balance, leakage, relation, and candidate-collapse results are recorded in
`61_M1_CHECKPOINT_250_TRIPLE_ROBUST_AUDIT.md`.

Per the updated user-requested operations protocol, no sleep command is active. Jobs are left
to Slurm and will be inspected when the user next requests a status update.

The wave is now summarized. The 2,500-fact level remains blocked because the gate failed.
