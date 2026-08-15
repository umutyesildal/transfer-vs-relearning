# 107 - Qwen Checkpoint Retention Pareto Diagnostic Plan

**Date:** 2026-07-19  
**Status:** Executed and complete; see Document 108. No checkpoint was promoted.

## 1. Motivation

Document 106 found no passing model family. Qwen is the closest failed candidate: its update-252
endpoint passes every factual-storage and prompt-robustness gate, but generic PPL rises from
14.698839 to 21.471761 (ratio 1.460779), above the frozen 1.25 limit. The retained Qwen training run
contains checkpoints every 25 optimizer updates plus update 252. Before creating a new retention
intervention or deleting intermediate checkpoints, this plan asks whether generic drift accumulated
later than factual robustness.

This is explicitly post-hoc exploratory analysis. A passing retained checkpoint cannot be promoted,
used for seed 43, or authorize scale-up. It may only nominate a fixed update for a new confirmatory
plan whose endpoint rule is frozen before retraining.

## 2. Frozen source artifacts

- Model family: pinned `Qwen/Qwen2.5-1.5B` from Document 106.
- Training run: the completed seed-42 Qwen run under
  `/vol/tmp2/yesildau/m1_cross_family_screen_v1/training/qwen/`.
- Checkpoint steps: `25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252`.
- Dataset, probe registry, normalization, candidate sets, tokenization, and scoring remain identical
  to Documents 105--106.
- Frozen Qwen base PPL: `14.6988390227992`, using the already verified WikiText-2 token stream with
  SHA-256 `be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f`.

The update-252 checkpoint is evaluated uniformly with the intermediates rather than substituting a
different evaluator output. Its result must agree materially with the Document 106 final endpoint;
otherwise the wave fails integrity review.

## 3. Immutable evaluation suite

Every checkpoint receives:

1. 500 canonical exact-prefix probes;
2. 4,000 Forms A/B/C/D under direct and QA scaffolds;
3. per-cell and eight-cell robust intersections;
4. relation-swapped forced choice and paired relation binding;
5. trained-checkpoint WikiText-2 PPL and the frozen 30-prompt generic controls.

The base model is not redundantly reevaluated for every checkpoint. PPL ratios use the frozen base
PPL above only when the scored-token stream hash matches Document 106.

## 4. Frozen gates and exploratory selection rule

The thresholds are unchanged:

| Gate | Requirement |
|---|---:|
| Exact-prefix | >=90% |
| Minimum trained A/B relation-by-scaffold cell | >=80% |
| Minimum held-out C/D relation-by-scaffold cell | >=80% |
| Global robust intersection | >=70% |
| Minimum per-relation robust intersection | >=70% |
| PPL ratio | <=1.25 |
| Integrity/generic behavior | No leakage, empty collapse, or synthetic intrusion |

If multiple checkpoints satisfy every gate, the exploratory nominee is the **earliest optimizer
update**. This minimizes unnecessary exposure and is frozen before the trajectory is observed. If
none pass, no checkpoint is nominated and the next admissible plan is a Qwen retention intervention
(general-language replay or explicit base-retention regularization). If a checkpoint is nominated,
it still requires a separate confirmatory retrain with that fixed endpoint and a precommitted
replication rule.

## 5. Execution and compute

Use scratch root:

```text
/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1
```

The eleven evaluations run as a Slurm array with at most three concurrent A100 80GB tasks. Exclude
`gruenau10` because two independent project jobs encountered the same persistent 72.43-GiB foreign
GPU process there. Simultaneous tasks use isolated output/config/tmp namespaces. Each task produces
no model checkpoint and retains only compact evaluator evidence.

Expected runtime is approximately 20--35 minutes per task. With three-way concurrency the safe
family wall-time estimate is 90--150 minutes including queueing and checkpoint load variance.
Expected new storage is well below 100 GiB; the retained training checkpoints already exist and are
not copied.

## 6. Mandatory preflight and stop conditions

Before submission:

