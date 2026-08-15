# 48 - M1 Acquisition Ladder Plan

Last updated: 2026-07-10

## Decision

The next M1 family restores the small English acquisition pilot that was specified in the
historical Notion plan but not executed as a training curriculum. Previous M1 runs trained
on the full 5,000-subject / 25,000-fact dataset and used the 100-subject subset only for
evaluation. This plan trains on nested small subsets before any new full-scale run.

The ladder is:

1. 10 subjects / 50 facts
2. 100 subjects / 500 facts
3. 500 subjects / 2,500 facts
4. 5,000 subjects / 25,000 facts only after the first three levels pass

The subsets are deterministic and nested: `10 subset 100 subset 500`.

## Scientific Purpose

This is a diagnostic acquisition experiment, not a new post-hoc definition of M1 success.
It separates four failure modes:

- inability to store even a tiny number of synthetic bindings;
- memorization of seen strings without paraphrase generalization;
- prompt-specific extraction without direct/QA robustness;
- capacity or interference failure that appears only as the number of facts grows.

The final M1 learned-fact gate remains candidate-ranking based. The ladder does not weaken
that gate.

## Data Contract

Each subject has the five current relations:

- `profession`
- `born_in`
- `lives_in`
- `studied_at`
- `works_at`

Each fact receives exactly five supervised training rows:

- three declarative templates;
- two English QA templates that are textually distinct from the held-out probe.

Every fact also receives one held-out validation QA row and one exact-prefix diagnostic
probe. Exposure is fixed across facts, so the first ladder experiment does not confound
acquisition with the low/medium/high frequency buckets.

No multiple-choice options or negative object strings are included in the CLM text.
Only canonical answer tokens and EOS contribute to the loss.

Generated local/remote artifacts live under:

```text
artifacts/datasets/acquisition_ladder_v1/
```

These generated artifacts are operational outputs and are not committed.

## First Training Recipe

Model:

```text
HuggingFaceTB/SmolLM2-360M
```

Training:

- full-parameter fine-tuning, not LoRA;
- answer-only causal loss;
- 10 epochs;
- learning rate `5e-5`;
- cosine schedule with 5% warmup;
- batch size 8, no gradient accumulation;
- block size 128;
- checkpoints every approximately 10% of training.

The 10-epoch setting is intentional. The first rung is a micro-overfit test whose purpose
is to establish whether the model and objective can learn 50 controlled bindings at all.

## Evaluation Views

Every saved checkpoint will be evaluated in English with the full relation-level candidate
inventories, not a reduced 8-candidate training set.

Required views:

1. Exact-prefix ranking using a declarative prefix seen during training.
2. Held-out direct probe ranking.
3. Held-out QA-matched probe ranking.
4. Direct/QA robust top-1 overlap by fact ID.

Training and validation loss are supporting diagnostics only. They do not determine the
winner.

## Precommitted Progression Gate

A ladder level passes only if one checkpoint satisfies all of the following:

- exact-prefix English top-1 at least 90%;
- held-out QA English top-1 at least 50%;
- held-out direct English top-1 at least 50%;
- direct/QA robust top-1 overlap at least 40% of the level's facts.

Select the earliest checkpoint that satisfies all four criteria. If no checkpoint passes,
do not launch the next level automatically.

These are diagnostic progression thresholds. Promotion to thesis M1 still requires the
existing learned-fact gate and records the exact learned-fact subset for downstream M2/M3.

## Interpretation Matrix

- Exact-prefix failure on 50 facts: objective, data, tokenizer, or evaluator pipeline issue.
- Exact-prefix success but held-out failure: string memorization without extraction.
- QA success but direct failure: prompt-format overfitting.
- 10-subject success followed by 100/500 failure: scale, capacity, or interference issue.
- All three levels pass: proceed to the full M1 dataset with the same objective family.

Model scaling to 1.7B/2B and the expose's from-scratch fallback remain later decisions. They
must not be used to bypass a failure on the 50-fact micro-overfit rung.

## Execution Protocol

For every training or evaluation submission:

1. record the Slurm job ID;
2. inspect the queue immediately;
3. estimate runtime from dataset size and comparable jobs;
4. wait for the estimated interval;
5. inspect queue, logs, manifests, and metrics;
6. update documentation before launching the next rung.

## Implemented Files

- `src/transfer_vs_relearning/data/acquisition_ladder.py`
- `scripts/build_acquisition_ladder.py`
- `configs/training/m1_smollm2_360m_acquisition_ladder_10_answer_only_lr5e-5_ep10.yaml`
- `tests/test_acquisition_ladder.py`

## Implementation Status

Local implementation completed on 2026-07-10.

- `transfer-vs-relearning` commit: `8ee4f17` (`Add diagnostic M1 acquisition ladder`)
- full local test suite: passed (`.....s...`, with only the repository's expected skips)
- Python compile check: passed
- shell syntax checks: passed
- real `synthetic_v1` builder smoke test: passed
- 10-subject output: 50 facts, 250 training rows, 50 held-out validation rows
- 100-subject output: 500 facts, 2,500 training rows, 500 held-out validation rows
- 500-subject output: 2,500 facts, 12,500 training rows, 2,500 held-out validation rows
- exact train/validation text overlap at the 10-subject level: zero
- generated dataset artifacts: intentionally uncommitted

The first push attempt failed inside the restricted sandbox because GitHub DNS was not
available. The required external push request was then rejected by the Codex execution
service because its usage window was exhausted until 18:38 CEST. Therefore `8ee4f17` is
currently local and the HU pull/job submission has not yet occurred. Do not record a Slurm
job ID until the push succeeds and the remote submission returns one.
