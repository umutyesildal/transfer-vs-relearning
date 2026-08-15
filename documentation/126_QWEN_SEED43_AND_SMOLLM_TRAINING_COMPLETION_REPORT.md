# 126 — Qwen Seed-43 and SmolLM Training Completion Report

**Date:** 28 July 2026  
**Status:** All three training jobs completed successfully; factual/robust/PPL evaluation has not yet been run. This is a training-completion record, not a model-selection result.

## 1. Executive status

No project job remains active from this wave. Exact Slurm IDs `429991`, `429992`, `429993`, and `429994` returned no active queue row after completion. Preflight `429993` enabled Qwen training `429994`; each training manifest records `status: complete` and 36.0 completed epochs.

This establishes successful execution and retained checkpoints. It does **not** establish factual retrieval, prompt robustness, PPL retention, binding improvement, or a final M1. Those claims require the frozen held-out evaluation wave.

## 2. Completed-job ledger

| Condition | Slurm job | A100-80GB runtime | Start / completion (UTC) | Scratch training tree | Checkpoints |
|---|---:|---:|---|---|---:|
| SmolLM2-1.7B contrastive treatment | 429991 | 24,697.35 s (6 h 51 m 37 s) | 05:59:47 → 12:52:51 | `/vol/tmp2/yesildau/smollm_contrastive_binding_v1/training/seed42` | 11 |
| SmolLM2-1.7B matched factual-LM control (`lambda=0`) | 429992 | 3,042.56 s (50 m 43 s) | 06:14:54 → 07:06:16 | `/vol/tmp2/yesildau/smollm_binding_control_v1/training/seed42` | 11 |
| Qwen2.5-1.5B replay, independent seed-43 | 429994 | 16,040.27 s (4 h 27 m 20 s) | 06:19:59 → 10:51:04 | `/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1/training/replay_w0_5_seed43` | 11 |

Each condition retained updates 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, and 252, plus a final-model directory. The trees occupy about 109 GiB for each SmolLM condition and 98 GiB for Qwen seed-43. They remain scratch-only and have not been cleaned up.

## 3. SmolLM matched treatment/control contract

Both SmolLM runs use SmolLM2-1.7B, Relation V2 canonical-form-diversity data, 100 subjects / 500 facts, 3,500 train rows, 500 validation rows, seed/data seed 42, answer-only LM labels with EOS unsupervised, learning rate `5e-5`, 36 epochs, batch 10, accumulation 50, and 252 optimizer updates. Dataset identity is exact:

| Field | Treatment | Control |
|---|---|---|
| Dataset manifest SHA-256 | `da1eef468ee0bf940f4650bb79eaa5fab121664259767a7d8cae4657c19a8f70` | same |
| Train SHA-256 | `8eb65505b22f5c7f8e67f2d1877efad7503489dd8bdf2608cad08791f7d05a67` | same |
| Validation SHA-256 | `495cdcda9049b372159ef167f3da866e4cb82caf1977796efbb3baa9e07973e7` | same |
| Objective | `LM + 0.10 × relation-matched ranking`, 15 negatives | canonical answer-only LM (`lambda=0`) |
| Final validation loss | 0.0001843 | 0.0031131 |
| Aggregate Trainer train loss | 41.9302 | 0.7548 |

The losses are not comparable quality metrics: contrastive aggregate includes ranking/candidate scoring while control has only canonical LM. The roughly 8.1× runtime difference is expected because treatment scores 16 candidate sequences per example. This completed treatment started before separate factual-LM/ranking-loss aggregate logging was deployed, so it cannot alone support final causal attribution to the contrastive term.

## 4. Qwen seed-43 replication contract and observations

Qwen seed-43 reused the frozen 500-subject / 2,500-fact seed-42 population, 17,500 factual rows, 2,301 aligned replay-validation rows, local Qwen2.5-1.5B revision, answer-only loss, replay coefficient 0.5, 36 epochs, batch 50, accumulation 50, and 252 updates. Only run identity, model seed, and training-order seed changed to 43.

