# vngrs-m2-oscar-eval-v2-recovery-v1

Status: FROZEN / UNEXECUTED / EXACT SHA-BOUND USER AUTHORIZATION REQUIRED.

## Objective and immutable scientific scope

Recover exactly source task indices 21–62, not completed indices 0–20. These are 19 Qwen M2,
20 SmolLM M2 and three M1-parent OSCAR-only tasks. The original 63-task matrix, model manifests,
FP16, harness tasks, corpus/probe identities, seeds, checkpoint grid, gates and analysis remain
unchanged. Original V1B and both qualification roots are read-only. No retraining is involved.

Source: `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_execution_v1b`.
Fresh destination: `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1`.
HU checkout: `/vol/tmp2/yesildau/transfer-vs-relearning-monorepo-v1`.
Branch: `agent/m2-three-model-vngrs-d0`; exact commit supplied separately by user.

## Frozen bindings

- Config `configs/evaluation/m2_eval_recovery_v1.json` SHA-256:
  `edf50ac91ad71e162ae11fdc668473957086161ded652e69638ec6f8719abfdf`.
- Recovery module `src/transfer_vs_relearning/study/m2_eval_recovery.py` SHA-256:
  `86a28dc65c6cb89d02e4067be2280b00a959bba711f7bb91efa69e82cdbd6fb6`.
- Entrypoint `scripts/study/execute_m2_eval_recovery.py` SHA-256:
  `eba92bbb7d431541d27661d9f066a7c2f777a124c3d7c1cc1b4e8922e7dc93aa`.
- Reused executor SHA-256: `c7c8f38f70b811cce9440d9f6b75ea505d38d2f61d31a691df95ef2da45d0a2b`.
- Qualified GPU gate SHA-256: `06afb59e45e9e93823e74b1429241544851e5a3da575920aebed0ff5aff9abb9`.
- V1A PASS audit SHA-256: `ee2c7f395569c8b37f94e6c4fbc0a82eb5e475f32df695008f0e88591563059f`.
- Source inventory canonical SHA-256:
  `bc930b814634530538c7ec4cb3642ffe1d5eed10e3d6ebe150bc75d3e8ec4839`.
- Source matrix SHA-256: `5b55e11b1fa9548e5d4f942c22534eb807a5f2cda498a3f320678608df82442c`.
- Existing OSCAR heldout SHA-256: `0b1eddf91704e2b9b2ef345670141284b7c51002972809f8543907302323c36d`.
- Runtime: `/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python`.
- Environment-root `environment.lock.txt` SHA-256:
  `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`.

The read-only preparation inventory covers all 63 state directories: 1,288 files,
1,091,411,786 bytes. Each state has a sorted relative-path/byte/SHA list whose canonical JSON
hash is bound in the inventory. The outer canonical JSON uses sorted keys and compact separators.
Five control hashes, all 63 task-result hashes and the heldout hash are included. Every failed
state has exactly two configs and its original GPU-guard failure, with no scoring artifacts.
The config binds the exact control and qualification paths/hashes; source matrix transitively
binds the exact 63 model-manifest identities and original M1 projection.

## Single execution after authorization

1. Ordinary non-force push of exact authorized commit and clean preservation-checked HU
   fast-forward. Verify contract/config/module/entrypoint/executor/gate/lock hashes and run the
   63 targeted CPU-only tests: recovery, GPU gate, M2 executor, M2 matrix, numeric-order repair
   contract and M1 executor test modules. No pytest cache/bytecode writes on HU.
2. Require destination absent including broken symlink, exact scratch path resolution, 40 GiB
   available scratch, 8,192 free inodes, no matching recovery jobs and qualification PASS.
   Create only new destination subdirectories; four scheduler test-only checks must pass before
   any real job. A failed check stops the wave; root is not reused automatically.
3. One `longrun` CPU preflight: account yesildau, four CPUs, 64G, two-hour limit. Reproduce the
   full frozen inventory; validate source task order, runtime, frozen dataset/probe/corpus
   identities, model manifests and M1 factual baselines. No corpus reconstruction or model load.
   Create only read-reference symlinks to 21 complete states, existing OSCAR corpus and two
   control inputs. Persist reproduced inventory and preflight PASS under the new root.
4. One `afterok` A100 canary evaluates task 21 (Qwen M2-A update152), once. This is one of the
   42 required scientific states, not an extra evaluation. Resources: account yesildau,
   partition gpu, `gpu:a10080gb:1`, eight CPUs, 64G, time 2-12:00:00, no requeue.
5. One `afterok` array `22-62%6` with identical GPU resources. No completed state is eligible.
   Every task checks immutable identities, source links, successful preflight, completed canary,
   fresh local destination and shared STOP marker before invoking the unchanged evaluator.
   CUDA UUID/SMI identity and both >=20 GiB free-memory samples precede any model load.
6. One `afterany` CPU finalizer dependent on that array: partition std, two CPUs, 8G, one hour.
   Reproduce the original source inventory again, validate all preserved links, then run existing
   63-state completeness and scientific analysis over the combined read-reference/new-output view.
   Analysis is permitted only at 63/63 complete, using unchanged 10,000-draw seed42 bootstrap.

Names: `m2-rec-pre`, `m2-rec-canary`, `m2-rec-array`, `m2-rec-final`.
Entrypoint `start` requires config/contract/contract SHA/exact commit/repo and explicit
`exact_sha_bound_user_authorization_received`. Use only this recovery launcher, never old `start`.
All logs/tmp/cache/HF_HOME/XDG_CACHE_HOME stay under new root; the frozen dataset cache is reused
offline. No CUDA_VISIBLE_DEVICES override. Every real job uses `--no-requeue`. Submission IDs
are recorded after each successful submission; ambiguous submission stops without retry.

## Failure behavior and prohibitions

Caught task/input failures create a shared STOP directory; subsequent tasks exit before model
loading. Already-running peers (at most six) may finish. SIGKILL/node loss cannot reliably write
STOP, so this is not a global scheduler cancellation guarantee. No foreign or existing job is
cancelled. If preflight/canary fails, dependencies may remain never-satisfied; do not cancel,
release or resubmit without authority. Finalizer remains incomplete on missing/failed results.

Parent/checkpoint weights are read-only inference inputs for only the 42 listed tasks.
Training, optimizer updates, checkpoint writes, corpus reconstruction/downloads, source/prior-root
mutation, rescoring completed states, cleanup/deletion, fallback, threshold/metric/precision
changes, second wave and automatic retry are forbidden. Preparation is not execution authority;
the user must approve this final contract SHA-256 and implementation commit before publication
or submission.
