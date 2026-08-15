# 114 - Qwen Turkish Bridge Clean-GPU Recovery Plan

**Date:** 2026-07-22  
**Status:** IMPLEMENTED LOCALLY; commit/push and HU submission pending.

## 1. Why A Separate Recovery Is Required

The two-model bridge family produced one valid SmolLM2 completion but no Qwen run. Qwen was stopped
before model load on two independent waves because its Slurm-allocated A100 contained foreign,
non-Slurm-visible compute work:

- job 411197_0 on `gruenau9`: foreign Python process using 31,490 MiB;
- job 411201_0 on `gruenau10`: foreign VLLM process using 74,166 MiB plus Firefox using 87 MiB.

Both canonical Qwen output attempts ended before creating the output root. The completed SmolLM2
run, its four checkpoints, final model, optimizer state, and 42 GiB scratch tree must remain
untouched. The two-model preflight cannot be reused because it correctly requires both original
roots to be absent.

## 2. Scientific Contract Is Unchanged

This is an infrastructure recovery, not a new condition. Qwen still uses:

- the frozen Qwen2.5-1.5B update-50 M1 endpoint;
- Contract V2 manifest hash
  `f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e`;
- the same 1,000-document Turkish Wikipedia dose;
- block size 512, batch 2, gradient accumulation 8;
- LR 1e-5, four warmup steps, full-sequence CLM;
- seed/data-seed 42;
- step 32 low endpoint and step 128 full endpoint;
- checkpoints 32/64/96/128 plus final model.

No corpus, token budget, update count, prompt, eligibility set, evaluator, threshold, optimizer, or
retention rule changes.

## 3. Qwen-Only Preflight

The new preflight validates only the still-absent Qwen destination while requiring the existing
SmolLM2 manifest to be complete with four checkpoints and a final model. It recomputes all 16
Contract V2 artifact hashes, verifies Qwen model/tokenizer scratch paths, checks home/capacity/
inodes/symlinks, and records the Qwen-only storage estimate.

| Storage item | Bytes |
|---|---:|
| estimated Qwen active output | 40,405,508,328 |
| Qwen-only reserve with 30% headroom | 52,527,160,826 |

The preflight refuses to run if Qwen's canonical root exists, SmolLM2 is missing/incomplete, home
exceeds the protected threshold, or the Qwen reserve no longer fits scratch.

## 4. Clean-GPU Selection

The recovery job is pinned to `gruenau10` and requests two A100 80 GB devices for a short single-
model job. This temporary over-allocation is a bounded response to Slurm allocating GPUs that it
reports idle while they contain external processes. It is not data parallelism: Qwen trains on
exactly one GPU and retains `world_size=1`.

Before Python/model load, the launcher:

1. enumerates exactly the two allocated GPU UUIDs;
2. records baseline memory and standard `nvidia-smi` compute-process rows for each;
3. selects the first GPU with zero compute processes and less than 1,024 MiB baseline use;
4. replaces `CUDA_VISIBLE_DEVICES` with only that selected UUID;
5. aborts before output creation if neither allocated GPU is clean.

The occupied spare is never used, inspected beyond standard GPU process metadata, signalled, or
terminated. The allocation is released as soon as the approximately 8--15 minute Qwen job ends.

## 5. Submission And Audit

One reusable submitter creates:

1. fresh Qwen-only preflight;
2. dependent Qwen recovery training;
3. one `afterany` post-run storage audit.

All logs, caches, temporary files, checkpoints, and final weights remain under
`/vol/tmp2/yesildau/turkish_bridge_v1`. After successful training, retain all Qwen and SmolLM2
checkpoints until the frozen bridge evaluation selects endpoints and verifies hashes. No cleanup
is part of this recovery.

Expected Qwen training time after GPU start is approximately 8--15 minutes, with a conservative
90-minute Slurm limit. Check startup immediately for the selected UUID and `gpu_preflight=clean`,
then recheck after approximately 10 minutes. Do not submit a duplicate while the job is active.

## 6. Verification And Stop Conditions

Local shell syntax and whitespace checks pass. The targeted suite passes 46 tests; the complete
available suite passes 180 tests with four optional environment skips.

Stop without training if the preflight fails, Qwen root exists, SmolLM2 evidence changes, Contract
V2 hashes change, fewer/more than two GPUs are visible, both GPUs contain compute processes, no GPU
is below the baseline-memory guard, or any path resolves to HU home. A stopped recovery does not
authorize hardware/recipe/model changes without a new documented decision.

## 7. HU Launch And Verified Startup - 2026-07-22

The implementation was committed and pushed as `4d709a9`, then HU was fast-forwarded to exact
commit `4d709a9c42b9585eb955290c5bce513548287bb8`. Shell syntax and the authoritative 11-test launcher
subset passed; Qwen's output root was absent, the complete SmolLM2 tree was present, and the user
queue was empty.

The recovery wave was submitted exactly once:

| Job | Role | Verified state |
|---:|---|---|
| 411204 | fresh Qwen-only storage/hash/path preflight | PASS; stderr empty |
| 411205 | two-A100 allocation, one-clean-GPU Qwen training | RUNNING on `gruenau10` |
| 411206 | post-run family storage audit | PENDING on `afterany:411205` |

Preflight 411204 recorded home at 8,297,888 KiB, `/vol/tmp2` with 123,023,581,184 KiB available
(approximately 115 TiB), 3% scratch inode use, the exact Contract V2 hash, Qwen output absence,
preserved complete SmolLM2 evidence, and the 52,527,160,826-byte Qwen reserve.

Job 411205 received two A100 80 GB devices. The first contained the already observed foreign VLLM
process at 74,166 MiB plus Firefox at 87 MiB and was rejected. The second had a 17 MiB baseline and
zero compute processes. The launcher selected only UUID
`GPU-5d089b0f-2824-0adc-2d93-1be85aa4ad86`, exported it as the sole training device, and printed
`gpu_preflight=clean`. Initial stderr was 0 bytes and the Qwen `training_manifest.json` was created
under the canonical scratch root. No checkpoint existed at the 17-second startup check, as
expected. Recheck after approximately 8--10 minutes; do not submit a duplicate.

## 8. Final Recovery Result And Storage Audit - 2026-07-22

Job 411205 completed successfully. The canonical run is:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/training/qwen/20260722T061622Z_turkish_bridge_qwen_seed42_480a83a5
```

The wall-clock interval was approximately 6m33s and Trainer runtime was 320.963s. The run produced
the frozen low-dose checkpoint at update 32, intermediate checkpoints 64 and 96, the full-dose
checkpoint at update 128, and `final_model`. It used 6,215 training blocks and 1,274 validation
blocks. Final train loss was 2.467925 and final validation loss was 2.592992. These losses are
training diagnostics, not the frozen English/Turkish PPL promotion result.

The retained Qwen tree is approximately 38 GiB. Its 66,212-byte stderr contains only ordinary
tqdm/model-write progress; no traceback, OOM, NaN, failed assertion, or GPU-process-guard failure
was found. Post-run audit 411206 passed with empty stderr. Home remained approximately 8.0 GiB;
`/vol/tmp2` retained approximately 115 TiB free with 3% inode use. The complete SmolLM2 tree
(approximately 42 GiB) was unchanged. No large artifact was written into HU home.

The recovery is therefore complete. Preserve both models' M0, M1, update-32, and update-128/final
endpoints until the separately frozen bridge evaluation wave has produced per-probe evidence,
PPL/retention metrics, selected manifests, and checksums. M2/M3 and scale-up remain on HOLD.
