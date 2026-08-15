# Document 134 - Qwen Pre-M2 GPU Blocker and Offline Preparation Status

**Date:** 2026-07-31  
**Status:** Four-probe GPU smoke passed; the full Phase D baseline wave is pending preflight and queue availability  
**Scope:** Frozen Qwen bilingual baseline smoke attempts and offline readiness work

## 1. Current decision

The two frozen Qwen M1 artifacts remain intact and hash-verified. Smoke 439733 successfully
reloaded and scored both artifacts on an allocated clean GPU, but the Phase D bilingual baseline
has **not** yet produced its full scientific result. No M2/M3 training, dose selection, or
principal baseline wave has been started. The immediate next task is the coordinated preflight and
48-slice baseline wave; the previous GPU/device-contamination blocker has been reduced to a
queue-availability risk.

The smoke job 439723 requested one A100 at a time and excluded `gruenau10` because another user's
long-running Python process was observed there. `gruenau9` was also allocated, so the job remained
pending with `ReqNodeNotAvail`. After the offline-preparation commit advanced the checkout, the
stale pending job was cancelled; no result directory or scientific output was deleted.

## 2. Smoke and loader incident ledger

| Job | Outcome | Interpretation |
|---|---|---|
| 439716 | Immediate `ExitCode=1` | Initial smoke launcher had a stale hard-coded commit guard. No evaluator execution. |
| 439718 / 439719 | Seed-43 task stopped on GPU guard; seed-42 reached evaluator and failed before model load | Seed-43 GPU had an existing Python compute process. Seed-42 exposed the frozen-selected manifest format incompatibility. |
| 439721 | Both tasks stopped on GPU guard | Both assigned GPUs on `gruenau10` had an existing compute process. |
| 439723 | Pending, `ReqNodeNotAvail` | `gruenau10` is excluded because GPU 1 still has PID 22926 using about 8.7 GiB; `gruenau9` is allocated. No evaluator execution. |

The v1 seed-42 output directory contains only an empty 4 KiB directory. The v1 seed-43 and v2
result directories were absent. These attempts therefore contain no usable per-probe evidence and
must not be treated as baseline observations.

## 3. Corrections made before execution resumes

The following corrections are committed on `corpus-update` and pushed:

- Turkish Form D and field-of-study template ambiguity was narrowed before materialization;
- the bilingual evaluator now uses `answer_language` for gold resolution, candidate surfaces, and
  same-subject confusable scoring;
- the evaluator loader now supports the frozen selected-artifact manifest format
  (`files.model.safetensors.path`) and its `training_manifest` tokenizer provenance;
- the smoke launcher now requires the submit-time commit, uses a clean scratch root, serializes
  seed tasks, and records only scratch output;
- the smoke launcher log directives were corrected to match its v3 scratch root;
- a fail-closed 60,000-probe baseline aggregator was added;
- a CPU preflight, 48-slice evaluation launcher, and submit wrapper were prepared but **not
  submitted**.

The relevant local tests and shell checks pass for the changed evaluator, aggregator, smoke
launcher, baseline preflight, and baseline slice launcher. The broad baseline remains gated on the
coordinated preflight and successful completion of all 48 slices.

## 4. Storage and path state

The latest HU preflight observed approximately 14 GiB in the shared home, below the explicitly
approved 30 GiB ceiling. `/vol/tmp2` had approximately 114 TiB available and 3% inode use. The
repository `artifacts` and `runs` paths resolve to `/vol/tmp/yesildau/transfer-vs-relearning`, and
the Qwen contract and selected model artifacts remain on approved scratch paths. No new large home
file was created by these smoke attempts.

## 5. What remains gated

The following order remains unchanged from Document 133:

1. Completed: run the two-model GPU reload/scoring smoke on a clean compatible device (439733).
2. Run the single coordinated preflight and then the 48 fixed bilingual baseline slices.
3. Aggregate direction, relation, form, scaffold, Branch A/B, robust-intersection, forced-choice,
   tokenizer, and generic-PPL evidence for both frozen seeds.