- verify exact repository commit and full HU tests;
- verify the completed Qwen training manifest and all eleven checkpoint directories;
- hash every generated local model manifest, registry, launcher, general corpus, and probe registry;
- verify every result namespace is absent and resolves under approved scratch;
- record HU home usage, scratch capacity/inodes, expected tasks, output estimate, and retention;
- inspect the queue and reject duplicate checkpoint tasks;
- exclude `gruenau10` from GPU tasks.

Stop without submission if any checkpoint is missing, a model manifest cannot be frozen, an output
namespace exists unexpectedly, source hashes disagree, home exceeds the protected limit, or the
wave would not fit live scratch capacity/inodes.

## 7. Required output and next decision

The summarizer must produce a machine-readable per-checkpoint CSV/JSON containing all gates,
generic metrics, pass/fail flags, and the frozen earliest-passing rule. The chronological result
belongs in:

```text
documentation/108_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_RESULT.md
```

Until Document 108 exists, no new training is authorized. Intermediate checkpoints must not be
cleaned before this diagnostic and its artifact audit are complete.

## 8. Implementation and submission record

Implementation was frozen in `transfer-vs-relearning` commits `89e373d`, `94c8dde`, and
`dc54f68`. The final HU checkout is `dc54f687b753856db7c936aec693d801e06b2f90`, and the complete HU
test suite passed at that commit (171 tests). The implementation adds deterministic checkpoint
preparation, a guarded preparation-resume mode, a family-level storage preflight, an eleven-task
maximum-three-concurrent evaluation array, and frozen token-stream/gate summarization.

Three operational corrections occurred before an evaluation could start:

1. the first helper created an empty `logs/` directory before the strict namespace-absence check;
   the directory was verified empty and removed with `rmdir`;
2. login-session hashing outlived the disconnected SSH client and ultimately completed all eleven
   model manifests, configs, `checkpoint_registry.csv`, and `wave_manifest.json`; a later Slurm
   preparation job correctly refused to overwrite this completed preparation;
3. HU rejected the nonexistent `standard` partition before creating any job; both CPU launchers
   were corrected to the actual `std` partition.

The completed registry was independently checked to contain exactly steps
`25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252` and eleven existing model manifests. Failed
dependency jobs `410114` and `410115` were cancelled because they could never run. The active
submission is:

| Role | Job ID | State at last check |
|---|---:|---|
| Superseded family preflight | `410116` | `COMPLETED`; storage gates passed |
| Failed evaluation array | `410117_[0-10%3]` | all tasks failed before model load |
| Active mandatory family preflight | `410128` | `COMPLETED`; `PASS` |
| Active Qwen checkpoint evaluation array | `410129_[0-10%3]` | tasks 0--2 `RUNNING` |

Preflight `410116` passed with HU-home usage `8,296,684 KiB` (approximately 7.91 GiB) and the
100-GiB family estimate fitting current scratch capacity/inodes. Array `410117` then exposed an
inline CSV-parsing launcher defect: every task reached `sha256sum ''` and stopped before model load,
GPU evaluation, or result-namespace creation. Commit `88fef9a` replaces the inline parser with a
tested field resolver; the full HU suite then passed 172 tests at
`88fef9a742be0854120fd5065d04a9105378e86d`.

The replacement preflight `410128` completed with `PASS` at `2026-07-19T15:36:55Z`. Array tasks
`410129_0`, `_1`, and `_2` then entered `RUNNING` together on `gruenau9`; tasks 3--10 are correctly
held by the `%3` array limit. No nonempty array stderr was present at the initial 39-second check,
and the excluded `gruenau10` node is not in use. Expected end-to-end duration remains approximately
90--150 minutes after the array became eligible. Do not submit a duplicate while `410129` is
present.

## 9. Completion pointer

Array `410129_[0-10%3]` completed all eleven hard, exact, and generic-capability evaluations.
Document 108 supersedes the active-status wording above and records the corrected eight-cell
summary, frozen decision, artifact hashes, and post-run storage audit. No retained checkpoint
passed every gate.
