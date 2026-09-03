# vngrs-m2-oscar-gpu-identity-qualification-v1

Status: FROZEN / UNEXECUTED / EXACT USER AUTHORIZATION REQUIRED.

## Objective and evidence boundary

Qualify the new M2 allocation-local CUDA UUID gate before preparing any scientific retry.
The preserved V1B family is incomplete: 21 complete indices 0–20 and 42 guard-failed indices
21–62. This contract does not recover or rescore any of those states. A PASS establishes the
binding on one current allocation, not the historical cause of every V1B failure and not a
guarantee about other allocations.

## Frozen identities

- Gate module: `src/transfer_vs_relearning/study/m2_gpu_gate.py`.
- Module SHA-256: `6e328d8c8879ec1e0b852fc85dbc357b6ea50490420c81c8a44da90a9be10d09`.
- Python: `/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python`.
- Runtime lock: same directory, `environment.lock.txt`.
- Runtime lock SHA-256: `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`.
- HU checkout: `/vol/tmp2/yesildau/transfer-vs-relearning-monorepo-v1`.
- Branch: `agent/m2-three-model-vngrs-d0`.
- Exact implementation commit: supplied separately in the user's authorization.
- Fresh output root: `/vol/tmp2/yesildau/vnd_m2_oscar_gpu_identity_qualification_v1`.
- Required audit: `gpu_identity_audit.json` under that root.

## Allowed single wave after exact authorization

1. Ordinary non-force push of the exact authorized commit. Verify HU branch, tracked/untracked
   cleanliness, ancestor relation and no overlapping changes; fast-forward only. Stop on drift.
2. Verify contract/module/runtime hashes and the exact commit. Run the 34 local/HU targeted
   tests without CUDA/model access. All tests must pass.
3. Verify root absence (including broken symlinks), scratch-resolved paths and no duplicate
   `m2-gpu-id-qual-v1` job. Require at least 1 GiB free scratch space and 1,024 free inodes.
   No HU-home output, downloads, environment installation or prior-root writes are allowed.
4. Run one scheduler test-only check, then at most one real job: account `yesildau`, partition
   `gpu`, `gpu:a10080gb:1`, 8 CPUs, 64G host RAM, 10-minute limit, job name `m2-gpu-id-qual-v1`.
   No array, explicit GPU override, device fallback, job requeue or automatic retry. Use
   `--no-requeue`; do not alter Slurm-provided `CUDA_VISIBLE_DEVICES`.
5. Only after preflight create the fresh root with `logs`, `tmp`, `cache` directories. All Slurm
   output/error and TMPDIR/HF_HOME/XDG_CACHE_HOME must resolve there. Set PYTHONDONTWRITEBYTECODE=1,
   PYTHONPATH=src, HF_HUB_OFFLINE=1, HF_DATASETS_OFFLINE=1 and TRANSFORMERS_OFFLINE=1.
   Inside the job recheck exact commit/cleanliness/module/runtime/contract hashes before CUDA.
6. Invoke `assert_allocated_gpu_memory(Path(root) / "gpu_identity_audit.json")` exactly once in
   the pinned Python. It may initialize a CUDA context and read device UUID/name/free/total
   memory; query SMI only by that UUID. No model/tokenizer loading, inference or scoring.
7. Read the compact audit and logs, persist a local chronological result. No second submission.

## Acceptance and failure

PASS requires exactly one Slurm-visible CUDA device, a valid CUDA-derived GPU UUID, A100-80GB,
SMI UUID equality, coherent total memory and at least 21,474,836,480 free bytes in BOTH CUDA
and SMI samples. The gate writes identity, Slurm visibility, memory and error details on PASS
and failure. No physical-index fallback is allowed. Missing audit, timeout, unavailable UUID,
ambiguous visibility, low memory or any failed preflight means qualification remains BLOCKED.
No threshold may be lowered after observing a failure. A PASS does not authorize the 42-task
recovery; that requires a fully bound recovery contract and a separate user authorization.

Training, model weights/tokenizers, evaluation/scoring, parent/checkpoint access, V1B source
mutation, cancellation of existing jobs, cleanup, deletion, fallback and automatic retry are
forbidden. The 21 completed evaluations and all historical failure roots remain preserved.