4. Only after the complete baseline package is available, freeze factual cycles, endpoint, gates,
   and the matched M2/M3 CPU materialization.

No result-based checkpoint selection or M2/M3 training decision is permitted while Phase D is
incomplete.

## 6. CPU-only M2/M3 analysis package prepared

In parallel with GPU execution gating, the repository now contains a fail-closed analysis path for
the future matched M1/M2-clean/M3-fact outputs:

- `scripts/analyze_qwen_m2_m3_results.py` accepts a JSON manifest of state IDs, arms, seeds, and
  either `per_probe_results.csv` or `hard_suite_per_fact.csv`;
- `src/transfer_vs_relearning/metrics/qwen_m2_m3.py` verifies identical probe IDs and static
  metadata across states before computing any contrast;
- state summaries cover direction, relation, form, scaffold, Branch A/B, frequency, name, rarity,
  popularity, and the planned cross-dimension slices;
- paired M2-minus-M1, M3-minus-M1, and M3-minus-M2 changes use subject-level bootstrap intervals;
- `branch_interactions.csv` reports the precommitted interaction `(M3-M2)_B - (M3-M2)_A`;
- robust eight-cell intersections and their paired contrasts are emitted separately; and
- the generated manifest explicitly records that no threshold or gate is selected by the script.

The synthetic end-to-end CLI test and the full local test suite excluding the previously known
system-Python `yaml` collection failure both passed. This package prepares analysis only; it does
not fabricate baseline results and does not open the Phase D or M2/M3 execution gates.

## 7. CPU-only M2/M3 launcher family prepared

The remaining operational preparation is also now in the repository, without submitting any
Slurm work:

- `scripts/prepare_qwen_m2_m3_training_family.py` consumes a later `status=frozen` Phase-E
  contract and creates matched full-sequence pretokenized configs for `m2_clean` and `m3_fact` on
  seeds 42 and 43;
- the generator checks block size, `fact_cycles`, artifact hashes, matched token budgets, and
  scratch-only placement before writing configs;
- `scripts/validate_qwen_m2_m3_training_family.py` performs a second fail-closed check;
- `slurm/preflight_qwen_m2_m3.slurm` performs the required home/storage/inode/path checks; and
- `slurm/train_qwen_m2_m3_array.slurm` plus `scripts/submit_qwen_m2_m3.sh` encode the four-run
  dependency chain and clean-GPU guard.

The launcher tests, Python compilation, and shell syntax checks pass. The family remains dormant:
it cannot be materialized or submitted until Phase D produces both bilingual baseline packages and
Phase E freezes dose, endpoint, update budget, and gates. The successful smoke validates the
execution path, but it does not open the M2/M3 gate.

## 8. Fresh GPU smoke attempt 439733

After replacing the node-wide GPU guard with an allocated-device guard, the current smoke array was
submitted once at commit `e33abea7474803c4fa54cc5e5a4b2abfa91e4dec`:

- `439733_0` (`qwen_m1_seed42_step75`) entered `RUNNING` on `gruenau10` with
  `CUDA_VISIBLE_DEVICES=0`;
- the selected model manifest and seed/checkpoint identity passed verification;
- the allocated GPU started at 18 MiB and passed the clean-device guard despite unrelated
  processes on GPU1/GPU2;
- the model loaded successfully, initial stderr is empty, and the scratch output root is
  `/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_v3/results/seed42_step75`; and
- `439733_1` (`qwen_m1_seed43_step50`) remains pending behind the array throttle `%1`.

At the initial post-submit check this was still only a four-probe smoke and had not produced a
baseline scientific result; the array was left running and no unrelated GPU process or old job was
interrupted. Its final outcome is recorded below.

## 9. Final outcome of smoke 439733

The serialized array completed both four-probe tasks on `gruenau10` using the allocated clean
device (`CUDA_VISIBLE_DEVICES=0`). The two result directories are complete under
`/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_v3/results/`; `squeue` no longer lists job 439733.
`sacct` could not provide terminal accounting because the HU accounting service returned a Munge
authentication error, so the evaluator completion markers and output files are the authoritative
evidence for this smoke.