| Integrity item | Recorded value |
|---|---|
| Git commit | `6562b3a97423bd34b9f194368386d4d2c8fa9b9c` |
| Dataset manifest SHA-256 | `36a8e80b50750b643ae123e0b64ff668d2ba5f3d50cf23a9a64f806de5b7751c` |
| Train / validation rows | 17,500 / 2,301 |
| Train / validation SHA-256 | `7337450464ae47a40145c08086116e42098c3de10f3f78cb46024fce926e79d5` / `40a9218febe09a76269f9d21a7ab9cd8331f7fa558be6ae33a8f5c45ad2f1078` |
| Replay anchor rows | 17,500 / 2,301 |
| Mean factual / anchor loss | 0.398893 / 1.198113 |
| Final replay-validation loss | 2.945878 |

These are training-process observations only. Seed-43 must receive the same exact-prefix, A/B/C/D direct/QA, eight-cell intersection, binding, generic-integrity, and WikiText-2 PPL evaluation before it can confirm/refute seed-42 step-75.

## 5. Execution health and next gate

All manifests report one A100-80GB GPU, CUDA 12.8, BF16, local-files-only operation, and intended scratch output roots. Final stderr tails were normal validation progress bars; no traceback, OOM, NaN, or Inf was observed. The preflight recorded home at 8,299,516 KiB, `/vol/tmp2` with 114 TiB free and 3% inode use. A fresh post-run storage audit is still required before the broad evaluation wave.

Completed: all three trainings, their 11-checkpoint sets, and reproducibility manifests. Not complete: Qwen seed-43 gate evaluation/replication decision; SmolLM treatment/control factual, margin, robustness, and PPL comparison; selected artifact checksums; final M1/M2/M3 decision.

## 6. Required next sequence

1. Capture post-run storage audit.
2. Submit frozen Qwen seed-43 checkpoint evaluation.
3. Submit matched held-out evaluations for both SmolLM conditions.
4. Compare only after every metric is present; never select by aggregate training loss.

## 7. Qwen evaluation wave submitted — 28 July 2026

Commit `6e18560` freezes a seed-43 evaluation launcher that reuses the seed-42 four-form registry
and the exact/general evaluator contracts. The job family was submitted once as `437142`
(storage/path/checkpoint preflight), `437143` (frozen 11-checkpoint registry preparation), and
`437144_[0-10%3]` (three-at-a-time A100 checkpoint evaluations). The array is dependency-held
until preflight and preparation pass. Each array task produces the exact-prefix score, all
A/B/C/D direct/QA cells, eight-cell intersections, relation-binding outputs, generic integrity,
and WikiText-2 PPL for one seed-43 checkpoint. No seed-43 result is interpreted before the full
array completes and is summarized.

## 8. Parallel SmolLM held-out evaluations submitted — 28 July 2026

Commit `4373688` freezes the shared final-model evaluator for the two matched SmolLM conditions.
It runs the canonical exact-prefix evaluator, the A/B/C/D direct/QA frozen suite (which emits
per-fact candidate margins and relation-level forced-choice data), and generic WikiText-2 PPL /
integrity evaluation. Pre-submission preflights for both conditions passed: home was 8,299,668 KiB,
all output/cache paths resolved to scratch, `/vol/tmp2` had 114 TiB free and 3% inode use.

Two independent A100 jobs were submitted once: contrastive treatment **`437148`** and matched
`lambda=0` control **`437149`**. Both were pending normal scheduler priority at submission, with a
two-hour wall limit and expected runtime of approximately 60–90 minutes each. They are intentionally
parallel and write to separate scratch roots under `/vol/tmp2/yesildau/smollm_binding_evaluations_v1`.

## 9. SmolLM treatment/control held-out result — 28 July 2026

Jobs `437148` (contrastive treatment) and `437149` (`lambda=0` control) both completed their
frozen final-model evaluations. Both exact evaluators completed all 500 expected probes without
failure. The treatment improves every principal factual access comparison over the matched control,
but neither condition reaches the precommitted 70% eight-cell robust threshold; therefore SmolLM
does not open seed-43 or 2,500-fact scale-up.

