# M1 historical Slurm reuse audit

**Date:** 2026-08-22  
**Status:** `HISTORICAL_ROUTE_CONFIRMED_NON_EXECUTABLE`  
**Scope:** inspect preserved training launchers and completed-run records  
**New training/evaluation:** not run

## Finding

The project already has a working training path. The old M1 launchers do not use a different
training engine per experiment; they converge on the same repository entrypoint:

```text
scripts/training/train_clm.py
```

The established operational route is:

```text
account=yesildau
partition=gpu
gres=gpu:a10080gb:1
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/training/train_clm.py --config <config>
```

Each launcher also binds a fresh scratch root, offline Hugging Face/Torch caches, a task-local
`TMPDIR`, an exact repository commit and a preflight/smoke gate before the training command.

## Preserved launchers to reuse

| Existing launcher | Model/role | Proven operational pattern |
|---|---|---|
| `slurm/m1/train_m1_provenance_screen.slurm` | OLMo/Pythia/Falcon candidate registry | `gpu` + A100; preflight, tokenization audit, smoke, then `train_clm.py` |
| `slurm/m1/train_qwen_scale_probe.slurm` | Qwen M1 scale probe | `gpu` + A100; offline caches, manifest checks, then `train_clm.py` |
| `slurm/m1/train_m1_retention_seed42.slurm` | Qwen retention/control chain | `gpu` + A100; immutable preflight manifest and exact config binding |
| `slurm/m1/train_smollm_prompt_consistency.slurm` | SmolLM M1 prompt-consistency chain | `gpu` + A100; preflight, dataset/config preparation, then `train_clm.py` |
| `slurm/m1/train_m1_pythia_repair_rtx3090_bf16.slurm` | RTX3090 BF16 repair route | historical explicit RTX3090 route with a pinned compatibility environment |

The first three-model M1 draft must reuse this launcher shape rather than inventing a new model
trainer. The new controller only needs to orchestrate three independent instances and attach the
new epoch-trace/checkpoint-evaluation policy.

## Historical completion evidence

The preserved reports record successful training with this route, including:

- SmolLM2-360M Relation V2 10-subject run `391106`, all 252 updates complete;
- SmolLM2-360M 2,500-fact exploratory run `392293`, all 252 updates complete;
- GPT-2 M1 3-epoch run `378802`, with ten completed checkpoint evaluations;
- Qwen scale/retention chains using the A100 launcher family;
- later model-specific BF16/compatibility repairs using the same `train_clm.py` entrypoint.

These are historical evidence and are not silently relabeled as the new matched three-model M1
wave. Their value here is operational: the Slurm/account/environment/trainer path is already
known to work.

## Route decision for the new draft

The current read-only HU route test accepted `yesildau` requests on the `gpu` partition for A100,
RTX A6000, RTX6000 and V100. The frozen M1 draft is BF16, so A100 is the default route and RTX
A6000 is the compatible fallback. RTX6000/V100 require a separately authorized precision change;
RTX3090 remains inaccessible through `wbimlgpu`/`viscomgpu` for this account and is not required
for the initial wave.

The existing `train_clm.py` implementation and historical launchers remain unchanged. No Slurm
job, output root, model load, evaluation or training was started by this audit.

## Boundary

This audit does not create the SHA-bound M1 execution contract. It resolves the false impression
that the project lacks a working trainer: the trainer exists and has completed many prior runs.
The future contract must bind the exact three draft configs, model/tokenizer manifests, scratch
roots, A100/RTX A6000 route, epoch snapshot policy and eval-v2 DAG before execution.