| Model | Probes | Top-1 | Relation-swapped forced choice | Failure taxonomy |
|---|---:|---:|---:|---|
| `qwen_m1_seed42_step75` | 4 | 1/4 (25%) | 2/2 | 2 `prompt_form_failure`, 1 `early_eos_preference`, 1 `none` |
| `qwen_m1_seed43_step50` | 4 | 1/4 (25%) | 1/2 | 2 `prompt_form_failure`, 1 `early_eos_preference`, 1 `none` |

Both tasks emitted `status=smoke_passed`; no evaluator failure occurred. Stderr contained only the
Transformers `torch_dtype` deprecation warning and normal weight-loading progress. The probe-level
pattern was the same for both seeds: `lives_in` was retrieved correctly, while `born_in` and
`field_of_study` were wrong and `profession` triggered early-EOS preference. This is a loader/GPU
compatibility smoke, not evidence for the full baseline: the four probes use one subject and one
prompt form. Phase D therefore remains gated on the coordinated 48-slice bilingual baseline.

## 10. Full baseline wave submission 439737/439738

After the fresh submit-time checks passed, the full baseline chain was submitted once:

- preflight job 439737 is running in the std partition on node gruenau;
- dependent GPU array 439738 is pending with the expected afterok:439737 dependency;
- the array has 48 tasks with throttle 1, one A100 per task, and a three-hour per-task limit;
- the expected output root is /vol/tmp2/yesildau/qwen_pre_m2_baseline_v1;
- the family estimate is zero new checkpoints and approximately 16 GiB of scratch working space;
  retention is per-probe evidence plus compact summaries, with no checkpoints; and
- preflight stderr was empty at the first post-submit check. No baseline GPU task had started yet,
  so its device guard and stderr remain to be checked after dependency release.

The submit-time audit recorded 14 GiB in HU home, 114 TiB available on /vol/tmp2, 3% /vol/tmp2
inode use, and scratch-resolved repository runs/artifacts paths. Existing unrelated pending jobs
were not changed.

## 11. Baseline array 439738 aborted by allocated-device guard

The preflight 439737 completed successfully in 3m40s and produced the frozen manifest. After the
dependency released, array 439738 repeatedly landed on gruenau10 with the allocated selector
mapped to a device showing 8,735 MiB in use. The fail-closed guard identified the existing process
as PID 22926 (python, approximately 8,710 MiB) and rejected the device before model loading.

Tasks 0 through 41 reached the same guard failure; 42 non-empty task stderr files were observed.
No result files were created under the baseline output root, so this wave produced no scientific
observation and did not load either selected model. The remaining array tasks were cancelled with
scancel 439738 to avoid spending more queue slots on guaranteed guard failures. The preflight job
439737 and its manifest remain valid. A retry is not authorized by this report until a fresh queue
and allocated-device check confirms a clean A100; no duplicate baseline submission was made.

## 12. Current A100 availability check

At the live check after the aborted array, no clean A100 was available. gruenau9 was mixed with
all three A100s allocated. gruenau10 was also mixed with one Slurm-accounted A100 allocation, and
the host-level process list showed active processes on all three physical A100s: PID 50228 on GPU0
(772 MiB), PID 22926 on GPU1 (8,710 MiB), and PID 45045 on GPU2 (11,412 MiB). The scheduler
therefore provides no reliable start-time estimate. Retry only after a newly allocated device
passes the compute-process guard; no retry was submitted during this check.

## 13. RTX 3090 fallback smoke attempts

Because no clean A100 was available, a probe-limited RTX 3090 fallback was prepared and pushed at
commit 039695c. The first attempt, array 439783, was scheduled on guppi5 even though Slurm
reported the node as idle; its allocated RTX 3090 contained PID 7344 using approximately 24,100
MiB, so both tasks stopped at the allocated-device guard before model loading. No result files
were produced.

