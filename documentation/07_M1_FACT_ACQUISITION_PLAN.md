# 07 - M1 Fact Acquisition Plan

Last updated: 2026-07-05

This is the executable plan for the first M1 training pilots. It follows the literature
notes in `06_M1_FACT_ACQUISITION_RESEARCH_NOTES.md`.

## Current Implementation State

Local implementation commit prepared:

```text
be230625897a3f941842ef95f19bbdc4a20743b3 - Add M1 English fact acquisition training
```

Local validation passed:

```text
PYTHONPATH=src python3 -m pytest tests/test_data_core.py tests/test_evaluation_core.py tests/test_training_core.py -q -ra
```

Result:

```text
36 outcomes; 2 expected local skips because torch is not installed locally.
```

The push to GitHub must be performed through the normal repository workflow before HU can
pull this commit. The blocked automation-safe command is:

```bash
git push origin corpus-update
```

## Goal

Produce an M1 checkpoint from base GPT-2 after English-only continued causal language
modeling on the synthetic facts.

Training data:

```text
artifacts/datasets/synthetic_v1/output/english_training.jsonl
```

The trainer reads only the `text` field. It does not train on Turkish repetition data or
probe questions.

## Pilot Grid

Run these three pilot configs first:

- `configs/training/m1_gpt2_english_facts_lr5e-5_ep1.yaml`
- `configs/training/m1_gpt2_english_facts_lr1e-4_ep1.yaml`
- `configs/training/m1_gpt2_english_facts_lr5e-5_ep3.yaml`

Common settings:

- base model: `artifacts/models/openai-community__gpt2/model_manifest.json`
- objective: causal language modeling
- block size: 512
- effective batch size: 16 (`per_device_train_batch_size=8`, `gradient_accumulation_steps=2`)
- optimizer/schedule: AdamW through Hugging Face Trainer, cosine scheduler, warmup ratio 0.05
- weight decay: 0.01
- precision: BF16
- checkpoint target: approximately 25%, 50%, 75%, and 100%

## Slurm Command

From the HU repo root:

```bash
git pull origin corpus-update
PYTHONPATH=src python -m pytest tests/test_training_core.py -q -ra
```

Then submit the first pilot:

```bash
sbatch --export=ALL,TRAIN_CONFIG=configs/training/m1_gpt2_english_facts_lr5e-5_ep1.yaml slurm/train_m1_gpt2_english_facts.slurm
```

Change `TRAIN_CONFIG` for the other two pilot configs.

## Job Protocol

For every submitted M1 job:

1. Check `squeue` immediately.
2. Check `logs/m1-gpt2-english-<jobid>.out` and `.err` after startup.
3. Estimate completion time from the first progress logs.
4. Check again after the estimated interval.
5. Do not launch follow-up M1 jobs without explicit approval.

## Outputs

Each run writes under:

```text
runs/training/m1_gpt2_english_facts/
```

Each run directory contains:

- `training_manifest.json`
- `train_metrics.json`
- `eval_metrics.json`
- `checkpoints/checkpoint-*`
- `final_model/`

The manifest records config hash, dataset hash, base model manifest hash, git commit,
software versions, GPU info, estimated steps, checkpoint directories, and final model path.

## Selection Rule

Do not select M1 by training loss alone.

After the pilot runs, evaluate all saved checkpoints on:

- English direct prompts,
- English QA-matched prompts.

Main M1 learned-fact gate:

- English direct prompt,
- primary mean-logprob ranking,
- correct answer top-1,
- positive margin over the strongest incorrect candidate.

Robust subset:

- top-1 under both English direct and English QA-matched prompts.

The checkpoint with the best learned-fact coverage under the main gate, while maintaining
reasonable QA-matched robustness, becomes the candidate M1 checkpoint.
