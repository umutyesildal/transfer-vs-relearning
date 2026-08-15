# 119 - M1 Qwen Retention Seed-43 Replication Plan

**Date:** 24 July 2026  
**Status:** Complete; frozen replication failed; see Document 120  
**Authority:** Documents 117--118 and the adjudicated seed-42 artifact  
**Scope:** Qwen clean-English replay replication at 100 subjects / 500 facts

## 1. Decision and Evidence Gate

The outcome-transparent adjudication required by Document 118 is complete. It preserved the
original frozen artifact and produced a separate corrected artifact:

| Artifact | Decision | SHA-256 |
|---|---|---|
| original frozen summary | `retention_remediation_failed` | `78a2f440faede734e7480c6ab3c32b0b60f181d90895d136c6e4b413429e0487` |
| adjudicated summary | `replicate_replay_seed43` | `e7d52bfc0bfa9c0adda02f641ea6b0d8bc0620d33ecdf4599c8fa778270899a6` |

Only replay checkpoint 50 passes all corrected gates. Its historical length diagnostic remains
one, lexical-empty count is zero, synthetic intrusion is zero, and the sole short lexical row is
`qa_02` with continuation `navigation`. This corrected seed-42 result remains discovery evidence;
seed 43 is the independent replication gate.

## 2. Frozen Replication Contract

The replication changes only:

- model seed: 42 -> 43;
- data-order seed: 42 -> 43;
- run identity and absolute scratch output root.

Everything else remains fixed to the seed-42 replay condition:

- Qwen/Qwen2.5-1.5B frozen base snapshot;
- the same 100 subjects / 500 facts;
- the exact same 3,500 factual train and 500 validation rows;
- the exact same frozen 3,500/500 clean-English anchor rows and hashes;
- canonical + Form A + Form B curriculum;
- answer-only factual loss with `supervise_eos: false`;
- replay coefficient 0.5 and maximum 64 anchor tokens;
- LR `5e-5`, 36 epochs, effective factual batch, warmup, constant scheduler, and 252 updates;
- checkpoint retention schedule and earliest-passing-checkpoint rule;
- all factual, robustness, PPL, and integrity thresholds.

The dataset `split_seed` remains 42 because the population and rows are frozen; `data_seed=43`
changes the training order without regenerating or resplitting the scientific population.

## 3. Evaluation and Promotion Rule

After training, evaluate every retained seed-43 checkpoint using the same exact-prefix, A/B/C/D,
eight-cell robust intersection, WikiText-2 PPL, generic-completion, intrusion, and generation suites.
Report both integrity views:

- original strict sensitivity: any generation with at most two token IDs is flagged;
- corrected primary integrity: decoded output without any Unicode letter or number is empty.

The seed-43 candidate passes only if one checkpoint meets:

- exact-prefix >=90% globally and per relation;
- minimum A/B and C/D relation-form accuracy >=80%;
- robust intersection >=70% globally and per relation;
- PPL ratio <=1.25;
- zero lexical-empty generations and zero synthetic-subject intrusion;
- no dataset-integrity or generation-degeneration failure.

Select the earliest checkpoint passing all corrected primary gates. The original strict metric is
reported as a sensitivity result and cannot silently replace or relax another gate.

If seed 43 passes, freeze the selected model-only checkpoint with manifest and SHA-256 and open the
500-subject / 2,500-fact scale contract. If it fails, scale-up remains blocked; no third seed or
coefficient sweep opens automatically.

## 4. HU Execution Contract

The dedicated root is:

```text
/vol/tmp2/yesildau/m1_retention_seed43_v1
```

Expected training output is 11 checkpoints plus the final model. The conservative family reserve
is 250 GiB, using 20,401,094,656 bytes per checkpoint for preflight estimation. All model outputs,
optimizer state, caches, logs, and temporary files remain under scratch. No large artifact may be
written to HU home.

Execution order:

1. validate the exact source commit and seed-42 summary hashes;
2. run one mandatory storage/inode/path/queue preflight for this family;
3. submit one replay seed-43 A100-80GB training job with a three-hour limit;
4. confirm allocation, GPU state, progress, and clean initial stderr;
5. run the dependent post-training storage audit;
6. implement and run the frozen all-checkpoint seed-43 evaluation wave;
7. summarize, freeze the selected artifact if passing, and update Documents 100 and 119.

Closest measured runtime is seed-42 replay at 125.6 minutes. Expected seed-43 runtime after GPU
allocation is approximately 110--145 minutes. Return after roughly 15--20 minutes for the first
meaningful checkpoint/progress check; do not submit a duplicate while progress continues.

## 5. Current Holds

- seed-43 implementation/test/preflight/submission: **OPEN**;
- 500 subjects / 2,500 facts: **HOLD pending a passing seed-43 evaluation**;
- M2 and M3: **HOLD pending the mandatory 500-subject gate**.

## 6. Submission Record