The launcher was then constrained to the currently idle guppi8 node. Array 439785 task 0 entered
RUNNING on guppi8 with an RTX 3090 at 15 MiB and emitted gpu_preflight=clean; task 1 remains
pending behind the intentional array throttle of 1. Its scratch root is
/vol/tmp2/yesildau/qwen_pre_m2_baseline_smoke_rtx3090_v1. This is still only a compatibility
smoke; the full A100 baseline plan remains unchanged until the fallback behavior and memory fit
are confirmed.

Task 0 of array 439785 then completed on guppi8 in 2m31s:

- the RTX 3090 reported 24,576 MiB total and 15 MiB before evaluation;
- the allocated-device guard passed and the frozen seed-42 model loaded successfully;
- all four probes completed with status smoke_passed and top1=1/4;
- stderr contained only the Transformers torch_dtype deprecation warning and normal loading
  progress; and
- task 1 (seed 43) is running on the same constrained node behind the array throttle.

Task 1 of array 439785 completed on guppi8 in 22s with the same clean-device and model-load
checks. Its four-probe result was status smoke_passed with top1=1/4; stderr again contained only
the Transformers torch_dtype deprecation warning and normal loading progress. Both frozen Qwen M1
artifacts therefore pass the RTX 3090 reload/scoring smoke. The next gated step is a fresh
scratch/storage preflight followed by the full 48-slice baseline using the validated 3090 path.

## 14. Full RTX 3090 baseline submission 439787/439788

After the fresh submit-time storage, inode, path, queue, and output-root checks passed, the
RTX 3090 baseline chain was submitted once at commit 53b5d8f:

- preflight 439787 is RUNNING in the std partition on node gruenau;
- dependent array 439788 is pending with afterok:439787 and throttle 1;
- the array has 48 tasks, one RTX 3090 per task, and excludes the contaminated guppi5, guppi6,
  and guppi7 nodes;
- the scratch output root is /vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1;
- the preflight retains no checkpoints and estimates approximately 16 GiB of scratch working
  space; and
- both initial preflight log files were empty at the first post-submit check.

The baseline task has not started yet; its allocated-device guard and first slice must pass before
any scientific output is treated as valid.

The dependency subsequently released and array 439788 began on guppi8. At the first progress
check, preflight 439787 had completed with status baseline_preflight_passed, tasks 0 through 5 had
completed 2,500-probe slices successfully, and task 6 was RUNNING with gpu_preflight=clean. The
completed task stderr files contained only the Transformers torch_dtype deprecation warning and
normal weight-loading progress; their result directories contain the expected per-probe evidence
and baseline_slice_complete markers. No duplicate array was submitted.

## 15. Full RTX 3090 baseline completion and first result readout

Array 439788 has now reached terminal state with all 48/48 slice tasks complete. The output root
contains 48 summary files, 48 stdout files, 48 stderr files, and 48
`status=baseline_slice_complete` markers. No task reported
`unexpected_gpu_compute_processes_on_allocated_device`, and the allocated-device guard therefore
passed for the full wave. The scratch root currently occupies approximately 635 MiB at
/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1. The full post-run home `du` value could not be
re-obtained because the SSH session stopped at the password prompt; the submit-time audit had
recorded 14 GiB in home, so this report does not claim a new exact post-run home total.

Each selected model was evaluated on 24 slices of 2,500 probes: 60,000 probes per model and
120,000 probes across both seeds. Integrity checks passed for both models: all probes were unique,
there were no empty expected answers or predicted surfaces, all three directions and four forms
were present, and predictions were candidate rankings rather than answer-cue strings.

The exact point estimates from the completed 60,000-probe evaluations are:

| Metric | Seed 42, step 75 | Seed 43, step 50 |
|---|---:|---:|
| Global top-1 | 60.12% | 60.63% |
| EN→EN | 99.29% | 99.24% |
| TR→EN | 52.03% | 52.52% |
| TR→TR | 29.05% | 30.12% |
| Robust 8-cell EN→EN | 96.08% | 96.28% |
| Robust 8-cell TR→EN | 22.52% | 23.44% |
| Robust 8-cell TR→TR | 14.96% | 16.80% |