| Metric | Contrastive treatment | `lambda=0` control | Difference |
|---|---:|---:|---:|
| Exact primary top-1 | 500/500 (100.0%) | 500/500 (100.0%) | 0.0 pp |
| Hard A/B/C/D direct+QA top-1 | 3,640/4,000 (91.0%) | 3,501/4,000 (87.5%) | +3.5 pp |
| Same-subject relation forced choice | 1,490/1,600 (93.1%) | 1,431/1,600 (89.4%) | +3.7 pp |
| Eight-cell robust intersection | 261/500 (52.2%) | 198/500 (39.6%) | +12.6 pp |
| Robust minimum relation | profession 34/100 (34.0%) | profession 21/100 (21.0%) | +13.0 pp |
| WikiText-2 PPL | 17.5234 | 17.1980 | treatment +0.3254 |
| Generic completion top-1 | 30/30 | 30/30 | equal |
| Lexical-empty / synthetic intrusion | 0 / 0 | 0 / 0 | equal |

The relation-level robust treatment counts are born-in 60, field-of-study 63, lives-in 53,
profession 34, and works-in-industry 51 (each /100). Control counts are respectively 46, 59, 39,
21, and 33. Treatment failure taxonomy is 249 prompt-form failures, 93 same-subject relation
swaps, and 18 early-EOS preferences; control has 342, 140, and 17. Thus contrastive candidate
ranking materially improves prompt-invariant access and relation binding, while the remaining
failure is still dominated by crossed prompt-form access, particularly profession.

This is a valid matched seed-42 comparison of endpoint quality, but not a complete mechanistic
training-dynamics analysis: the treatment started before separate LM/ranking-loss aggregates were
written. The robust gate failure blocks SmolLM seed-43 and scale-up under Document 125. No model
selection follows from this result alone.

## 10. Qwen evaluation progress at the same check

The first Qwen seed-43 array wave (checkpoints 25, 50, and 75) was still RUNNING after 57 minutes;
the remaining eight checkpoints were correctly throttle-held at three concurrent A100 tasks. Based
on this observed pace, the remaining Qwen wave was estimated at approximately 3–6 hours. Next
action: wait for all 11 frozen outputs, then summarize the seed-43 earliest-passing checkpoint and
compare it to seed-42 step 75 without changing any gate.

### Interim Qwen seed-43 hard-suite evidence — 28 July 2026

The first informative seed-43 checkpoint tasks completed their hard suites. This is not yet a full
replication decision because exact-prefix, generic-integrity, and PPL outputs must be verified from
the same frozen tasks, but the factual robust evidence is strong:

| Checkpoint | Hard top-1 | Eight-cell robust | Minimum robust relation | Relation forced choice |
|---|---:|---:|---:|---:|
| Step 50 | 19,845/20,000 (99.225%) | 2,405/2,500 (96.20%) | profession 451/500 (90.2%) | 7,965/8,000 (99.56%) |
| Step 75 | 19,872/20,000 (99.36%) | 2,407/2,500 (96.28%) | profession 433/500 (86.6%) | 7,976/8,000 (99.70%) |

Step-50 failure taxonomy has 125 prompt-form failures and 30 same-subject relation swaps; step-75
has 106 and 22. Both pass the frozen hard-suite global and relation robust thresholds. Under the
precommitted earliest-passing rule, step 50 would be preferred *only if* its pending exact, PPL,
and corrected-integrity metrics also pass. The remaining eight array checkpoints continue in
three-task waves; no early model-selection claim is made.

## 11. SmolLM exploratory lambda remediation submitted — 28 July 2026

The completed `lambda=0.10` treatment improves robust access over the matched control but fails
the 70% gate, with the sharpest remaining deficits in profession Form-C and
works-in-industry Form-D. A single-variable exploratory remediation is therefore frozen: keep the
same 100-subject/500-fact dataset, seed, 252 updates, answer-only LM term, 15 deterministic
relation-matched negatives, optimizer, and evaluator, while changing only the ranking coefficient
from `0.10` to **`0.25`**. This is labelled exploratory because the coefficient follows observed
seed-42 diagnosis; it cannot retrospectively validate the prior treatment.

Commit `9459e30` implements the condition with the now-available separate factual-LM/ranking-loss
logger. Its full preflight passed: home 8,299,704 KiB, scratch-only output/cache paths, 114 TiB
free on `/vol/tmp2`, and 3% inode use. One A100-80GB job, **`437152`**, was submitted to the distinct
`/vol/tmp2/yesildau/smollm_contrastive_lambda025_v1` root and was pending normal scheduler priority
at submission. Expected GPU runtime is 7–8 hours, followed by a 60–90 minute frozen evaluation.
