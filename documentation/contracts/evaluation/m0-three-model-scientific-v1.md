# Three-model scientific M0 eval-v1 execution contract

**Status:** `frozen` | **Execution:** `not authorized` | **Date:** 2026-08-16

## Purpose

Run the first scientific eval-v1 baseline on the exact OLMo, Qwen and SmolLM base assets. The
three models form one cohort, but each model has an independent eight-lane DAG. All three
preflights must pass before any job is submitted. This contract freezes identities and behavior;
it does not itself authorize HU, Slurm, GPU, inference or scoring.

## Frozen family identity

- eval contract: `documentation/contracts/evaluation/eval-v1.md`, SHA-256
  `72403598d7f9c8ba35bdfcc3e4791d097d41c6ef8f4e79c55cf9a6f34a37479e`;
- family manifest: `configs/evaluation/m0_scientific_three_model_v1.yaml`, SHA-256
  `264525095a3f67b5899771069ad227a41ed431de14fd98c38168690787d2bf5d`;
- implementation commit: `ea4e01de68e80cd33136674aa3cb59dc4547cfbd`;
- operator: `scripts/study/run_three_model_m0_evaluation.py`;
- family root: `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1`;
- model order: `olmo`, `qwen`, `smollm`;
- execution-ready: true;
- execution-authorized: false.

| Model | Exact config | SHA-256 |
|---|---|---|
| OLMo-2-0425-1B | `configs/evaluation/m0_scientific/olmo_m0_eval_v1_scientific_v1.yaml` | `b6dc833f6a16da4c4bb95bb54e69f2f55c998b72066f748688f1043d44e8caf9` |
| Qwen2.5-1.5B | `configs/evaluation/m0_scientific/qwen_m0_eval_v1_scientific_v1.yaml` | `2824e92044c6df7a82e698b012bd99d64e98f8c21684b0b2878f174e1177df76` |
| SmolLM2-1.7B | `configs/evaluation/m0_scientific/smollm_m0_eval_v1_scientific_v1.yaml` | `76311220bf15bd4965b3c26065df23b283a03a603e2f855cb339e95f01683c28` |

## Per-model lanes

Each model runs eight independent lanes after its read-only CPU preflight:

1. full WikiText BPB;
2. full Pile-10k BPB;
3. full 67-subtask BLiMP;
4. HellaSwag plus three WinoGender slices;
5. full 16-subtask TurBLiMP;
6. trwiki-20260601 cross-domain Turkish byte-PPL/BPB;
7. the 12,000-row bilingual factual suite;
8. generation integrity and frozen generic completions.

There are 24 GPU lanes across the three models. No scientific `--limit` or factual `probe_limit`
is permitted. The 1,500-row dense factual panel is derived from the matching full rows at M0 and
is not rescored.

## Parallel and fallback policy

The operator first evaluates every local/read-only identity check for all models. A blocker in one
model submits zero jobs for all models. When separately authorized, it creates three independent
DAGs and submits them without waiting in the agent process. Each lane receives the earliest route
within a frozen 900-second scheduler window, using declared capacity in this order:

1. V100-32GB;
2. A100-80GB;
3. RTX3090;
4. RTX6000;
5. RTXA6000.

This means RTX3090 is an explicit fallback when V100/A100 are unavailable. Route choice changes
only hardware/runtime metadata, never data, prompts, precision or metrics. Every GPU lane uses
FP16 and has a 24-hour Slurm limit. A final `afterany` job inventories each model; a second family
`afterany` finalizer combines the three raw statuses.

## Frozen inputs and preservation

- Harness environment lock:
  `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`;
- offline dataset content manifest:
  `0bd32f84bcf94b8208b35a32cdb9a0e311e7ba005392a7557f80c316d0dfd7fb`;
- source cache: 404 files / 413,883,554 bytes, read-only;
- full factual registry:
  `5125850a2db24c6b570971a58e9ba8a8586cabdec9084eb0e99bbd639691d93f`;
- trwiki validation split:
  `15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8`.

No network retrieval, model relocation, cache mutation, previous-root write, HU-home artifact,
training, corpus materialization, cleanup or deletion is allowed. Finalization rehashes the source
cache and invalidates the scientific bundle if a file is missing, changed or added.

## Result and failure semantics

Each lane writes raw logs, task/sample artifacts, runtime metadata and a content inventory. A model
bundle is complete only when all eight lanes, model manifest, environment lock and source-cache
identity pass. The raw finalizer writes `complete_raw_pending_normalization`; it never produces a
qualification result or a model PASS/FAIL. Cross-model normalization and eval-v1 gate computation
are a later deterministic step.

An incomplete lane remains `not_run`, `failed_pre_scoring` or `partial_invalid`. It is never zero,
never silently omitted and never triggers an automatic outcome-aware rerun. Partial submission is
preserved and does not automatically cancel already-submitted jobs.

## Expected duration

This is the first full 24-lane scientific run, so no exact wall-time claim is possible before the
first completed runtime ledger. The planned operational envelope is:

- CPU/offline preflight: typically minutes;
- short capability/generation lanes: tens of minutes to several hours;
- full Pile, BLiMP and 12,000-probe factual lanes: potentially several hours;
- conservative per-lane ceiling: 24 hours;
- family wall time if GPUs start near together: approximately 6–24 hours, plus scheduler queue;
- worst contracted ceiling after jobs start: 24 hours plus the short finalizers.

The operator returns immediately after submission. Progress is read with the `status` command; no
agent must stay blocked while Slurm runs.

## Commands after separate authorization

```bash
.venv/bin/python scripts/study/run_three_model_m0_evaluation.py preflight

.venv/bin/python scripts/study/run_three_model_m0_evaluation.py submit

.venv/bin/python scripts/study/run_three_model_m0_evaluation.py status
```

The current frozen configs deliberately set both family and per-model
`execution_authorized: false`. A new exact authorization-bound publication/correction is required
before `submit` can pass. Editing those booleans ad hoc is forbidden.