The two seeds are closely aligned, with seed 43 approximately 0.5 percentage points higher on
global top-1. English retrieval is near-ceiling, while the cross-lingual directions are the main
bottleneck. At the relation level, `field_of_study`, `profession`, and `works_in_industry` are
the most fragile Turkish cells; for example, robust TR→TR accuracy is approximately 0.2--0.4%
for `field_of_study`, 3.2--3.8% for `profession`, and 3.2--5.2% for `works_in_industry` across
the two seeds. Form D is the weakest surface form at approximately 57.2--57.3%, and QA
scaffolding is approximately five points below direct prompting.

This is the completed factual 48-slice baseline point-estimate package, not yet the final gate
package: the current quick summaries used only 10 bootstrap samples for debugging. The
precommitted 2,000-subject-bootstrap confidence intervals and the generic English/Turkish PPL
audit still need to be generated before declaring the pre-M2 evaluation gate fully closed and
starting the M2/M3 training comparison.

## 16. Final CI and generic-PPL package launched

After a fresh coordinated preflight, the remaining baseline-package work was submitted from
commit `2e4d2430a74616e59ba8840bd9d0215f49d67a38`:

- HU home: 14 GiB, below the 30 GiB stop threshold;
- `/vol/tmp2`: 114 TiB available and 3% inode use;
- repository `runs` and `artifacts`: resolved to `/vol/tmp/yesildau/...` scratch paths;
- existing baseline root: approximately 777 MiB;
- planned additional output: approximately 2 GiB, scratch-only, with no checkpoints.

The final 2,000-bootstrap aggregation is job `439941` on `std`, outputting to
`/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/summaries_final`. It entered RUNNING on
`gruenau3` with an initially empty stderr file. The generic EN/TR PPL array is `439942`, throttled
to one RTX 3090 and excluding guppi5--7, outputting to
`/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/ppl_final`. Task `439942_0` entered RUNNING on
guppi8, reported 15 MiB GPU use, and passed `gpu_preflight=clean`; task `439942_1` is pending
behind the intentional array throttle. The PPL stderr was empty at the first check.

These jobs are left running. No M2/M3 training submission has been made; it remains gated on the
final CI and PPL package.

## 17. Final-package CI retry correction

At the 15-minute check, the first aggregation job `439941` had failed before reading the baseline
rows. Its launcher incorrectly required the historical baseline preflight manifest's `git_commit`
to equal the newer commit containing the aggregation launcher. This was a provenance assertion
error, not a data, slice, or model-evaluation failure. The job produced no summary files; it only
left an empty scratch directory, which was verified and removed with `rmdir`.

The assertion was corrected in commit `075777a`, pushed, and pulled on HU. A fresh storage/path
preflight again passed, and corrected CI retry `439947` was submitted to the `std` partition. At
the immediate retry check it was pending for `Priority`; its output and stderr were still empty.
The independent PPL task `439942_0` remained RUNNING on clean guppi8, with its English summary
already written and Turkish scoring still in progress; task `439942_1` remained behind the
intentional throttle.

## 18. PPL seed-42 completion and remaining retries

The next status check showed that PPL task `439942_0` completed successfully on guppi8. Both
English and Turkish summaries are present under
`/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/ppl_final/qwen_m1_seed42_step75`; stdout ends
with `status=ppl_complete`, `gpu_preflight=clean`, and stderr contains only the expected
Transformers `torch_dtype` deprecation/loading output. The array's seed-43 task produced no output
or log content and disappeared from the queue, while the HU Slurm accounting service was returning
Munge authentication errors, so its terminal reason could not be recovered from `sacct`.

The per-model output guard was corrected in commit `516b06d`, allowing a missing sibling task to be
retried without touching the completed seed-42 directory. A fresh storage/path preflight passed
again, and seed-43-only PPL retry `439949` was submitted with output
`ppl_final/qwen_m1_seed43_step50`. The corrected final-CI aggregation had likewise left no files;
after another fresh preflight, CI retry-2 `439950` was submitted to produce
`summaries_final`. At launch, both jobs were pending by normal scheduler priority.

