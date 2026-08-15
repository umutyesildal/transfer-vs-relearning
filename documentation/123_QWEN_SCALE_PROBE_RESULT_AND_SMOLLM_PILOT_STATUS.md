# 123 — Qwen 2,500-Fact Scale Probe Result and SmolLM Contrastive Pilot Status

**Date:** 26 July 2026  
**Status:** Qwen seed-42 exploratory scale probe complete; SmolLM seed-42 contrastive pilot remains in technical smoke recovery.  
**Authority:** Append-only result record for the exploratory plan frozen in Document 122. It does not supersede the M1 HOLD or authorize M2/M3.

## 1. Executive result

The Qwen2.5-1.5B clean-English-replay scale probe completed all 252 updates and all eleven frozen checkpoint evaluations at 500 subjects / 2,500 facts. It gives a clear checkpoint trade-off:

- Step 25 retains generic English but has not learned the factual population.
- Steps 50 and 75 have both high factual retrieval/binding and low generic-English drift.
- Step 75 is the best observed factual–PPL Pareto point: 99.29% hard-suite top-1, 99.96% primary exact-prefix top-1, 100% paired born-in/lives-in binding, and PPL 15.909 (1.082 times the frozen Qwen base reference of 14.699).
- From step 100 onward, factual metrics remain near-ceiling but generic English degrades rapidly; PPL reaches 411.501 at the final update. These later checkpoints cannot satisfy the frozen PPL-ratio gate.

This is strong positive scale evidence for Qwen at seed 42, but it is **not a stable final M1 claim**. A cell-level robust-intersection aggregation must still be produced from the completed per-probe files, and an independent seed-43 replication is required before any final selection.

The independent SmolLM2-1.7B contrastive-binding pilot has not produced scientific metrics yet. Its first real smoke correctly caught a Relation V2 profile-schema bug before training; that bug was corrected and re-preflighted. The current smoke retry is queued for an A100 allocation.

## 2. Frozen Qwen contract actually executed

| Item | Executed value |
|---|---|
| Model | Qwen2.5-1.5B local frozen manifest |
| Population | 500 subjects × 5 relations = 2,500 facts |
| Training data | 17,500 seven-row hybrid factual rows; 2,301 clean validation-aligned monitoring rows |
| Objective | Answer-only factual LM plus clean-English replay, coefficient 0.5 |
| Optimizer budget | 36 epochs, physical batch 50, accumulation 50, 252 updates |
| Seed | model/data seed 42/42 |
| Checkpoints | 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252 |
| Exact evaluator | 2,500 facts |
| Hard evaluator | 20,000 four-form probes (A/B/C/D × direct/QA) |
| Generic evaluator | Frozen WikiText-2 test protocol plus 30 generic completions |

The reduced 2,301 monitoring validation denominator is only the clean replay-alignment correction recorded in Document 122. It does not change the 2,500 exact or 20,000 hard evaluation denominators.

## 3. Execution history and infrastructure corrections

| Stage | Slurm job(s) | Outcome |
|---|---|---|
| V3 preflight and preparation | 418371, 418372 | PASS; scratch-only paths and clean aligned anchors verified |
| Qwen training | 418373 on `gruenau10` A100-80GB | PASS; 252 updates in 4h26m17s |
| Evaluation preparation | 418374 | PASS; 11-checkpoint registry created |
| Initial evaluation array | 418375 | All tasks stopped before model load because launcher registry arguments were empty |
| Corrected RTX evaluation array | 418386 | Steps 50/75 completed; remaining tasks OOMed on contaminated/shared 24GB RTX 3090 allocations |
| A100 retry array | 418397 | PASS for all previously missing Qwen checkpoints; final step 252 completed |

The two evaluation failures are infrastructure/launcher failures, not negative model evidence. No Qwen checkpoint was retrained or overwritten; the A100 retry evaluated the same frozen checkpoint paths.

## 4. Qwen checkpoint results

The base reference is Qwen PPL 14.699 under the matched frozen WikiText-2 protocol, as recorded in Document 106. `Hard top-1` is the global count over all 20,000 probes. `Exact primary` and `exact total-logprob sensitivity` are the two frozen scoring views from the 2,500-fact evaluator.

