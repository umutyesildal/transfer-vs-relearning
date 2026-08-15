# 21 - M1 BIO QA First Run Report

Date: 2026-07-07

## Purpose

This report records the first actual training run for the BIO-QA redesign branch.

The goal of this run is to isolate the effect of the new English-side acquisition data
while keeping the model family aligned with the earlier R2 comparison point.

## Source State

Synthetic data repo:

- branch: `bio-qa-m1`
- commit: `ae0e457`
- pushed to GitHub: yes

Training repo:

- branch: `corpus-update`
- commit: `a0bbbaf`
- pushed to GitHub: yes

## Dataset Sync

New dataset version:

```text
synthetic_v1_bio_qa
```

HU sync command used:

```bash
python scripts/sync_synthetic_dataset.py \
  --source-repo https://github.com/umutyesildal/synthetic-data-generation \
  --ref bio-qa-m1 \
  --version synthetic_v1_bio_qa
```

Synced source commit:

```text
ae0e457f4b1f34ce288395cbaa45cdd0e39835fd
```

The synced manifest records the new optional BIO-QA artifacts:

- `english_biographies.jsonl`
- `english_qa_train.jsonl`
- `english_training_m1_bio_qa.jsonl`
- `english_training_m1_bio_qa_summary.json`

## Data Comparison Against Earlier M1 Inputs

Row counts:

- baseline English training: `104169`
- R1 QA-mix dataset: `416676`
- BIO-only dataset: `104169`
- BIO-QA merged dataset: `135403`

Approximate average whitespace words per row:

- baseline English training: `6.92`
- R1 QA-mix: `8.24`
- BIO-only: `27.40`
- BIO-QA merged: `23.16`

Interpretation:

- BIO-QA does not win by brute-force row count,
- it wins by making each English training row much denser and more subject-centered,
- this is exactly the intended redesign hypothesis.

## Training Config

```text
configs/training/m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1.yaml
```

Key settings:

- dataset version: `synthetic_v1_bio_qa`
- train file: `english_training_m1_bio_qa.jsonl`
- base model: `HuggingFaceTB/SmolLM2-360M`
- learning rate: `5e-5`
- epochs: `1`
- effective batch size: `16`

## HU Validation Before Launch

Focused tests run on HU:

```text
tests/test_data_core.py
tests/test_training_core.py
tests/test_recipe_data.py
```

Result:

```text
passed
```

## Slurm Launch

Training job:

```text
380525
```

Initial queue state:

```text
RUNNING on gruenau9
```

Verified startup log:

- selected config is the BIO-QA SmolLM2-360M config,
- dataset version resolves to `synthetic_v1_bio_qa`,
- train file resolves to `english_training_m1_bio_qa.jsonl`,
- base model manifest resolves to `HuggingFaceTB__SmolLM2-360M`,
- runtime shows `NVIDIA A100 80GB PCIe`,
- no early stderr failure was observed at launch.

## Comparison Target

Primary comparison anchor:

```text
R2 = SmolLM2-360M + R1 QA-mixed dataset + 1 epoch
```

R2 best metrics to beat:

- direct top1: `0.022`
- QA top1: `0.024`
- robust overlap: `5/500`

## Current Status

```text
training complete; checkpoint evaluation complete
```

First live check at `2026-07-07 14:35 CEST`:

- Slurm state: `RUNNING`
- elapsed: `5:58`
- remaining limit: `3:54:02`
- node: `gruenau9`
- run directory currently contains `training_manifest.json`
- stdout is still at the startup/config printout
- stderr is empty

Interpretation:

- the launch is healthy,
- the job has not crashed early,
- but there is not yet enough emitted training output to compare checkpoint quality,
- so the next meaningful comparison step is after training finishes and checkpoint
  evaluation jobs are submitted.

Completion check at `2026-07-07 14:43 CEST`:

- Slurm queue entry is gone, so training has completed
- run directory now contains:
  - `train_metrics.json`
  - `eval_metrics.json`
  - `training_manifest.json`
  - `final_model/`
- stdout now contains the full training trace through epoch `1.0`
- stderr only shows progress-bar output, not a failure

## Final Training Metrics

- train loss: `1.347`
- eval loss: `1.167`
- train runtime: `417.6` seconds
- train steps per second: `1.561`

Intermediate evaluation snapshots from stdout:

- epoch `0.2502`: eval loss `1.256`
- epoch `0.5004`: eval loss `1.180`
- epoch `0.7506`: eval loss `1.168`
- epoch `1.0`: eval loss `1.167`

## Training-Only Comparison Against R2

R2 reference:

- train loss: `1.956`
- eval loss: `1.751`
- runtime: `300.8` seconds
- steps per second: `2.713`

BIO-QA first-run comparison:

- train loss improved from `1.956` to `1.347`
- eval loss improved from `1.751` to `1.167`
- runtime increased from `300.8s` to `417.6s`
- throughput fell from `2.713` to `1.561` steps/sec

Interpretation:

- BIO-QA is clearly stronger than R2 on the training objective itself,
- the denser subject-centered data appears easier for the model to fit,
- but this is still not enough to claim a better M1,
- the thesis gate depends on English retrieval quality under direct and QA-matched
  probing, so evaluation remains the decisive step.

## Evaluation Follow-Up

Checkpoint evaluation for this run has now been completed and recorded separately in:

```text
documentation/22_M1_BIO_QA_EVALUATION_REPORT.md
```

Outcome summary:

- the BIO-QA branch improved training loss and eval loss relative to R2,
- but it did not beat R2 on the English learned-fact gate,
- so the first BIO-QA run should not be promoted as M1.
