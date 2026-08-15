# 113 - Turkish Bridge Parallel Training Plan And Launch

**Date:** 2026-07-22  
**Status:** IMPLEMENTED LOCALLY; commit/push and HU submission pending.

## 1. Objective

Run the bounded Phase 109B Turkish bridge adaptation from the two frozen M1 endpoints selected in
Documents 109 and 112:

- Qwen2.5-1.5B update 50;
- the selected Document 104 SmolLM2-1.7B endpoint.

This is a feasibility/model-selection pilot on 100 subjects and 500 facts. It is not M2, M3, a
seed-43 replication, a retention intervention, or a scale-up.

## 2. Frozen Comparison

Both tasks use the finalized Document 110 Turkish Wikipedia corpus and the exact Contract V2
artifact whose manifest SHA-256 is:

```text
f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e
```

The two models receive the same frozen 1,000-document raw source pool and the same model-token
budget. Tokenization and resulting unused surplus blocks remain model-specific and are already
recorded in Document 112.

| Setting | Frozen value |
|---|---:|
| block size | 512 |
| per-device batch | 2 |
| gradient accumulation | 8 |
| effective blocks/update | 16 |
| low endpoint | step 32 / 262,144 model tokens |
| full endpoint | step 128 / 1,048,576 model tokens |
| learning rate | 1e-5 |
| scheduler | constant with 4 warmup steps |
| loss | full-sequence CLM |
| seed / data seed | 42 / 42 |
| checkpoints | 32, 64, 96, 128 plus final model |

The independent variable in this pilot is model family and frozen M1 starting point. No
post-outcome threshold, prompt, eligible set, corpus, dose, or checkpoint schedule changes.

## 3. Submission Wave

One reusable submission script creates exactly three dependent Slurm components:

1. a single CPU family preflight;
2. a two-task GPU array `0-1%2`, allowing Qwen and SmolLM2 to train concurrently;
3. one `afterany` family storage audit after both array tasks reach terminal state.

The preflight recomputes and validates all 16 Contract V2 artifact hashes, exact model/tokenizer
scratch paths, output nonexistence, home usage, scratch bytes/inodes, symlink destinations, update
budget, checkpoint count, and the frozen 110,721,074,308-byte reserve. Training cannot start unless
it passes, and each GPU task rejects a preflight manifest older than one hour.

Each task requests one A100 80 GB GPU. Before model load it prints the allocated GPU identity and
queries active compute processes. Any pre-existing/orphan compute process causes an immediate
failure before training, preventing recurrence of the earlier unexplained 72.4 GiB GPU occupancy
failure.

## 4. Storage And Retention