| Step | Hard top-1 | Relation forced-choice | Exact primary | Exact sensitivity | Pair binding | PPL | PPL/base |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 2,933 / 20,000 (14.67%) | 4,080 / 8,000 (51.00%) | 13.84% | 21.16% | 8.2% | 13.413 | 0.912 |
| 50 | 19,679 / 20,000 (98.40%) | 7,927 / 8,000 (99.09%) | 99.64% | 99.52% | 99.2% | 15.200 | 1.034 |
| 75 | 19,858 / 20,000 (99.29%) | 7,961 / 8,000 (99.51%) | 99.96% | 99.80% | 100.0% | 15.909 | 1.082 |
| 100 | 19,866 / 20,000 (99.33%) | 7,971 / 8,000 (99.64%) | 100.00% | 99.76% | 100.0% | 22.303 | 1.517 |
| 125 | 19,849 / 20,000 (99.25%) | 7,958 / 8,000 (99.48%) | 100.00% | 99.84% | 100.0% | 37.006 | 2.518 |
| 150 | 19,889 / 20,000 (99.45%) | 7,966 / 8,000 (99.58%) | 100.00% | 99.88% | 100.0% | 97.393 | 6.626 |
| 175 | 19,907 / 20,000 (99.54%) | 7,965 / 8,000 (99.56%) | 100.00% | 99.88% | 100.0% | 155.656 | 10.590 |
| 200 | 19,899 / 20,000 (99.50%) | 7,968 / 8,000 (99.60%) | 100.00% | 99.88% | 100.0% | 268.777 | 18.285 |
| 225 | 19,908 / 20,000 (99.54%) | 7,970 / 8,000 (99.63%) | 99.96% | 99.88% | 100.0% | 328.864 | 22.373 |
| 250 | 19,899 / 20,000 (99.50%) | 7,967 / 8,000 (99.59%) | 100.00% | 99.88% | 100.0% | 411.975 | 28.027 |
| 252 | 19,896 / 20,000 (99.48%) | 7,970 / 8,000 (99.63%) | 100.00% | 99.88% | 100.0% | 411.501 | 27.995 |

### 4.1 Failure pattern and integrity

At step 75 the hard-suite taxonomy contains 106 prompt-form failures and 36 same-subject relation swaps, with no early-EOS failure. At step 252 it contains 74 prompt-form failures and 30 same-subject relation swaps. Thus factual errors become rarer after step 75, but the marginal factual improvement is small compared with the PPL cost.

Every completed generic evaluation reports zero synthetic-subject intrusions. The 30 generic completion probes contain one or two empty-or-near-empty completions depending on checkpoint; this must be interpreted with the frozen generic-integrity criterion rather than silently ignored. Generic-completion top-1 is 29/30 through step 100 and 28/30 from step 125 onward.

### 4.2 Gate interpretation

| Frozen criterion | Step 75 evidence | Current interpretation |
|---|---|---|
| Exact-prefix ≥90% | 99.96% primary / 99.80% sensitivity | Pass |
| PPL ratio ≤1.25; preferred <1.10 | 1.082 | Pass, preferred band |
| Paired relation binding | 100.0%, 0 swapped-answer rate | Pass on this dedicated binding test |
| Four-form per-cell and eight-cell robust intersection | Global hard top-1 99.29% | **Not yet aggregated; do not substitute global top-1 for the cell/intersection gate** |
| Generic integrity | 0 synthetic-subject intrusions; 2/30 near-empty outputs | Requires frozen integrity-rule check in the follow-up summary |

The precommitted selection rule is the earliest checkpoint meeting all gates, not the checkpoint with the best global factual score. On available metrics, step 75 is the best **provisional** candidate: it dominates step 50 on factual metrics while staying under the PPL gate. Step 100 and later are disqualified by PPL regardless of their near-ceiling factual scores. Step 25 has lower PPL than base but is plainly pre-acquisition.

## 5. SmolLM contrastive-binding pilot status

| Event | Job(s) | Result |
|---|---|---|
| Initial preflight | 418405 | PASS |
| Initial A100 one-step smoke | 418406 | Stopped before optimizer update: trainer expected legacy `university_en` but Relation V2 profile has `field_of_study_en` / `works_in_industry_en` |
| Schema correction and local verification | commit `5c72ba7`; 43 selected tests passed | Inventory now includes only relation columns physically present in the frozen profile file |
| Corrected preflight | 418407 | PASS |
| First corrected smoke submission | 418448 | Safe stop before training: it waited beyond the old 30-minute preflight-age guard |
| Queue-age launcher correction | commit `3f06475` | Fresh preflight then smoke accept a 240-minute verified queue window |
| Current fresh preflight and smoke | 418449, 418450 | Preflight PASS; smoke queued for A100 resources at report time |