## 19. Twenty-minute retry status: no execution evidence

At the next 20-minute check, neither `439949` nor `439950` remained in `squeue`, and neither had
written any summary, stdout, or stderr content. Seed-42 PPL remains complete and intact; seed-43
PPL and the final CI summary remain absent. The Slurm accounting query continued to fail with a
Munge authentication error, and `scontrol show job` could no longer retrieve the disappeared job
IDs. This is an infrastructure/scheduler observability issue, not a scientific result. No further
blind duplicate submission is recorded until the terminal state or a safer single-job submission
path is established.

## 20. Root cause identified and corrected retry launched

The missing-output retries were traced to an operator error in the manually constructed
`EXPECTED_COMMIT` value, not to Slurm scheduling. The remote checkout was at
`516b06d7e034f69df8d5bd819401952c7144908d`, while the retry commands used incorrect full hashes.
The first shell test in each launcher therefore exited silently before any diagnostic `printf`,
which explains the zero-byte stdout/stderr files and disappearance from `squeue`. The controller
was healthy (`scontrol ping` reported primary UP); the separate `sacct` Munge error is an
accounting-service observability issue but was not the cause of these exits.

The verified hash was used after a fresh storage/path preflight. Corrected jobs are now running:

- seed-43 PPL task `439955_1` on guppi8 RTX 3090, with `gpu_preflight=clean`;
- final CI aggregation `439956` on gruenau3 in `std`.

Both jobs have non-empty initial launch output. The previous empty-output retry records remain
historical failures and were not treated as scientific observations.

## 21. Corrected retry progress

At the 10-minute check, both corrected jobs were still RUNNING with valid output:

- PPL `439955_1` remained on guppi8 with `gpu_preflight=clean`, empty stderr, and completed the
  English seed-43 summary; Turkish PPL scoring was still in progress.
- CI `439956` remained on gruenau3 with clean storage/path preflight output and completed the final
  2,000-bootstrap summary for seed 42 (`60,000` probes). It had started the seed-43 summary and
  had not reported an error.

The final CI output now contains the verified seed-42 compact metrics, manifest, integrity summary,
forced-choice table, robust intersections, and 60,000-row per-probe evidence. Seed-43 CI and both
remaining Turkish PPL outputs are still required before the baseline gate closes.

## 22. Final CI/PPL package completed

Jobs `439955_1` and `439956` completed successfully. Both 60,000-probe CI packages report
`status=passed`, 60,000 unique probes, zero empty expected answers, zero empty predicted surfaces,
all three directions, all four forms, both scaffolds, and candidate-ranking predictions. The final
accuracy summaries use the precommitted 2,000 bootstrap samples.

| Metric | Seed 42, step 75 | Seed 43, step 50 |
|---|---:|---:|
| Global top-1 (95% CI) | 60.12% (59.74--60.51) | 60.63% (60.23--61.02) |
| EN→EN (95% CI) | 99.29% (99.17--99.40) | 99.24% (99.12--99.35) |
| TR→EN (95% CI) | 52.03% (51.34--52.73) | 52.52% (51.84--53.24) |
| TR→TR (95% CI) | 29.05% (28.42--29.67) | 30.12% (29.47--30.74) |

Generic PPL was also completed on the frozen 2,891-document English WikiText corpus and the
10,034-document contamination-audited Turkish validation corpus:

| Corpus | Seed 42, step 75 | Seed 43, step 50 |
|---|---:|---:|
| English PPL | 15.909 (15.437--16.387) | 15.170 (14.734--15.626) |
| Turkish PPL | 17.349 (17.212--17.499) | 15.741 (15.619--15.875) |

The post-run storage audit recorded 14 GiB in HU home, 114 TiB available on `/vol/tmp2`, and 3%
inode use on `/vol/tmp2`. No new large regular file was found in home beyond the already authorized
frozen model copies and environment libraries. The completed baseline root is approximately 850
MiB on scratch. The factual 48-slice and generic EN/TR baseline packages are now complete; M2/M3
training may proceed only after the Phase E dose/endpoint freeze and matched-input materialization.
