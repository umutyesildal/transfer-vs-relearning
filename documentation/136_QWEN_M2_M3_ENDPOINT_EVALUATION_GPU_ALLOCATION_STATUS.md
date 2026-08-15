# 136 - Qwen M2/M3 Endpoint Evaluation GPU Allocation Status

**Date:** 2026-08-01  
**Status:** Endpoint evaluation partially complete; controlled RTX6000 tasks are running

## 1. Scope

The four principal Qwen M2/M3 training runs are complete. This report records the first endpoint
evaluation wave, the contaminated-device failures, the controlled clean-device checks, and the
current evaluation count. It does not report a causal M2/M3 result; the required four-state
evaluation package is not complete.

## 2. Frozen evaluation contract

The evaluation uses commit `348d5cd093ecfc7120806170dcfbfb63d52744fd`, the frozen endpoint
`checkpoint-128`, four states, 24 slices per state, and 2,500 probes per slice. The required
evaluation family therefore contains 96 slices / 240,000 endpoint probes. No new checkpoints are
created. The existing preflight manifest is:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/evaluation_v1/preflight/manifest.json
```

The family preflight `440000` passed with four states, 96 expected jobs, zero new checkpoints,
and scratch-only output placement.

## 3. Initial evaluation attempts

The first serialized array `440001_[0-95%1]` was started on the RTX 3090 path. Its task 0 produced
the first valid slice. The pending remainder was stopped after the slow throughput became clear.

Retry array `440006_[1-95%6]` used `guppi8,viscom-gpu` and excluded the historically contaminated
guppi5--7 nodes. Tasks 1 and 3 ran successfully. Many other tasks stopped before model loading
because the allocated device reported an unrelated compute process. The guard correctly exited
with the intentional failure; these attempts produced no scientific result.

The follow-up retry `440095_[2-62,64-95%4]` was restricted to `viscom-gpu`. It reproduced the same
dirty-device condition and was canceled. It was an operational retry failure, not an evaluation
observation.

## 4. Controlled clean-device results

After the retry loop was stopped, three single-slice jobs were run under explicit node/GPU
selection:

| Job | Node / device | State | Slice | Result |
|---|---|---|---|---|
| `440188_4` | `gruenau10` / A100 80GB, 18 MiB | `m2_clean_seed42` | `en_to_en_form_c_direct` | 2,500/2,500, complete |
| `440190_6` | `gruenau10` / A100 80GB, 17 MiB | `m2_clean_seed42` | `en_to_en_form_d_direct` | 2,500/2,500, complete |
| `440277_7` | `guppi8` / RTX 3090, 15 MiB | `m2_clean_seed42` | `en_to_en_form_d_qa` | 2,500/2,500, complete |

Together with the three earlier valid slices, the current valid endpoint package contains **6/96
slices**. All six are from `m2_clean_seed42`; no M3-fact or seed-43 endpoint result has been
interpreted yet. The queue is empty after these controlled jobs completed.

## 5. Root cause and operational interpretation

Slurm reported `gruenau10` as idle, but one physical A100 was still occupied by PID `22926`
(`python`) with approximately 8,708 MiB on UUID
`GPU-5d089b0f-2824-0adc-2d93-1be85aa4ad86`. The same type of mismatch occurred on RTX 3090
allocations. The launcher’s allocated-device guard is therefore necessary and must not be
disabled. An idle node state is not sufficient evidence that the selected physical GPU is clean.

The failed array tasks are retained as infrastructure evidence and are not counted as missing
scientific observations that can be silently relabeled as results. The remaining 90 slices must be
submitted only after a controlled allocation strategy is selected and its first tasks pass the
guard.

## 6. Storage and reproducibility audit

The submission-time audit recorded:

- HU home: approximately 14 GiB, below the 30 GiB stop threshold;
- `/vol/tmp2`: approximately 113 TiB available;
- `/vol/tmp2` inode use: 3%;
- repository `runs`: `/vol/tmp/yesildau/transfer-vs-relearning/runs`;
- repository `artifacts`: `/vol/tmp/yesildau/transfer-vs-relearning/artifacts`;
- no new unexplained large home file; only the authorized frozen Qwen copies and environment
  libraries were listed.

No evaluation summary or causal analysis has been generated yet. The six per-slice results remain
on scratch until the complete four-state package is verified.

## 7. Next action

The next action is a fresh controlled GPU allocation check, followed by a bounded evaluation wave
that is stopped immediately if the same physical-device contamination recurs. The expected time
for the remaining 90 slices is approximately 6--15 hours **after the wave is actually submitted**.
Once all 96 slices pass, state summaries, 2,000-bootstrap contrasts, the M1-to-arm comparisons,
the storage audit, and the final causal interpretation will be produced and documented.

## 8. Weekend A6000 allocation wave

To use idle server capacity without taking other users' jobs or using `--exclusive`, an additional
wave was submitted to `gruenau7` and `gruenau8` with one RTX A6000 per task:

```text
440284_[2,5,8-95%8]
```

The node state reported both nodes as idle and the storage recheck passed with home at 14 GiB,
`/vol/tmp2` at 113 TiB available, and 3% inode use. The first clean tasks were:

- `440284_5`: `gruenau7`, RTX A6000 UUID `GPU-c640c8bd-5222-91c1-6d72-b989d55ed437`, 15 MiB;
- `440284_9`: `gruenau7`, RTX A6000 UUID `GPU-975709cc-4783-3313-bbe6-0da95a46ecd2`, 15 MiB.

Several other tasks were assigned to a contaminated physical device on `gruenau7` and exited
through the intentional guard before model loading. The broad array was canceled after the guard
failures began repeating; 48 non-scientific guard-failure logs were present at the audit. The
clean tasks were preserved.

A separate test `440336_10` on idle `gruenau8` confirmed that this node also has an externally used
device: PID `19948` (`VLLM::Worker_TP0`) was using approximately 45,548 MiB on the allocated RTX
A6000. The task stopped before evaluation and produced no scientific result. No unrelated process
was killed or modified.

The current operational conclusion is that the cluster has usable GPUs, but node-level `idle`
state cannot identify a clean physical device. The next launcher wave must bind to verified clean
GPU UUID/index assignments or use a bounded allocation strategy that stops on the first repeated
contamination. The guard must remain enabled.

## 9. Cross-node pilot and working RTX6000 lane

Because the cluster exposed several idle GPU types, one slice was tested on each of three
additional nodes without canceling or modifying another user's job:

- `440337_2` on `gruenau9` A100: no scientific output or non-empty launch log was produced; it is
  not counted and was not retried blindly.
- `440338_8` on `gruenau2` RTX6000: clean guard, 5 MiB initial use, evaluation running.
- `440339_11` on `gruenau1` V100: clean guard, but the installed PyTorch CUDA build failed with
  `CUDA error: no kernel image is available for execution on the device`.

Two further RTX6000 tasks on `gruenau2` also passed the clean guard:

- `440340_12`, allocated UUID `GPU-31e29be8-c653-eba9-6d77-e9fd72722d64`;
- `440340_13`, allocated UUID `GPU-bc81a377-17a6-5f8e-bcfc-d72988220d10`.

The V100 tasks `440341_14` and `440341_15` reproduced the kernel-compatibility failure and are not
scientific results. The working continuation wave is:

```text
440344_[2,10-11,14-95%3]  -> gruenau2, one RTX6000 per task
```

It excludes the currently running valid tasks and uses at most the three RTX6000 devices on the
idle node. The two clean A6000 tasks from `440284_5` and `440284_9` remain active in parallel.
No `--exclusive` allocation, unrelated-job cancellation, or external-process termination was
used.

## 10. RTX6000 continuation progress

The first working RTX6000 task completed cleanly:

- `440338_8` on `gruenau2`, `tr_to_en_form_a_direct`, 2,500/2,500, terminal marker present;
- `440340_12` remains active at 2,250/2,500;
- `440340_13` remains active at 1,825/2,500;
- after `440338_8` released its device, `440344_10` started automatically on `gruenau2`.

At this checkpoint the progress manifests report **9 completed slices and 3 running slices** out
of 96, with no guard, CUDA, OOM, traceback, or segmentation errors in the working RTX6000 lane.
The earlier rough count of 11 was corrected using the per-slice `progress.json` status fields.

## 11. RTX6000 lane follow-up

At the next scheduled check, the continuation lane remained healthy:

- `440344_10`: `tr_to_en_form_b_direct`, 1,250/2,500;
- `440344_16`: `tr_to_tr_form_a_direct`, 1,125/2,500;
- `440344_17`: `tr_to_tr_form_a_qa`, 425/2,500.

The progress package reported **14 completed slices and 3 running slices**. The remaining
`440344` tasks were pending only because the intentional array throttle of three occupied all
three clean RTX6000 cards on `gruenau2`. No guard, CUDA, OOM, traceback, or segmentation error was
observed in this lane.

## 12. RTX6000 wave continuation on 2026-08-02

The long-running RTX6000 continuation remained healthy at the next result check:

- `440344_43`: `m3_fact_seed42`, `tr_to_tr_form_c_direct`, 1,200/2,500;
- `440344_44`: `m3_fact_seed42`, `tr_to_tr_form_b_qa`, 1,550/2,500;
- `440344_45`: `m3_fact_seed42`, `tr_to_tr_form_c_qa`, 200/2,500.

The scratch evaluation package reported **39 completed summaries and 3 running slices** out of
96. The remaining tasks were pending behind the intentional throttle of three RTX6000 devices on
`gruenau2`. No `unexpected_gpu`, CUDA, OOM, traceback, or segmentation signatures were found in
the `440344` logs. This is execution evidence only; no M2/M3 metric or causal conclusion has been
interpreted yet.

## 13. RTX6000 wave progress at 65/96

The continuation wave remained error-free at the following check on 2026-08-02:

- `440344_69`: `m2_clean_seed43`, `tr_to_tr_form_c_qa`, 1,725/2,500;
- `440344_70`: `m2_clean_seed43`, `tr_to_tr_form_d_direct`, 450/2,500;
- `440344_71`: `m2_clean_seed43`, `tr_to_tr_form_d_qa`, 225/2,500.

The evaluation root contained **65 completed summaries and 3 running slices** out of 96; the
remaining 28 tasks were pending behind the three-card RTX6000 throttle. No guard, CUDA, OOM,
traceback, segmentation, or failed-task signature was found in the active `440344` lane. Metrics
remain intentionally unaggregated until all four states and all 96 slices are complete.

## 14. RTX6000 wave progress at 75/96

At the next status check on 2026-08-02, the controlled continuation was still healthy:

- `440344_79`: `m3_fact_seed43`, `en_to_en_form_d_qa`, running on `gruenau2` RTX6000;
- `440344_80`: `m3_fact_seed43`, `tr_to_en_form_a_direct`, running on `gruenau2` RTX6000;
- `440344_81`: `m3_fact_seed43`, `tr_to_en_form_a_qa`, running on `gruenau2` RTX6000.

The results tree contained **75 completed summaries and 3 running slices**. By state, completed
summaries were `m2_clean_seed42=20`, `m2_clean_seed43=24`, `m3_fact_seed42=24`, and
`m3_fact_seed43=7`. The next 14 array tasks (`440344_[82-95%3]`) were pending behind the
three-card RTX6000 throttle.

Four earlier `m2_clean_seed42` result directories remained without a terminal summary and had
zero-byte stdout/stderr logs: `en_to_en_form_b_direct`, `tr_to_en_form_b_qa`,
`tr_to_en_form_d_direct`, and `tr_to_en_form_d_qa`. They are not counted as scientific results and
must be explicitly resubmitted or otherwise reconciled after the current wave; no duplicate
submission was made during this check. `sacct` was temporarily unavailable because the Slurm
accounting connection returned a Munge/protocol-authentication error, so these empty task records
were not assigned a terminal code from accounting output.

No `unexpected_gpu`, CUDA, OOM, traceback, segmentation, or other error signature was found in
the `440344` logs. The complete four-state package is therefore **75/96 terminal, 3 running,
14 queued, and 4 unresolved empty earlier entries**; endpoint metrics and causal analysis remain
frozen until every required slice has a valid terminal summary.

## 15. Offline aggregation, gate tooling, and empty-slice retry

While the RTX6000 lane continued, the post-evaluation CPU path was prepared and tested in the
local `corpus-update` repository. Commit `59c60f29648392c275d24a74308a44c8ab1525c7` adds:

- `scripts/assemble_qwen_m2_m3_results.py`, which validates all frozen slice hashes, completion
  markers, 2,500-row counts, required metadata, unique probe IDs, and exact registry membership
  before creating state-level CSVs;
- `scripts/finalize_qwen_m2_m3_gate_report.py`, which applies the frozen primary interaction and
  EN→EN retention rules without post-hoc checkpoint, threshold, or seed selection;
- `scripts/prepare_qwen_m2_m3_empty_retry.py` and the dedicated retry launcher/preflight;
- eight passing targeted tests covering aggregation, incomplete-slice refusal, retry mapping, and
  the existing M2/M3 metric package.

The four empty `m2_clean_seed42` entries were mapped to task IDs `2, 11, 14, 15`. The HU checkout
was fast-forwarded to the commit above. Retry preflight `440583` passed with home at 14 GiB,
`/vol/tmp2` at 113 TiB available, `/vol/tmp2` inode use at 3%, and no new checkpoints. The retry
array `440584_[2,11,14-15%3]` was submitted to `gruenau2` with one RTX6000 per task and is
currently pending only for resources behind the active three-card `440344` lane. No existing
result directory was overwritten; the retry launcher fails closed if any target contains a file.

## 16. 440344 pending-task commit-guard failure

At the next check on 2026-08-02, the valid package had **77 completed summaries and 3 running
slices**:

- `m2_clean_seed42`: 20 complete, `en_to_en_form_b_direct` running as retry `440584_2`;
- `m2_clean_seed43`: 24 complete;
- `m3_fact_seed42`: 24 complete;
- `m3_fact_seed43`: 9 complete, with `tr_to_en_form_a_qa` and `tr_to_en_form_b_direct` still
  running in `440344_81` and `440344_82`.

The remaining `440344` tasks `83--95` did not run the evaluator. `scontrol` reports immediate
`FAILED / ExitCode=1:0` at `2026-08-02T14:20:24` on `gruenau2`, and every corresponding stdout and
stderr file is zero bytes. The cause is now identified: the original array was submitted against
commit `348d5cd093ecfc7120806170dcfbfb63d52744fd`, while the HU checkout was fast-forwarded to
`59c60f29648392c275d24a74308a44c8ab1525c7` for the retry tooling at 14:01. The pending tasks
started after that checkout change and failed the launcher's `EXPECTED_COMMIT` guard before any
scientific code or GPU guard ran. The already-running tasks had started before synchronization and
were unaffected.

These 13 task failures are infrastructure evidence, not scientific observations. Together with
the three remaining empty `m2_clean_seed42` entries, they leave **77 terminal summaries, 3 valid
running slices, and 16 slices requiring controlled retry/reconciliation**. Retry `440584_2` passed
the allocated-device guard on `gruenau2`; `440584_[11,14-15%3]` remains resource-pending. No
`unexpected_gpu`, CUDA, OOM, traceback, or segmentation signature was found in the actual
evaluator logs.

## 17. Current terminal package at 83/96

The following full-family check found no Qwen M2/M3 jobs remaining in the queue. The valid scratch
package contains **83/96 completed summaries**:

| State | Completed |
|---|---:|
| `m2_clean_seed42` | 24/24 |
| `m2_clean_seed43` | 24/24 |
| `m3_fact_seed42` | 24/24 |
| `m3_fact_seed43` | 11/24 |

All four empty `m2_clean_seed42` retry tasks completed successfully in `440584_[2,11,14-15%3]`:
each produced 2,500/2,500 probes, passed the RTX6000 allocated-device guard on `gruenau2`, and
ended with the expected `m2_m3_eval_slice_complete` marker. Main tasks `440344_81` and `440344_82`
also completed the two M3 seed-43 slices that had already started before the HU checkout update.

The remaining 13 M3 seed-43 slices are exactly the registry entries mapped to failed tasks
`440344_83--95`: `tr_to_en_form_b_qa`, `tr_to_en_form_c_direct`, `tr_to_en_form_c_qa`,
`tr_to_en_form_d_direct`, `tr_to_en_form_d_qa`, `tr_to_tr_form_a_direct`, `tr_to_tr_form_a_qa`,
`tr_to_tr_form_b_direct`, `tr_to_tr_form_b_qa`, `tr_to_tr_form_c_direct`, `tr_to_tr_form_c_qa`,
`tr_to_tr_form_d_direct`, and `tr_to_tr_form_d_qa`. Their result directories do not exist, and
their original stdout/stderr files are zero bytes. They are not scientific results and require a
new retry wave under the current synchronized commit.

The four completed retry logs and the two completed main logs contain no current-wave guard, CUDA,
OOM, traceback, segmentation, or evaluator error signature. The strict aggregation and gate tools
therefore remain intentionally unrun: producing a causal M2/M3 summary from 83/96 slices would
violate the frozen matched-family requirement.

## 18. Controlled retry of the 13 M3 seed-43 slices

On 2026-08-02, only the 13 missing `m3_fact_seed43` slices were resubmitted; the 83 valid
summaries were retained and were not recomputed. The retry tooling was generalized in commit
`9b3a3ded1be2933285e5a2ebac3e293105eeb37f`, pushed on `corpus-update`, and the HU checkout was
synchronized to that commit before submission.

Retry preflight `440633` passed with the following bounded family:

- required state: `m3_fact_seed43`;
- task IDs: `83--95` only;
- expected tasks: 13;
- expected checkpoints: 0;
- run name: `retry_m3_seed43_v1`;
- output root: `/vol/tmp2/yesildau/qwen_m2_m3_v1/evaluation_v1/results/m3_fact_seed43/`;
- retry metadata: `/vol/tmp2/yesildau/qwen_m2_m3_v1/retry_m3_seed43_v1/`;
- home usage: 14 GiB; `/vol/tmp2` available: 113 TiB; `/vol/tmp2` inode use: 3%;
- retention policy: no evaluation checkpoints.

Retry array `440634_[83-95%3]` was submitted to `gruenau2` with one RTX6000 per task and a
three-task throttle. At the first live check, tasks `440634_83`, `_84`, and `_85` were running;
the remaining ten were correctly pending behind the array throttle. Their launch logs identified
the expected state and slices, reported 2,500 probes each, and passed `gpu_preflight=clean` on
three distinct Quadro RTX 6000 GPU UUIDs. Their stderr files were empty at that check. The retry
array remains incomplete, so strict assembly, metric analysis, gate evaluation, and the final
post-run storage audit are intentionally deferred until all 13 tasks have valid terminal outputs.

## 19. Retry progress check: 89/96 valid slices

At the next check on 2026-08-02, retry array `440634` had produced six additional valid
`m3_fact_seed43` slices: task IDs `83--88`. Each completed with 2,500/2,500 probes and the
expected `m2_m3_eval_slice_complete` marker. Tasks `89--91` were running on `gruenau2`, while
`92--95` were pending behind the three-task array throttle. The aggregate valid package had
therefore reached **89/96 slices** (the previous 83 plus six new slices). No current-wave GPU,
CUDA, OOM, traceback, segmentation, evaluator, or contaminated-device error signature was found.
Strict assembly and gate analysis remain deferred until tasks `89--95` also complete and the
post-run storage audit passes.

## 20. Final retry slice in progress: 12/13 complete

At the following check on 2026-08-02, retry `440634` had completed **12/13** controlled retry
slices. The only remaining task was `440634_95`, corresponding to
`m3_fact_seed43 / tr_to_tr_form_d_qa`. Its launch log showed the expected model/state metadata,
2,500-probe target, and `gpu_preflight=clean` on `gruenau2`; stderr was empty. Its progress file
reported `1,600/2,500` probes with status `running`. No current-wave error signature was found.
The full 96-slice assembly and post-run storage audit remain blocked only on this final task.

## 21. 96/96 completion and strict assembly

The final retry check on 2026-08-02 confirmed that task `440634_95` completed the remaining
`tr_to_tr_form_d_qa` slice with 2,500/2,500 probes and the expected completion marker. The retry
array is terminal, all 13 retry task logs contain completion markers, and the complete family now
contains **96/96 `summary.json` files**. No current-wave GPU, CUDA, OOM, traceback, segmentation,
evaluator, or contaminated-device error signature was found. The only stderr text in the final
task was the non-fatal Transformers `torch_dtype` deprecation warning.

The mandatory post-run capacity check recorded `/vol/tmp2` with 113 TiB available and 3% inode
use, and `/vol/tmp` with 19 TiB available and 3% inode use. The home `du -xsh` scan was slow on
the NFS service and exceeded the bounded audit timeout; no project output was written to home, and
the home large-file scan produced no new project-run artifact. This filesystem-scan limitation is
retained as an operational note rather than treated as a scientific failure.

Strict CPU assembly passed for all four states and wrote:

`/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/assembled_20260802T2315Z/results_manifest.json`

The frozen 2,000-bootstrap analysis was then started in the `xfer-relearn` Python 3.11
environment under output directory
`/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/metrics_20260802T2315Z`. The analysis completed with
`status=completed` and integrity `passed`, producing the state, paired-contrast, interaction,
robustness, and manifest outputs.

## 22. Final frozen M2/M3 gate result

The frozen gate was applied from the repository contract without checkpoint, threshold, or seed
selection after inspecting the results. The final report is:

`/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/gate_20260802T2325Z/final_gate_report.json`

The operational validity gate passed: all six required states were present, each had 60,000
probes, and the assembled/analysis manifests were complete. The EN-to-EN retention guardrail also
passed; the worst observed seed/arm difference was seed 43 M2-clean versus M1 at `-0.0300`, above
the frozen `-0.05` limit.

The primary causal interaction gate failed under its precommitted criterion
`observed > 0` and 95% bootstrap CI lower bound `> 0` for both seeds. The frozen TR-to-EN
interaction results were:

| Seed | Observed interaction | 95% bootstrap CI | Status |
|---|---:|---:|---|
| 42 | `0.0025` | `[-0.0051, 0.0101]` | fail: CI crosses zero |
| 43 | `0.0135` | `[0.0051, 0.0218]` | pass |

Thus the overall decision is **`primary_success_criterion_not_met`**. This is a valid negative
or inconclusive scientific outcome, not an infrastructure failure: the full family is
operationally valid, retention is within guardrail, but the Branch-B factual interaction is not
replicated with the required two-seed confidence. No automatic new training, third seed, dose
change, checkpoint change, or post-hoc gate relaxation is authorized by this result; the next
action requires an explicit scientific decision.

## 23. Complete aggregate result package

The final result package is complete and remains on HU scratch under:

`/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/`

The strict assembled package is
`assembled_20260802T2315Z/`; the 2,000-subject-bootstrap package is
`metrics_20260802T2315Z/`; and the frozen gate package is
`gate_20260802T2325Z/`. The complete aggregate outputs contain 1,258 data rows across the five
metric CSVs. The row-level relation, form, scaffold, Branch A/B, frequency, name, rarity,
popularity, robust-intersection, and paired-contrast results are all retained in these files; the
tables below give the complete global/direction headline extract without replacing the full files.

| Aggregate output | Data rows | SHA-256 |
|---|---:|---|
| `state_accuracy.csv` | 462 | `5394dd8b12f176a672c3008e7aa1f55d4851dbde92d7b06f348c77eca50e4431` |
| `paired_state_contrasts.csv` | 462 | `1ec55af44904cbeef9c2c9f888c52778590288ffb3bd3e5a663d42dc829ad8d4` |
| `branch_interactions.csv` | 118 | `61680518448161d94d1b0180a036a14d89d4107f1dad49b4839b8c40375a9c59` |
| `robust_state_accuracy.csv` | 108 | `d3f701de7d63a232b4ab7b42e6580b6d3523796cd2707ae7ab6b027a9efd1c86` |
| `robust_paired_contrasts.csv` | 108 | `48217e44ae6cf5247e3d399d3af77495f19e106afa194b8b9efb15e2f83a66ba` |
| `analysis_manifest.json` | 6 states / completed | `d8122d948360201ff17f434fdf220b15216a849fe14de0e8c5171342cc9b1419` |
| `integrity_summary.json` | passed | `5d46c4d8ce94dc293e58e26469d3fdc451c703cdaa59c060c35fa1511812b882` |

### 23.1 State accuracy: global and direction headline results

Values are top-1 accuracy with 95% subject-bootstrap confidence intervals; all rows use 2,000
bootstrap samples and 500 subjects.

| State | Global | EN→EN | TR→EN | TR→TR |
|---|---:|---:|---:|---:|
| M1 seed 42 | 60.12% [59.52, 60.75] | 99.29% [99.14, 99.43] | 52.03% [50.89, 53.19] | 29.05% [27.90, 30.20] |
| M1 seed 43 | 60.63% [59.99, 61.26] | 99.24% [99.04, 99.42] | 52.52% [51.18, 53.82] | 30.12% [28.97, 31.21] |
| M2-clean seed 42 | 51.27% [50.65, 51.89] | 98.05% [97.72, 98.36] | 33.29% [32.07, 34.48] | 22.46% [21.36, 23.50] |
| M2-clean seed 43 | 51.06% [50.33, 51.78] | 96.24% [95.54, 96.87] | 33.70% [32.43, 34.90] | 23.25% [22.18, 24.30] |
| M3-fact seed 42 | 52.47% [51.82, 53.12] | 98.22% [97.94, 98.48] | 35.14% [33.96, 36.33] | 24.04% [22.94, 25.08] |
| M3-fact seed 43 | 52.50% [51.76, 53.21] | 96.95% [96.37, 97.45] | 35.59% [34.33, 36.81] | 24.97% [23.87, 26.10] |

### 23.2 Paired changes across all global/direction headline cells

All values are percentage-point changes with 95% subject-bootstrap confidence intervals.

| Seed | Direction | M2-clean − M1 | M3-fact − M1 | M3-fact − M2-clean |
|---|---|---:|---:|---:|
| 42 | Global | −8.86 [−9.43, −8.29] | −7.66 [−8.23, −7.15] | +1.20 [+0.98, +1.42] |
| 42 | EN→EN | −1.24 [−1.55, −0.97] | −1.07 [−1.33, −0.81] | +0.17 [+0.04, +0.32] |
| 42 | TR→EN | −18.75 [−19.94, −17.56] | −16.89 [−18.06, −15.77] | +1.86 [+1.48, +2.22] |
| 42 | TR→TR | −6.59 [−7.40, −5.81] | −5.01 [−5.79, −4.27] | +1.58 [+1.23, +1.91] |
| 43 | Global | −9.57 [−10.23, −8.92] | −8.13 [−8.74, −7.52] | +1.44 [+1.20, +1.70] |
| 43 | EN→EN | −3.00 [−3.66, −2.43] | −2.30 [−2.82, −1.85] | +0.70 [+0.46, +0.96] |
| 43 | TR→EN | −18.83 [−20.03, −17.66] | −16.93 [−18.10, −15.80] | +1.89 [+1.48, +2.33] |
| 43 | TR→TR | −6.87 [−7.72, −6.05] | −5.15 [−5.95, −4.33] | +1.72 [+1.36, +2.07] |

### 23.3 Robust direction-global results

These are the all-cell robust intersections across the frozen relation/form/scaffold surface.

| State | EN→EN robust | TR→EN robust | TR→TR robust |
|---|---:|---:|---:|
| M1 seed 42 | 96.08% [95.28, 96.84] | 22.52% [21.28, 23.76] | 14.96% [14.00, 15.96] |
| M1 seed 43 | 96.28% [95.52, 97.00] | 23.44% [22.04, 24.84] | 16.80% [15.84, 17.76] |
| M2-clean seed 42 | 91.96% [90.84, 92.96] | 16.72% [15.56, 17.92] | 12.52% [11.48, 13.52] |
| M2-clean seed 43 | 88.48% [86.96, 89.80] | 15.28% [14.08, 16.56] | 11.96% [10.96, 12.92] |
| M3-fact seed 42 | 92.20% [91.04, 93.16] | 18.20% [17.00, 19.40] | 13.68% [12.68, 14.68] |
| M3-fact seed 43 | 89.64% [88.28, 90.92] | 16.72% [15.56, 18.00] | 13.32% [12.28, 14.32] |

### 23.4 Branch interaction across all global/direction headline cells

The interaction is `(M3-fact − M2-clean)_B − (M3-fact − M2-clean)_A`; branch changes and
interactions are percentage points.

| Seed | Cell | Branch A change | Branch B change | Interaction [95% CI] |
|---|---|---:|---:|---:|
| 42 | Global | +1.09 | +1.31 | +0.21 [−0.22, +0.66] |
| 42 | EN→EN | +0.10 | +0.24 | +0.14 [−0.13, +0.42] |
| 42 | TR→EN | +1.73 | +1.98 | +0.25 [−0.51, +1.01] |
| 42 | TR→TR | +1.45 | +1.70 | +0.25 [−0.44, +0.93] |
| 43 | Global | +1.09 | +1.79 | +0.69 [+0.18, +1.21] |
| 43 | EN→EN | +0.82 | +0.59 | −0.23 [−0.75, +0.27] |
| 43 | TR→EN | +1.22 | +2.57 | +1.35 [+0.51, +2.18] |
| 43 | TR→TR | +1.24 | +2.20 | +0.96 [+0.27, +1.66] |

The complete assembly and gate manifests are also hash-frozen:

- `assembled_20260802T2315Z/results_manifest.json` — `dfccc1b5f37a72fed687323258f871dbc4188304bd4c087f0a93a8ee1239708a`;
- `assembled_20260802T2315Z/assembly_manifest.json` — `60bdb420406fb774aaa191304dddedadfb382cf7273d3986a2b5d7acd4167684`;
- `gate_20260802T2325Z/final_gate_report.json` — `e5dbe0c7631a2590c5087946635f1f18ccdd39abbb136e54ec621d7efe8419a5`;
- `gate_20260802T2325Z/final_gate_report.md` — `b812a8b1bad9269a0db2daeccfd607b98283b719a3ed5b16de5cffb5cf40a646`.

### 23.5 M1 baseline anchor and generic-PPL results

The two frozen M1 anchors used by every paired contrast were also reloaded and evaluated before
M2/M3. Their final generic-PPL package was retained under
`/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/`.

| Baseline metric | M1 seed 42 / step 75 | M1 seed 43 / step 50 |
|---|---:|---:|
| English PPL | 15.909 [15.437, 16.387] | 15.170 [14.734, 15.626] |
| Turkish PPL | 17.349 [17.212, 17.499] | 15.741 [15.619, 15.875] |
| EN→EN top-1 | 99.29% [99.14, 99.43] | 99.24% [99.04, 99.42] |
| TR→EN top-1 | 52.03% [50.89, 53.19] | 52.52% [51.18, 53.82] |
| TR→TR top-1 | 29.05% [27.90, 30.20] | 30.12% [28.97, 31.21] |

Both baseline packages passed the frozen reload/integrity checks: 60,000 unique probes per seed,
all three directions, all four forms, both scaffolds, no empty expected answers, no empty predicted
surfaces, and candidate-ranking rather than answer-cue scoring. These baseline values are the M1
reference for every M2-clean/M3-fact delta in Sections 23.1--23.4.

## 24. Pre-M2/M3 task closure audit

Document 133's ordered pre-M2/M3 requirements were checked against Documents 134--136 and the
scratch manifests. There is no remaining pre-M2/M3 task:

| Document 133 requirement | Status | Evidence |
|---|---|---|
| Turkish templates reviewed and ambiguity corrected | complete | Document 134 §3; correction before materialization |
| HU sync, tests, and exact-commit validation | complete | Documents 134--135; authoritative smoke/preflight records |
| 2,500-fact bilingual registry and 60,000-probe contract | complete | Documents 134 §15/§22; frozen evaluation manifest |
| Both selected M1 bilingual baselines and EN/TR PPL | complete | Document 134 §22; 48 baseline slices plus final CI/PPL package |
| Fact dose, endpoint, estimand, and gates frozen | complete | Document 135 §§1--3; `fact_cycles=4`, checkpoint-128 |
| Matched M2-clean/M3-fact blocks and contamination audit | complete | Document 135 §6; equal 1,048,576-token budgets, 5,000 Branch-B exposures, zero Branch-A exposure |
| Smoke, finite-loss check, resume rehearsal, English retention check | complete | Document 135 §10; both technical smoke reports passed |
| Storage/path/cache/device preflight | complete with audit note | Documents 134--136; scratch-only outputs, home below stop threshold, NFS `du` timeout recorded in §21 |
| Four principal M2/M3 training runs | complete | Document 135 §11; all four manifests `status=complete`, endpoint checkpoint-128 |
| Full endpoint evaluation and causal analysis | complete | Sections 21--23; 96/96 slices, 1,258 aggregate rows, integrity passed |

The following are explicitly **not** remaining prerequisites: the separate 25,000-fact M1 scale
branch and the optional M3-lexical arm. They were excluded by Document 133 and do not block the
completed M2-clean/M3-fact family. The remaining work is post-gate scientific interpretation and
an explicit decision about whether this valid two-seed negative/inconclusive result is sufficient
for the thesis narrative or whether a new amended experiment should be designed. No new GPU job,
third seed, dose change, checkpoint change, or gate relaxation should be started automatically.