No SmolLM factual result, model checkpoint, or model-selection claim exists yet. Full seed-42 training remains conditional on a successful one-step two-loss smoke. The planned population remains 100 subjects / 500 facts; a 2,500-fact SmolLM scale-up is not authorized until the frozen pilot passes in both seeds.

## 6. Artifact locations and storage audit

| Item | Location / result |
|---|---|
| Qwen full tree | `/vol/tmp2/yesildau/qwen_scale_probe_v3` |
| Qwen scratch occupancy after evaluation | 99 GiB |
| SmolLM pilot tree | `/vol/tmp2/yesildau/smollm_contrastive_binding_v1` |
| Home project usage | 7.91 GiB during the coordinated preflight, below the 10 GiB project limit |
| `/vol/tmp2` capacity/inodes | 114 TiB available; 19% capacity and 3% inode use at audit |
| New large home experiment files | None found: the >500 MB home scan listed existing Conda shared-library files only, not Qwen/SmolLM experiment artifacts |

No cleanup is performed in this report. Selected/final weights, optimizer state, and checkpoints remain on scratch pending the cell-level summary, frozen selection decision, manifest/checksum generation, and explicit retention decision.

## 7. Next controlled actions

1. Wait for SmolLM smoke 418450. If it passes finite two-loss training, submit its seed-42 full training; if it fails, document the failure before changing any scientific setting.
2. Generate the Qwen cell-level robust-intersection and frozen integrity summary from the completed checkpoint outputs. Select no checkpoint before that summary.
3. If step 75 passes the remaining frozen gates, create a selected-artifact manifest and SHA-256, then open an independent seed-43 replication plan. This does not authorize M2/M3.
4. Run the coordinated post-family storage audit again after the active SmolLM pilot reaches a terminal state.

## 8. Status update — 27 July 2026, 07:32 CEST

No Qwen result changed after the completed final step-252 evaluation at 20:22 CEST on 26 July. All eleven hard, exact, and generic summary files remain present under the Qwen scratch tree.

SmolLM smoke retry `418450` remains `PENDING (Resources)`: it has not started and therefore has zero runtime, no new training manifest, and no scientific result. Slurm currently forecasts an A100-80GB allocation on `gruenau9` at **28 July 2026, 03:25 CEST** (end estimate 03:55 CEST). This is a scheduler resource wait, not a new trainer failure. The smoke continues to request a clean A100 because the earlier RTX evaluation allocation was memory-contaminated and because the frozen pilot requires an A100 two-loss smoke before full training.

At this check `/vol/tmp2` retained approximately 114 TiB free with 3% inode use; `/vol/tmp` had approximately 19 TiB free and `/vol/fob-vol6` showed 625 GiB free. No output was moved, deleted, or written to home by this status check.

## 9. AGENTS.md home-storage audit — 27 July 2026, 07:42 CEST

The AGENTS.md storage rule and HU launcher runbook were reread before this audit. The result is
unambiguous: the pending SmolLM smoke is **not** caused by project data, checkpoints, caches, or
model artifacts residing in HU home.

| Audit item | Observed result |
|---|---|
| Full home regular-file usage | 8,299,416 KiB (about 7.91 GiB), below the 10 GiB project safety limit |
| `transfer-vs-relearning` checkout usage | 17,016 KiB (about 16.6 MiB) |
| Project files larger than 50 MiB | None |
| Project `optimizer.pt`, scheduler/RNG/trainer state, or `model.safetensors` files | None |
| Resolved `runs` path | `/vol/tmp/yesildau/transfer-vs-relearning/runs` |
| Resolved `artifacts` path | `/vol/tmp/yesildau/transfer-vs-relearning/artifacts` |
| Home files larger than 500 MiB | Three pre-existing Conda runtime libraries (`libtorch_cuda.so`, `libcublasLt.so.12`, `libcudnn_engines_precompiled.so.9`); no experiment artifact |

The `418450` Slurm state remains `PENDING (Resources)`, with zero runtime and an A100-80GB
allocation forecast of 28 July 03:25 CEST. It is therefore a cluster scheduling constraint, not a
home-storage incident. No deletion is authorized or required.

## 10. SmolLM smoke execution and permanent queue-safe recovery — 27 July 2026, 16:35 CEST

