# 29 - M1 Two-Stage Stage B2 Run Report

Date: 2026-07-07

## Purpose

This report records the first Stage B2 launch of the two-stage M1 branch and the
final training outcome.

Stage B2 means:

- start from the Stage A final model,
- continue with English QA rows,
- optimize only answer-token loss instead of full-sequence CLM.

## Source State At Launch

Training repo:

- branch: `corpus-update`
- commit: `04457b0`
- pushed to GitHub: yes

## Stage B2 Config

```text
configs/training/m1_smollm2_360m_english_qa_stage_b2_answer_only_lr5e-5_ep1.yaml
```

Key settings:

- dataset version: `synthetic_v1_bio_qa`
- train file: `output/english_qa_train.jsonl`
- answer field: `answer`
- base model manifest:
  `runs/local_model_manifests/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1/final_model_manifest.json`
- loss mode: `answer_only`
- learning rate: `5e-5`
- epochs: `1`

## HU Validation Before Launch

Focused tests run on HU:

```text
tests/test_training_core.py
tests/test_model_local_manifest.py
tests/test_training_answer_only.py
```

Result:

```text
passed
```

## Slurm Launch

Training job:

```text
383788
```

Verified startup log before training settled:

- selected config is the Stage B2 answer-only config,
- dataset version resolves to `synthetic_v1_bio_qa`,
- train file resolves to `artifacts/datasets/synthetic_v1_bio_qa/output/english_qa_train.jsonl`,
- answer field resolves to `answer`,
- base model manifest resolves to the Stage A final-model manifest,
- `loss_mode: answer_only` is present in the selected config,
- no early stderr failure was observed.

## Final Training Outcome

Training status:

```text
complete
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_qa_stage_b2_answer_only/20260707T181202Z_m1_smollm2_360m_english_qa_stage_b2_answer_only_lr5e-5_ep1_0d974577
```

Final training metrics:

- train loss: `1.328`
- eval loss: `1.308`
- train runtime: `1251s`
- train steps/sec: `1.53`

Retained checkpoints actually written by the trainer:

- `checkpoint-478`
- `checkpoint-956`
- `checkpoint-1434`
- `checkpoint-1912`
- `checkpoint-1914`

Immediate interpretation:

- Stage B2 lowered optimization loss much more than Stage B1.
- This is encouraging for the extraction objective itself.
- It does not count as an M1 success until English checkpoint evaluation finishes.

## Next Step

Run English direct and QA-matched checkpoint evaluation on the five retained checkpoints
and compare the result against Stage B1.
