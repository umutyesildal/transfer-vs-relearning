# 55 - M1 Born-In 10-Fact Direct-Supervision Report

Last updated: 2026-07-11

## Outcome

The 10-fact `born_in` direct-aware control passed the precommitted progression gate. From
checkpoint 50 onward, all ten facts rank first in exact-prefix, held-out direct, and held-out
QA evaluation.

## Reproducible Setup

- implementation commit: `6ea6136`
- subjects: 10
- relation: `born_in`
- facts: 10
- train rows: 70
- rows per fact: 7
- held-out direct validation rows: 10
- model: base SmolLM2-360M
- objective: answer-only
- epochs: 36
- batch size: 10
- optimizer steps: 252
- learning rate: `1e-4`
- scheduler: constant with warmup
- weight decay: 0

The run starts from the base model. It does not continue from the successful single-fact
checkpoint.

## Training Run

- Slurm job: `391048`
- node: `gruenau9`
- GPU: one A100 80GB
- runtime: 116.8 seconds
- aggregate train loss: 0.2865
- final held-out direct eval loss: approximately `6.14e-04`
- status: completed successfully

Run directory:

```text
runs/training/m1_smollm2_360m_diagnostic_born_in_10_direct_answer_only/
20260711T062145Z_m1_smollm2_360m_diagnostic_born_in_10_direct_answer_only_lr1e-4_ep36_8638408b
```

## Evaluation

- jobs: `391049` through `391059`
- views per checkpoint: exact prefix, held-out direct, held-out QA matched
- candidate inventory: complete city inventory
- all jobs completed without errors

## Checkpoint Results

Counts are top-1 facts out of ten. `Overlap` is the direct/QA top-1 intersection.

| Checkpoint | Exact | Direct | QA | Overlap | Mean ranks E/D/Q | Gate |
|---|---:|---:|---:|---:|---|---|
| 25 | 7 | 6 | 6 | 6 | 5.2 / 8.5 / 8.6 | fail |
| 50 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 75 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 100 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 125 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 150 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 175 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 200 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 225 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 250 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |
| 252 | 10 | 10 | 10 | 10 | 1.0 / 1.0 / 1.0 | pass |

Earliest passing checkpoint: `checkpoint-50`.

Precommitted gate:

- exact at least 9/10;
- direct at least 8/10;
- QA at least 8/10;
- direct/QA overlap at least 7/10.

## Interpretation

The direct-aware format mix scales from one to ten bindings within one relation. The model
requires more than 25 updates to resolve all ten facts, but by checkpoint 50 all three probe
formats reach perfect top-1 retrieval and remain stable through the end of training.

This rules out the following explanations for the earlier 50-fact failure:

- the 360M model cannot store more than one synthetic binding;
- answer-only loss is inherently incompatible with candidate ranking;
- direct paraphrase generalization works only for a single memorized example.

The remaining scale question is relation diversity and 50 simultaneous bindings. The next
controlled level should use the same direct-aware seven-row contract for all five relations
across the same ten subjects, starting from the base model. It must retain held-out direct
paraphrases and the full relation-specific candidate inventories.

