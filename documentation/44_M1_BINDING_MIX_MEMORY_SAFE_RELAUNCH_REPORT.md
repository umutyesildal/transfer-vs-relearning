# 44 - M1 Binding Mix Memory-Safe Relaunch Report

Date: 2026-07-09

## Purpose

This report records the first recovery run after the initial binding-mix launch failed with
CUDA out-of-memory before producing any checkpoints or metrics.

## Why A Relaunch Was Needed

The first run (`389597`) did not fail on evaluation quality grounds.

It failed during training startup with:

```text
torch.OutOfMemoryError: CUDA out of memory
```

This means the next step is a recipe-stability correction, not a scientific-direction
change.

## Recovery Strategy

Keep the same:

- dataset version: `synthetic_v1_binding_mix`
- base model: `HuggingFaceTB/SmolLM2-360M`
- learning rate: `5e-5`
- epochs: `1`
- block size: `512`

Change only the memory-sensitive execution settings:

- per-device train batch size: `8 -> 2`
- per-device eval batch size: `8 -> 2`
- gradient accumulation: `2 -> 8`
- gradient checkpointing: `false -> true`

Interpretation:

- effective batch size is preserved at `16`
- the experiment family stays comparable
- the relaunch is intended to fix execution stability without changing the core M1 question

## Relaunch Config

```text
configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc.yaml
```

## Source State

Training repo:

- branch: `corpus-update`
- launch commit: `59a63e3`
- pushed to GitHub: yes

Validation before launch:

Local:

```text
PYTHONPATH=src python3 -m pytest tests/test_training_core.py tests/test_data_core.py -q -ra
```

HU:

```text
PYTHONPATH=src /vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python -m pytest tests/test_training_core.py tests/test_data_core.py -q -ra
```

Result:

```text
passed
```

## Slurm Launch

Training job:

```text
389719
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_facts_binding_mix/20260709T154625Z_m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc_8ca27779
```

Immediate queue state:

- state: `RUNNING`
- node: `gruenau10`
- observed at: `2026-07-09 17:46 CEST`
- elapsed at first check: `0:13`
- time limit remaining at first check: `3:59:47`

Launch note:

- job export also sets `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`

## Current Status

Final observed outcome:

- job `389719` started successfully and used the intended memory-safe config
- the run again failed with CUDA OOM before producing checkpoints or metrics
- this time the node-level inspection showed external GPU contamination on `gruenau10`

Observed external GPU processes on the same node:

```text
42818, VLLM::Worker_TP0, 78064 MiB
42819, VLLM::Worker_TP1, 78064 MiB
```

Interpretation:

- the relaunch did not falsify the adjusted recipe yet
- the stronger explanation is node contamination, not a clean in-recipe failure
- the next correct move is a clean-node retry, not another scientific redesign

## Pending Execution Record

See `45_M1_BINDING_MIX_CLEAN_NODE_RETRY_REPORT.md` for the clean-node retry that excludes
`gruenau10`.
