# 24 - M1 Two-Stage Stage A Run Report

Date: 2026-07-07

## Purpose

This report records the first actual Slurm launch for the two-stage M1 branch.

This run is Stage A only:

- English biography-only acquisition,
- no Stage B extraction continuation yet,
- same SmolLM2-360M base model family used for recent M1 comparisons.

## Source State

Training repo:

- branch: `corpus-update`
- commit: `4d6059e`
- pushed to GitHub: yes

## Stage A Config

```text
configs/training/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1.yaml
```

Key settings:

- dataset version: `synthetic_v1_bio_qa`
- train file: `output/english_biographies.jsonl`
- base model: `HuggingFaceTB/SmolLM2-360M`
- learning rate: `5e-5`
- epochs: `1`
- effective batch size: `16`

## HU Validation Before Launch

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
382768
```

Initial queue observation:

```text
PENDING
```

Second queue observation at launch verification:

```text
RUNNING on gruenau9
```

Verified startup log:

- selected config is the Stage A biography-only config,
- dataset version resolves to `synthetic_v1_bio_qa`,
- train file resolves to `artifacts/datasets/synthetic_v1_bio_qa/output/english_biographies.jsonl`,
- base model manifest resolves to `HuggingFaceTB__SmolLM2-360M`,
- runtime shows `NVIDIA A100 80GB PCIe`,
- no early stderr failure was observed.

## Planned Follow-Up

After Stage A training completes:

1. evaluate retained checkpoints under the same English direct and QA-matched gate,
2. compare Stage A against:
   - BIO-QA single-stage,
   - R2 QA-mix SmolLM2 baseline,
3. decide whether to proceed to Stage B1:
   - Stage A final model,
   - English QA-only continuation,
   - current CLM objective first.

## Completion Status

Current status:

```text
training complete; checkpoint evaluation not yet submitted
```

Completion check:

- Slurm queue entry for `382768` is gone
- final run directory:

```text
runs/training/m1_smollm2_360m_english_biographies_stage_a/20260707T171129Z_m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_fa548873
```

- stdout shows the full epoch completed successfully
- stderr contains only progress-bar output

## Final Training Metrics

- train loss: `1.291`
- eval loss: `1.115`
- train runtime: `360.0` seconds
- train steps per second: `1.62`

Intermediate eval snapshots from stdout:

- epoch `0.2506`: eval loss `1.202`
- epoch `0.5013`: eval loss `1.128`
- epoch `0.7519`: eval loss `1.116`
- epoch `1.0`: eval loss `1.115`

## Training-Only Comparison

Relative to BIO-QA single-stage:

- train loss improved from `1.347` to `1.291`
- eval loss improved from `1.167` to `1.115`
- runtime decreased from `417.6s` to `360.0s`

Relative to R2:

- train loss improved from `1.956` to `1.291`
- eval loss improved from `1.751` to `1.115`

Training-only interpretation:

- Stage A biography-only acquisition fits even better than the BIO-QA single-stage mix,
- but the project decision still depends on English retrieval evaluation,
- so no M1 promotion decision should be made before checkpoint evaluation.

Stage A checkpoint evaluation has now been completed and is recorded in:

```text
documentation/25_M1_TWO_STAGE_STAGE_A_EVALUATION_REPORT.md
```