Implementation commit `b60eed18c78c274d6849e2bc98ee35bd86a0126e` passed 62 relevant tests
locally and on HU plus shell syntax validation. The first invocation attempted to execute the
non-executable submit script directly and stopped with `Permission denied` before any Slurm job was
created. Calling the reviewed script through `bash` then submitted the family exactly once:

| Role | Slurm ID | Initial state |
|---|---:|---|
| mandatory family preflight | `411323` | RUNNING on `gruenau`; initial stdout/stderr empty |
| Qwen replay seed-43 training | `411324` | PENDING on successful preflight dependency |
| post-run storage audit | `411325` | PENDING on training terminal-state dependency |

The preflight manifest target is
`/vol/tmp2/yesildau/m1_retention_seed43_v1/preflight/family_411323.json`. Do not submit a duplicate.
Training begins only if preflight verifies home/capacity/inodes, resolved paths, source commit,
frozen dataset/anchor hashes, both seed-42 summary hashes, the sole step-50 candidate, and the
250-GiB family reserve.

## 7. Training Completion and Evaluation Launch

Preflight 411323 passed at commit `b60eed18c78c274d6849e2bc98ee35bd86a0126e` with home
8,298,764 KiB (approximately 7.91 GiB), `/vol/tmp2` approximately 115 TiB free at 3% inode use,
the 250-GiB reserve, both seed-42 summary hashes, fixed seed/data-seed 43, and all destinations on
scratch. Training 411324 completed 252/252 updates on `gruenau9` in 2:00:27 with exit code 0:0,
all 11 checkpoints (25 through 252), a complete training manifest, and no traceback/OOM/runtime-
error/NaN/Inf signature. The run tree is approximately 98 GiB. Final-model weight SHA-256 is
`3941bda1dcf9c74233fc12a3fcc46df4e6a2f1c6aa96b9bbbca6efe8340eaaad`.

Audit 411325 passed the material storage checks: home remained approximately 7.91 GiB, no new
large home file appeared, and `/vol/tmp2` remained approximately 115 TiB free at 3% inode use. Its
only stderr is the known cluster `sacct`/Munge failure; `scontrol` fallback independently records
training `COMPLETED` and exit 0:0.

Training loss is not a promotion gate. Commit `da0ca665ec20a583bff82ba29f95a1d863620bb4`
implements the frozen 11-checkpoint evaluation and passed 63 relevant tests locally and on HU plus
all shell/Python syntax checks. The following chain was submitted once:

| Role | Slurm ID | Initial state |
|---|---:|---|
| checkpoint-manifest/config preparation | `411329` | RUNNING on `gruenau`; initial stderr empty |
| mandatory evaluation preflight | `411330` | dependency-held after preparation |
| 11 checkpoint evaluations, throttle 3 | `411331_[0-10%3]` | dependency-held after preflight |
| corrected-primary + legacy-sensitivity summary | `411332` | dependency-held after array |
| evaluation storage audit | `411333` | dependency-held after array |

Dependency inspection confirmed the full chain. Do not duplicate it. Preparation may spend several
minutes hashing 11 read-only checkpoint manifests. After GPU allocation, the evaluation wave is
expected to take approximately 1.5--3 hours on RTX3090 nodes. Recheck preparation/preflight and
first task allocation in approximately 5--10 minutes.

Preparation 411329 and evaluation preflight 411330 subsequently passed. The frozen registry has
11 tasks and SHA-256 `6aee03197c2464d4cc3d3fe245705799f3d10021e8ab69092108269218c5233f`;
the source training-manifest SHA-256 is
`266e2311e4805c7b9c83e53ff734bef3ed50fcadfecf1b39297012603da0c73b`. Preflight recorded home
8,298,880 KiB, approximately 114 TiB available on `/vol/tmp2`, 3% inode use, a 30-GiB compact
evaluation reserve, and exact commit `da0ca665ec20a583bff82ba29f95a1d863620bb4`.

Tasks 411331_0/_1/_2 entered RUNNING on `guppi5`, `guppi5`, and `guppi8`; the remaining tasks are
correctly array-throttle-held. At approximately ten minutes, all three stderr files were zero bytes
and their hard suites had reached 1,950/4,000, 1,950/4,000, and 2,100/4,000 probes. No completed
checkpoint summary exists yet. Leave the wave running and do not duplicate it; recheck in roughly
20--30 minutes for first-task completion and array turnover.

All 11 evaluations, summary 411332, and audit 411333 subsequently completed. The frozen decision is
`seed43_replication_failed`; no checkpoint passes every corrected gate. Step 50 passes PPL at
1.1869 and all gates except minimum C/D, which is 72% because profession/Form-C is 72% direct and
78% QA. Step 75 passes factual/robustness gates but PPL ratio is already 2.755. Document 120 is the
result authority. The 500-subject scale gate remains HOLD and no third seed or coefficient sweep is
opened automatically.
