# 57 - M1 All-Relations 50-Fact Direct-Supervision Report

Last updated: 2026-07-11

## Outcome

The five-relation, 50-fact direct-aware control passed the precommitted progression gate at
checkpoint 50. At checkpoint 75 it reached 50/50 exact, 48/50 direct, 49/50 QA, and 48/50
direct/QA overlap.

## Reproducible Setup

- implementation commit: `845c1dc`
- subjects: 10
- relations: 5
- facts: 50
- train rows: 350
- rows per fact: 7
- held-out direct validation rows: 50
- exact train/validation overlap: 0
- model: base SmolLM2-360M
- objective: answer-only
- epochs: 36
- batch size: 50
- optimizer steps: 252
- learning rate: `1e-4`
- scheduler: constant with warmup
- weight decay: 0

## Training Run

- Slurm job: `391060`
- node: `gruenau9`
- GPU: one A100 80GB
- runtime: 127.6 seconds
- aggregate train loss: 0.3434
- final held-out direct eval loss: approximately 0.0708
- status: completed without OOM or runtime errors

Run directory:

```text
runs/training/m1_smollm2_360m_diagnostic_all_relations_50_direct_answer_only/
20260711T064204Z_m1_smollm2_360m_diagnostic_all_relations_50_direct_answer_only_lr1e-4_ep36_b84bc68a
```

## Evaluation

- jobs: `391061` through `391071`
- views: exact prefix, held-out direct, held-out QA matched
- full relation-specific candidate inventories retained
- relation-binding metrics active for `born_in`/`lives_in`
- all evaluation jobs completed without errors

## Global Results

Counts are top-1 facts out of 50.

| Checkpoint | Exact | Direct | QA | Overlap | Mean ranks E/D/Q | Gate |
|---|---:|---:|---:|---:|---|---|
| 25 | 10 | 10 | 8 | 6 | 27.54 / 19.88 / 20.40 | fail |
| 50 | 48 | 40 | 44 | 37 | 1.04 / 1.56 / 1.22 | pass |
| 75 | 50 | 48 | 49 | 48 | 1.00 / 1.14 / 1.08 | pass |
| 100 | 50 | 47 | 49 | 47 | 1.00 / 1.18 / 1.08 | pass |
| 125 | 50 | 47 | 49 | 47 | 1.00 / 1.16 / 1.08 | pass |
| 150 | 50 | 47 | 49 | 47 | 1.00 / 1.16 / 1.08 | pass |
| 175 | 50 | 48 | 48 | 47 | 1.00 / 1.14 / 1.08 | pass |
| 200 | 50 | 47 | 49 | 47 | 1.00 / 1.14 / 1.08 | pass |
| 225 | 50 | 47 | 48 | 47 | 1.00 / 1.16 / 1.10 | pass |
| 250 | 50 | 48 | 48 | 47 | 1.00 / 1.14 / 1.10 | pass |
| 252 | 50 | 47 | 48 | 47 | 1.00 / 1.14 / 1.08 | pass |

Earliest passing checkpoint: `checkpoint-50`.

Best robust checkpoint by direct/QA overlap: `checkpoint-75`.

## Relation-Level Result At Checkpoint 75

| Relation | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| `profession` | 10/10 | 10/10 | 10/10 | 10/10 |
| `born_in` | 10/10 | 10/10 | 10/10 | 10/10 |
| `lives_in` | 10/10 | 9/10 | 10/10 | 9/10 |
| `studied_at` | 10/10 | 9/10 | 9/10 | 9/10 |
| `works_at` | 10/10 | 10/10 | 10/10 | 10/10 |

The two remaining robustness misses are concentrated in `lives_in` direct extraction and
`studied_at` direct/QA extraction. There is no global relation collapse.

## Interpretation

The direct-aware format contract scales from one fact to ten single-relation facts and then
to 50 facts across five relations. Relation diversity does not recreate the catastrophic
failure observed in the original 50-fact recipe.

The key controlled contrast is:

- original 50-fact ladder at its best: exact 12/50, direct 1/50, QA 11/50, overlap 1/50;
- direct-aware 50-fact run at checkpoint 75: exact 50/50, direct 48/50, QA 49/50, overlap 48/50.

The evidence now supports the diagnosis that missing prompt-format coverage, combined with
insufficient controlled exposure, was the central acquisition failure. Model size alone was
not the binding constraint at this scale.

## Decision

The precommitted gate passed. The next nested level is 100 subjects / 500 facts with the
same seven-row format contract. To preserve 36 exposures per row and 252 optimizer updates,
use micro-batch 50 with gradient accumulation 10, giving effective batch 500. Evaluate
checkpoint 25/50/75 first before launching a full checkpoint wave.