Job `418450` eventually received a GPU allocation at 07:35 CEST. It then stopped before dataset
tokenization or an optimizer update because the preflight manifest had aged beyond the configured
240-minute guard while the job waited in the A100 queue. The smoke tree remained only 2.5 MiB and
no model/checkpoint was created. This was the third infrastructure guard outcome, not a scientific
result or a two-loss training failure.

The launcher was corrected in commit `5270ec0`. Instead of validating a manifest written before a
potentially long queue wait, the smoke and the later full-training launcher now run the mandatory
scratch/path/home/capacity preflight **after Slurm has allocated the GPU and immediately before
any dataset/model write**. This is stricter than widening an age threshold: the machine state used
for training is the state actually audited.

Shell syntax and 41 selected trainer/config tests passed before the commit was pushed and pulled on
HU. A fresh smoke retry, `426979`, was submitted at 16:35 CEST and is `PENDING (Priority)` at the
time of this update. It requests the same clean A100-80GB, has a 30-minute wall limit, and has no
dependency on an aging pre-submission manifest. Full seed-42 training remains unsubmitted until
this smoke completes successfully.

### Queue check — 27 July 2026, 19:06 CEST

Retry `426979` has not started: it is `PENDING (Resources)` with zero runtime, no smoke stdout or
stderr file yet, and no new smoke run directory. Slurm continues to forecast a clean A100-80GB on
`gruenau9` at 28 July 03:25 CEST. The queue state therefore has not introduced a new technical or
scientific result since the preceding update.

## 11. Successful two-loss smoke and full SmolLM seed-42 launch — 28 July 2026

The queue-safe smoke `426979` received an A100-80GB allocation and completed successfully at
03:35 CEST. Its in-job preflight passed with home usage 8,299,436 KiB, all high-volume paths on
scratch, and the full-training namespace absent. The one-step run used the frozen 3,500-row
training and 500-row validation dataset, answer-only LM loss, 15 relation-matched negatives, and
contrastive coefficient 0.10. The manifest records the expected SmolLM2-1.7B base revision and
commit `5270ec0`.

The smoke produced finite metrics (`train_loss` 388.218; `eval_loss` 7.026), a checkpoint, and a
final-model directory entirely under `/vol/tmp2/yesildau/smollm_contrastive_binding_v1/smoke`.
These values validate execution only; they are not factual-quality or model-selection metrics.

The one-update Trainer runtime was 182.99 seconds. At 252 frozen updates this implies an
approximately 12.8-hour raw upper estimate before checkpoint/evaluation overhead. The GPU
partition permits up to four days; consequently commit `607e37f` changes only the operational wall
limit from 3 to 16 hours. It changes no scientific hyperparameter, data row, loss coefficient,
negative sampling rule, seed, or gate.

Full seed-42 training was submitted as Slurm job `429991` with a 16-hour limit and is
`PENDING (Priority)` at submission. Its launcher performs a fresh storage/path preflight at actual
GPU allocation, writes checkpoints/caches/logs only to the SmolLM scratch root, and retains all
artifacts pending frozen checkpoint evaluation and selection. No SmolLM factual conclusion is
available until that training and its held-out evaluation complete.

## 12. Controlled follow-up opened — 28 July 2026

Document 125 now governs this workstream. Read-only inspection of the existing Qwen seed-42
step-75 all-cell output gives 2,402/2,500 (96.08%) eight-cell robust facts; the minimum relation
is `profession` at 441/500 (88.2%). The existing corrected primary integrity rule classifies the
two length-flagged outputs (`Navigation` and `Shade`, each plus EOS) as lexically non-empty; the
historical 2/30 length-only count remains a sensitivity. Step 50 is disqualified by its 78.6%
minimum relation-form cell, so step 75 is the precommitted earliest seed-42 all-gates candidate.

The contrastive treatment `429991` is RUNNING on A100-80GB. Commit `8cf92a9` adds a distinct,
otherwise matched `lambda=0` factual-LM control and separate aggregate factual-LM/ranking-loss
logging for future contrastive treatment runs. Its combined storage/path/inode preflight passed
with home 8,299,516 KiB and 114 TiB free on `/vol/tmp2`; exactly one control job `429992` was
submitted and entered RUNNING on A100-80GB. The current treatment predated separate-loss logging, so
it cannot alone support the final causal attribution to the contrastive term.

Qwen scale seed-43 is now frozen in commit `6562b3a`. Preflight `429993` and its dependent A100
training `429994` were submitted once to the distinct `/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1`
root. They reuse the immutable seed-42 population/dataset/anchors and change only run identity,
model seed, and training-order seed to 43.
