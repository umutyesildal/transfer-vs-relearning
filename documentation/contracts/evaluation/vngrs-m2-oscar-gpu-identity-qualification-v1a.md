# vngrs-m2-oscar-gpu-identity-qualification-v1a

Status: FROZEN / UNEXECUTED / SEPARATE EXACT USER AUTHORIZATION REQUIRED.

## Scope and preserved evidence

One metadata-only GPU qualification after the consumed V1 job 484040 failed before memory
sampling at UUID parsing. Original contract SHA-256
`4221b25cdd61a55751be85e9636b944a490cea441466d142d6a25e3535bbc34e`, its root and audit
`727168aa0acddf24c869c6e9b483508c4051a744133ae027289a9f5eb6747917` remain immutable.
No part of the 21-complete/42-failed V1B evaluation family is rerun or changed.

## Exact identities and correction

- Gate: `src/transfer_vs_relearning/study/m2_gpu_gate.py`.
- Gate SHA-256: `06afb59e45e9e93823e74b1429241544851e5a3da575920aebed0ff5aff9abb9`.
- Python: `/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python`.
- Lock: `/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/environment.lock.txt`.
- Lock SHA-256: `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`.
- HU checkout: `/vol/tmp2/yesildau/transfer-vs-relearning-monorepo-v1`.
- Branch: `agent/m2-three-model-vngrs-d0`; exact commit supplied in user authorization.
- Fresh root: `/vol/tmp2/yesildau/vnd_m2_oscar_gpu_identity_qualification_v1a`.
- Job name: `m2-gpu-id-qual-v1a`.

PyTorch v2.6.0 `torch/csrc/cuda/Module.cpp` lines 895–940 emits CUuuid strings as bare
8-4-4-4-12 hexadecimal, not SMI's GPU-prefixed form. The repair accepts exactly either form,
normalizes case and adds the GPU prefix, rejects nil/malformed/MIG/index inputs, and still
queries SMI only by that CUDA-derived UUID. It never substitutes another device.
Audit schema 2 persists bounded raw UUID text, type, Torch version and device name before
parsing, including on failure. Missing native identity remains a hard failure.

## Single authorized sequence

1. Ordinary non-force push of the exact authorized commit; preservation-check HU branch,
   clean tracked/untracked state and ancestor relation; fast-forward only. Stop on drift.
2. Verify exact commit, this contract SHA (from user authorization), gate and runtime-lock
   hashes. Run the 49 targeted tests locally and on HU with no CUDA/model access:
   `tests/study/test_m2_gpu_gate.py`, `tests/study/test_m2_eval_executor.py`,
   `tests/test_m2_eval_v2_matrix.py`, `tests/test_m2_finalizer_numeric_order_repair_contract.py`,
   `tests/study/test_m1_wave_executor.py`. Use no pytest cache or bytecode writes on HU.
   CPU checks use documented xfer-relearn Python, not system Python 3.6.
3. Require fresh root absent including broken symlinks, scratch-resolved paths, at least
   1 GiB available scratch and 1,024 available inodes, and no matching active job name.
4. Exactly one `sbatch --test-only`, then at most one real job: account yesildau, partition gpu,
   `gpu:a10080gb:1`, 8 CPUs, 64G host RAM, ten-minute limit, `--no-requeue`. No array,
   node/device override, fallback or retry. Preserve Slurm CUDA_VISIBLE_DEVICES unchanged.
5. Only after successful preflight/test-only, create fresh root/logs/tmp/cache. Bind stdout,
   stderr, TMPDIR, HF_HOME and XDG_CACHE_HOME there. Set PYTHONDONTWRITEBYTECODE=1,
   PYTHONPATH=src, HF_HUB_OFFLINE=1, HF_DATASETS_OFFLINE=1, TRANSFORMERS_OFFLINE=1.
6. Inside the job recheck exact commit, cleanliness and contract/gate/lock hashes before CUDA.
   Invoke `assert_allocated_gpu_memory(Path(root) / "gpu_identity_audit.json")` exactly once
   using the pinned Python. CUDA context and device metadata are allowed, no models/tensors.
7. Read compact logs/audit/accounting; hash the audit and append the local chronological result.
   Stop on failure; no second submission or automatic resumption.

## Acceptance and prohibitions

PASS requires exactly one Slurm-visible CUDA device, native CUDA UUID, A100-80GB, exact
SMI UUID equality, coherent total memory and both CUDA/SMI free samples >=21,474,836,480 bytes.
No thresholds are relaxed. Missing audit, timeout or any failed guard leaves qualification
BLOCKED. Mock tests do not establish live hardware qualification. PASS applies only to the
current allocation, not the historical V1B root cause or every future allocation.

Model/tokenizer/parent/checkpoint access, loading, inference, evaluation/scoring, training,
optimizer updates, source/prior-root mutation, cancellation, cleanup, deletion, fallback and
automatic retry are forbidden. No 42-task scientific recovery is authorized by this contract.
That requires its own frozen input-binding/recovery contract and explicit user authorization.
