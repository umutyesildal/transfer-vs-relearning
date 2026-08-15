# 26 - M1 Two-Stage Stage B1 Run Report

Date: 2026-07-07

## Purpose

This report records the first Stage B1 launch of the two-stage M1 branch.

Stage B1 means:

- start from the Stage A final model,
- continue with English QA-only training,
- keep the current CLM objective before any answer-focused loss redesign.

## Source State

Training repo:

- branch: `corpus-update`
- commit: `0f43613`
- pushed to GitHub: yes

## Stage B1 Config

```text
configs/training/m1_smollm2_360m_english_qa_stage_b1_lr5e-5_ep1.yaml
```

Key settings:

- dataset version: `synthetic_v1_bio_qa`
- train file: `output/english_qa_train.jsonl`
- base model manifest:
  `runs/local_model_manifests/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1/final_model_manifest.json`
- learning rate: `5e-5`
- epochs: `1`
- effective batch size: `16`

## HU Preparation Before Launch

Preparation steps:

1. pull commit `0f43613`,
2. materialize a local manifest for the Stage A final model,
3. run focused tests.

Focused tests run on HU:

```text
tests/test_training_core.py
tests/test_model_local_manifest.py
```

Result:

```text
passed
```

## Slurm Launch

Training job:

```text
382777
```

Current observed state:

```text
RUNNING on gruenau9
```

Verified startup log:

- selected config is the Stage B1 QA-only config,
- dataset version resolves to `synthetic_v1_bio_qa`,
- train file resolves to `artifacts/datasets/synthetic_v1_bio_qa/output/english_qa_train.jsonl`,
- base model manifest resolves to the Stage A final-model manifest,
- runtime shows `NVIDIA A100 80GB PCIe`,
- no early stderr failure was observed.

## Planned Follow-Up

After Stage B1 training completes:

1. evaluate retained checkpoints under English direct and QA-matched prompts,
2. compare Stage B1 against:
   - Stage A,
   - BIO-QA single-stage,
   - R2,
3. decide whether the two-stage branch has finally crossed the learned-fact gate,
4. only if it still fails, consider Stage B2 with answer-focused loss.

## Completion Status

Current status:

```text
training complete; checkpoint evaluation complete
```

Final training metrics from stdout:

- train loss: `2.054`
- eval loss: `1.951`
- train runtime: `66.59` seconds
- train steps per second: `1.036`

Checkpoint evaluation for this run has now been completed and recorded in:

```text
documentation/27_M1_TWO_STAGE_STAGE_B1_EVALUATION_REPORT.md
```

Outcome summary:

- Stage B1 improved QA-side extraction relative to Stage A,
- but it still did not beat BIO-QA single-stage or R2 on the English gate,
- so Stage B1 should not be promoted as M1.