All outputs are absolute scratch paths:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/training/qwen
/vol/tmp2/yesildau/turkish_bridge_v1/training/smollm2
/vol/tmp2/yesildau/turkish_bridge_v1/cache
/vol/tmp2/yesildau/turkish_bridge_v1/tmp/training
/vol/tmp2/yesildau/turkish_bridge_v1/logs
```

Expected active family storage is 85.17 GB; preflight requires the frozen 110.72 GB reserve. All
four resumable checkpoints per model are retained through evaluation. After endpoint selection and
SHA-256 verification, step 32 and final model-only artifacts are retained; intermediate optimizer,
scheduler, RNG, and trainer state become cleanup candidates. No cleanup is part of this launch.

The post-run audit checks home usage, capacity, inodes, `artifacts`/`runs` resolutions, every home
file above 500 MB, per-model scratch size, and training-manifest presence. It runs even if a
training task fails and does not convert a scientific/runtime failure into a pass.

## 5. Expected Runtime And Checks

Based on the previous 1.5--1.7B jobs and the smaller 128-update/8,192-token-per-update budget:

- expected training after GPU start: approximately 20--45 minutes per task;
- safe Slurm limit: 90 minutes;
- first health check: immediately after start, then approximately 10 minutes later;
- the two tasks run in parallel, so family wall time is governed by the slower task plus queueing;
- evaluation is a separate later wave and is not submitted here.

At startup verify array state, node, A100 allocation, `gpu_preflight=clean`, resolved scratch paths,
initial manifest creation, checkpoint/output growth, and absence of traceback/OOM. Quiet logs alone
do not justify a duplicate submission.

## 6. Implementation Verification

The implementation adds dedicated preflight, training, post-audit, and submission launchers plus
tests for:

- scratch-only Slurm stdout/stderr and output roots;
- parallel two-task array and A100 request;
- orphan GPU-process rejection;
- combined reserve/checkpoint disclosure;
- `afterok` preflight and `afterany` audit dependencies;
- mandatory large-home-file audit.

Local shell syntax and whitespace checks pass. The targeted suite passes 45 tests; the complete
available suite passes 179 tests with four optional environment skips.

## 7. Stop Conditions

Do not train if the preflight fails, either output root already exists, Contract V2 hashes change,
home exceeds approximately 10 GiB without explanation, scratch cannot cover 110.72 GB, a model or
tokenizer resolves into HU home, or an allocated GPU already contains a compute process. Do not
retry or submit duplicates until the exact cause and partial scratch state are inspected.

Passing training is not passing the bridge pilot. The later frozen evaluation must compare M1,
step 32, and step 128 in EN→EN, TR→EN, TR→TR, English PPL, and Turkish PPL before any model is called
promising.

## 8. Initial HU Launch Record - 2026-07-22

The implementation was committed and pushed as `a1a0286`, then HU was fast-forwarded to exact
commit `a1a0286430ab4b32e4f812ce4c72aa708f1669ef`. Shell syntax and the authoritative 45-test subset
passed on HU. Both canonical training output roots were absent and the user queue was empty before
submission. Historical artifact-symlink migration state was left untouched.

The dependent wave was submitted exactly once:

| Job | Role | Initial observed state |
|---:|---|---|
| 411196 | combined home/capacity/inode/path/hash preflight | RUNNING on `gruenau`; stderr 0 bytes |
| 411197_[0-1%2] | Qwen and SmolLM2 parallel A100 training | PENDING on `afterok:411196` |
| 411198 | family post-run storage audit | PENDING on `afterany:411197` |

At the last immediate check, preflight 411196 had run for approximately 40 seconds and remained in
the bounded HU-home `du` stage with no stdout or stderr. No GPU job had started and no training
output existed yet. This quiet period is not treated as a failure and no duplicate is authorized.
Recheck in approximately 3--5 minutes; once the training tasks start, inspect both GPU preflight
records and report a 20--45 minute expected training window.

## 9. Initial GPU Wave Result And Retry Rule - 2026-07-22

Preflight 411196 passed with empty stderr. It recorded home at 8,297,796 KiB, `/vol/tmp2` with
123,067,155,456 KiB available (approximately 115 TiB), 3% scratch inode use, the exact Contract V2
hash, all 16 artifact hashes, correct scratch paths, four checkpoints plus one final model per
model, and the required 110,721,074,308-byte reserve.

Both array tasks were then allocated distinct A100 80 GB devices on `gruenau9`, but the GPU guard
found a foreign Python compute process on each device before model load:

| Task | Model | Foreign PID | Foreign process memory | Result |
|---:|---|---:|---:|---|
| 411197_0 | Qwen | 21881 | 31,490 MiB | safely aborted before output creation |
| 411197_1 | SmolLM2 | 20419 | 31,490 MiB | safely aborted before output creation |

Both processes belonged to a path under another HU user's home. No attempt was made to inspect,
signal, or terminate them. Slurm reported the node idle despite this non-Slurm-visible occupancy.
The earlier 72.4 GiB OOM class was therefore prevented as intended: neither model was loaded, no
training manifest/checkpoint/output root was created, and no training result is claimed.

Post-run audit 411198 passed with empty stderr. HU home remained approximately 8.0 GiB,
`/vol/tmp2` remained approximately 115 TiB free with 3% inode use, and only the three established
Conda/PyTorch/CUDA runtime libraries exceeded 500 MB in home.

Because the failure is node-local and both canonical output roots remain absent, one fresh retry is
permitted after a new family preflight. The reusable submitter now accepts a validated optional
node-exclusion list. The retry will exclude `gruenau9` while retaining the A100 80 GB request,
forcing eligibility onto `gruenau10`. It does not bypass the per-GPU process guard: if the newly
allocated GPU is occupied, the corresponding task must again stop before model load. No model,
data, budget, seed, optimizer, checkpoint, or scientific gate changes.

## 10. Clean-Node Retry Submission - 2026-07-22

The node-exclusion support was committed and pushed as `b596c48`, synchronized on HU as exact
commit `b596c48380af00e9ba59495c056a997689f82a9b`, and passed shell syntax plus the authoritative
10-test launcher subset. The queue was empty and both training roots remained absent.

One fresh retry wave was submitted:

| Job | Role | Initial observed state |
|---:|---|---|
| 411200 | fresh complete family preflight | RUNNING on `gruenau`; stderr 0 bytes |
| 411201_[0-1%2] | parallel A100 retry | PENDING on `afterok:411200`; `ExcNodeList=gruenau9` |
| 411202 | retry post-run storage audit | PENDING on `afterany:411201` |

The exclusion is recorded by Slurm, not merely requested in prose. At the initial 11-second check,
preflight was healthy and no GPU task had started. Recheck after approximately 3--5 minutes; do not
submit another retry. When 411201 releases, both tasks must report `gruenau10`, zero foreign compute
processes, and `gpu_preflight=clean` before training output is accepted.

## 11. Retry Startup Result - 2026-07-22

Fresh preflight 411200 passed with empty stderr and the same frozen storage/hash/path evidence.
The two retry tasks received different A100 80 GB devices on `gruenau10`, but their startup states
differed:

| Task | Model | GPU startup evidence | Current result |
|---:|---|---|---|
| 411201_0 | Qwen | foreign VLLM process using 74,166 MiB plus Firefox using 87 MiB | safely aborted before model load; no output root |
| 411201_1 | SmolLM2 | 17 MiB idle baseline; `gpu_preflight=clean` | RUNNING with empty stderr |

The Qwen guard again prevented a predictable OOM and no foreign process was inspected beyond the
standard `nvidia-smi` process record, signalled, or terminated. The SmolLM2 task is scientifically
valid: after approximately five minutes its scratch tree was about 20 GiB and checkpoints 32 and
64 were complete under the canonical run directory. Its initial training manifest exists and the
task remains active on `gruenau10`.

Post-audit 411202 correctly remains pending until the complete array is terminal. Do not interrupt
SmolLM2 and do not submit another Qwen job while this family is active. Recheck SmolLM2 after
approximately 5--10 minutes. Once it and the audit complete, inspect the final manifest, all four
checkpoints, metrics, storage state, and then prepare a separate Qwen-only infrastructure retry if
a genuinely clean GPU can be allocated. No Qwen scientific setting may change merely because its
A100 allocations were contaminated.

## 12. SmolLM2 Training Completion And Family Audit - 2026-07-22

SmolLM2 task 411201_1 completed successfully. Its manifest records start
`2026-07-22T05:42:43Z`, completion `2026-07-22T05:50:42Z`, and `status: complete`, for an end-to-end
wall interval of approximately 7 minutes 59 seconds. The Trainer-reported training runtime was
350.095 seconds.

| Metric | Result |
|---|---:|
| optimizer updates | 128 / 128 |
| train blocks available | 8,392 |
| validation blocks | 1,767 |
| train loss | 2.237035 |
| final validation loss | 2.242527 |
| implied endpoint validation PPL | approximately 9.42 |
| checkpoint directories | 32, 64, 96, 128 |
| final model | present |
| retained scratch size | approximately 42 GiB |

The implied PPL is descriptive only. It is not the frozen Turkish-PPL ratio or promotion decision;
the later evaluator must compute M1, step-32, and step-128 values through the same evaluation path.

SmolLM2 stderr was 86,555 bytes and therefore is not reported as empty. Inspection showed only
Trainer/tqdm progress-bar output, model-shard writes, and normal evaluation progress. There was no
traceback, CUDA OOM, NaN report, failed assertion, or runtime/scientific error. Stdout ended with
the launcher's independent `status=training_complete` assertion.

Family audit 411202 then completed with empty stderr and
`status=post_run_storage_audit_complete`. HU home remained approximately 8.0 GiB; `/vol/tmp2`
remained approximately 115 TiB free with 3% inode use; `artifacts` and `runs` still resolved to
scratch; and the only home files above 500 MB were the three established Conda/PyTorch/CUDA
libraries. The audit correctly reported Qwen's root absent and SmolLM2's 42 GiB root plus complete
manifest.

The training wave is operationally closed as one valid SmolLM2 completion and one infrastructure-
blocked Qwen non-run. All SmolLM2 checkpoints and optimizer states remain on scratch pending frozen
evaluation and selection; no cleanup is authorized yet. The next implementation step is a fresh
Qwen-only preflight/launcher that does not require the now-valid SmolLM2 output root to be absent.
No Qwen retry has been submitted at this point.
