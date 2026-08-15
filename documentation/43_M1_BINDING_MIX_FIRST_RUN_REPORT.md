# 43 - M1 Binding Mix First Run Report

Date: 2026-07-09

## Purpose

This report records the first executable M1 run on top of the new binding-focused dataset
family.

## Source State

Synthetic data repo:

- branch: `bio-qa-m1`
- launch commit: `ab018c0`
- pushed to GitHub: yes

Training repo:

- branch: `corpus-update`
- launch commit: `fdfb7ad`
- pushed to GitHub: yes

## Dataset State

Dataset version in `transfer-vs-relearning`:

```text
synthetic_v1_binding_mix
```

Local sync source used for the dataset artifact copy:

```text
syntheticFacts commit c91329aa4684beafeac653dca28ab71ba1d8f62f
```

Prepared pilot file:

```text
artifacts/datasets/synthetic_v1_binding_mix/pilot_100_subjects.json
```

## Selected Config

```text
configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1.yaml
```

Key settings:

- dataset version: `synthetic_v1_binding_mix`
- train file: `english_training_m1_binding_mix.jsonl`
- base model: `HuggingFaceTB/SmolLM2-360M`
- learning rate: `5e-5`
- epochs: `1`

## Validation Before Launch

Local synthetic-data validation:

- `python3 -m unittest discover -s tests`
- `python3 generate_canonical.py --run-pipeline`

Result:

```text
passed
```

Local training-repo focused tests:

```text
PYTHONPATH=src python3 -m pytest tests/test_data_core.py tests/test_training_core.py -q -ra
```

Result:

```text
passed
```

HU focused tests:

```text
tests/test_data_core.py
tests/test_training_core.py
```

Result:

```text
passed
```

## Slurm Launch

Training job:

```text
389597
```

Immediate Slurm state:

- state: `RUNNING`
- node: `gruenau10`
- start time: `2026-07-09 12:53:36`
- scheduled end time: `2026-07-09 16:53:36`
- time limit: `04:00:00`

Log paths:

- stdout: `logs/m1-gpt2-english-389597.out`
- stderr: `logs/m1-gpt2-english-389597.err`

## Early Interpretation

The important project milestone is now complete:

- the deep-research synthetic-data redesign is no longer only documented,
- it has been implemented,
- synchronized into the training repo,
- uploaded to HU,
- and launched as a real M1 run.

## Final Outcome

The job did not reach the metric-writing stage.

Observed behavior:

- Slurm job `389597` left the queue without producing `eval_metrics.json`
- the run directory only contains `training_manifest.json`
- the manifest remains at status `started`

Failure point:

- the run crashed at the beginning of trainer execution
- no completed training step or checkpoint was recorded

Primary error from `logs/m1-gpt2-english-389597.err`:

```text
torch.OutOfMemoryError: CUDA out of memory
```

Interpretation:

- this first binding-mix run is not an acquisition-quality failure
- it is an execution failure caused by the current SmolLM2 training recipe being too memory-heavy for this dataset/config combination on the allocated single A100 setup
- the current config uses:
  - block size: `512`
  - per-device train batch size: `8`
  - gradient accumulation: `2`
  - gradient checkpointing: `false`

## Pending Next Step

Before rerunning:

1. reduce memory pressure in the SmolLM2 M1 recipe,
2. relaunch the binding-mix run,
3. only after a clean training completion:
   - record trainer metrics,
   - evaluate retained checkpoints under English direct prompts,
   - evaluate retained checkpoints under English QA-matched prompts,
   - compare against earlier BIO-QA and plain SmolLM2 baselines.
