# M1 matched three-model eval-v2 execution contract v1

**Date:** 2026-08-22  
**Status:** `FROZEN / AWAITING EXACT SHA-BOUND AUTHORIZATION`  
**Scientific scope:** completed matched M1 trajectories for OLMo, Qwen and SmolLM

## 1. Single authorized objective

Execute one evaluation-only M1 wave over the already completed, immutable training family at
`/vol/tmp2/yesildau/m1_matched_three_model_retry_v1`. The wave evaluates the M0 parent and all 36
epoch-end M1 snapshots for each of the three fixed models, writes only to the fresh root
`/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v1`, and performs no training, network retrieval,
cleanup or source-artifact mutation.

The frozen execution config is
`configs/evaluation/m1_eval_v2_matched_three_model_v1.yaml` with SHA-256
`d08c175c94ee3c70edcb204c4bd1e3ec3929ceeb81e092783f1dddcf6b040d66`.

## 2. Closed input family

| Model | M1 checkpoint-manifest SHA-256 | M1 training-manifest SHA-256 | M0 parent-manifest SHA-256 |
|---|---|---|---|
| OLMo | `f1681974fb5aa8da8dece1d0af9786eca1013302a6bf39d3b4920015587c289c` | `68ad5c6b394918bbe5a57189ada0ebe6a14fe9c9213f658ffc1d4177d2935630` | `8702b80d5b7e4c996c8ce2ff5fe771ada08ab0080bde1926c0b1f53c607303dc` |
| Qwen | `08636e6df7d0fc532ccb5743f1a406da96d00dcdd4f0ab31194714a83d299dc0` | `0323b0088e2804b181cc0ade03a17868f8d37c16fe1ad7f483d73c501cc60b15` | `c9d3562b717784251fe14c2b7972660fe4a20fe4687e15f69746bc1713d2d4fb` |
| SmolLM | `6d64e96f4aab69df6621ca6506d06bc8bb55145e262caea2d76794a3b33e5d7c` | `638a9066484e8695f9600f7991441b9622a1b63596d3184d55e25606d13a138c` | `e5d04302087b8b41828f734c1d88c4620a74bb80d6919de62df37b9d57dadbfc` |

Every checkpoint manifest must contain exactly `parent, epoch-001, …, epoch-036` in order. Every
referenced model manifest and training manifest is re-hashed before namespace creation and again
inside the execution chain. Missingness is never converted to zero.

## 3. Frozen scientific evaluation

Every one of the 111 states receives:

- identity and training-trace binding;
- 1,500-probe bilingual cheap factual access;
- the historical 500-probe exact-prefix candidate-ranking supplement;
- WikiText English retention through LM Evaluation Harness;
- frozen `trwiki-20260601` Turkish cross-domain retention control;
- generation-integrity evaluation.

The parent, epoch 18 and epoch 36 for every model additionally receive:

- the 12,000-probe bilingual full factual suite;
- BLiMP;
- HellaSwag;
- Winogender female/male/neutral slices;
- the pinned `juletxara/turblimp` TurBLiMP task family.

Pile-10k remains retired and is forbidden. Eval-v2, all frozen registries, prompt identities,
scoring definitions, seeds, revisions and comparison gates remain unchanged.

## 4. Execution adapter and topology

The registered adapter is `slurm_m1_matched_wave_v1`:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `fa2aafdd0d465a01d53036788395968428bb0460ac16de329587de3ee4cd3734`
- `scripts/study/execute_m1_eval_v2.py` —
  `6205c1365588a0d006109c0c93e0c813a154e8c302a8045aac57b1c5adb981f9`

The only permitted DAG is:

```text
read-only final preflight
→ A10080 array 0-110%3 (one checkpoint state per task)
→ afterany family finalizer
```

The finalizer records every complete, failed or missing state and emits `complete` only at 111/111.
It does not normalize incomplete results or choose a model.

## 5. Storage and safety

- HU home is read-only and remains below the existing 30 GiB policy limit.
- Dataset/model caches are reused offline; network retrieval is forbidden.
- Training outputs, M0 results and prior failed roots are immutable.
- The output root must not exist at final preflight.
- No retry, rerun, threshold change, M2 action, cleanup or deletion is authorized.
- A submission failure after partial job creation must be recorded; it does not authorize a second
  wave.

## 6. Authorization boundary

Preparation, local tests and hashing do not authorize publication, HU fast-forward, output-root
creation, Slurm submission or evaluation. One exact authorization naming this contract SHA-256
and the frozen execution-config SHA-256 is required. After that authorization, the permitted
sequence is ordinary non-force push, preservation-checked HU fast-forward, final preflight and one
three-job DAG submission.

## 7. Append-only correction 1 (2026-08-23, pre-execution)

This correction is recorded before any execution. The original sections above remain preserved;
where a statement below conflicts with them, the statement below governs.

7.1 Superseded statements. The §4 adapter hashes `fa2aafdd…` / `6205c136…` are superseded; the
§4 DAG line "A10080 array 0-110%3 (one checkpoint state per task)" is superseded; and the §1
execution-config SHA-256 `d08c175c94ee3c70edcb204c4bd1e3ec3929ceeb81e092783f1dddcf6b040d66` is
superseded by `65c70265844a7ea94be80498546da2625b41bf2ea83beeafbda156ae70e28db8`. No other
section is reinterpreted.

7.2 Rebound execution adapter. The registered adapter `slurm_m1_matched_wave_v1` now binds:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `d573a0e0aaf342971cbc68068f9004e80f46de988b3de7513381aa01ced098e9`
- `scripts/study/execute_m1_eval_v2.py` —
  `0123fe5921b9e4e7c2ce61e74785ad5ead810914155e095d0beb55e3624b004d`

7.3 Topology. The permitted DAG is:

```text
read-only final preflight
→ A10080 array 0-107%3 over the 108 real M1 epoch snapshots (36 per model)
→ afterany family finalizer that projects the three M0 parent states
```

The wave closes scientifically only at 111/111 states: 108 measured snapshot states plus three
parent projections. A missing or failed state is never converted to zero or rescored.

7.4 Parent projection without rescoring. The M0 parent of each model is not re-measured on GPU.
At finalization the parent state is written as a reference projection from the canonical,
hash-closed M0 evidence bundle `/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1f`
(config `configs/evaluation/eval_v2_m0_metric_normalization_v1f.yaml`, SHA-256
`3781cd62e6bfa1d3484bd87f54b44000eb9aae35a8b0260ad31b93cc15d56047`; v1b source registry with 24
rows). The bundle must close through its own `final_inventory.json` hash chain and yield exactly
42 attributed metric rows, 14 per model; otherwise the finalizer fails closed and the wave is
incomplete.

7.5 Full-state cheap-factual derivation. At the nine full states (parent, epoch 18 and epoch 36
per model), the 12,000-probe full factual suite is scored once and the 1,500-probe cheap rows are
derived by filtering the precommitted cheap probe IDs from the full scores. The cheap rows at
full states are never separately rescored; their metric definition is unchanged and each derived
row carries its source full-probe identity. Dense states measure the 1,500-probe registry
directly as before.

7.6 Per-state validation gate. A snapshot task may record `complete` only after: byte-level
snapshot verification against the training-time snapshot manifest, harness results including full
denominators without limits, complete factual outputs, a complete 500-probe exact-prefix result,
a complete trwiki cross-domain perplexity result bound to corpus SHA-256
`15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8` with exactly 10,034
documents, and a complete generation-integrity panel.

7.7 Authorization binding. The single authorization sentence must name this corrected contract
SHA-256 and the corrected execution-config SHA-256 recorded in `documentation/current/
PROJECT_STATE.yaml` under `m1_evaluation`. Authorization remains one wave; no retry, rerun or
threshold change is authorized.

## 8. Append-only correction 2 (2026-08-23, dual-route acceleration)

This correction is recorded after the user explicitly chose to cancel the Correction-1 wave
before any scientific result was produced. Where a statement below conflicts with earlier
sections, the statement below governs.

8.1 Superseded statements. The §7.2 adapter hashes are superseded by the hashes in 8.2; the
§7.3 single-array topology is superseded by the dual-route topology in 8.3; and the Correction-1
execution-config identity `configs/evaluation/m1_eval_v2_matched_three_model_v1.yaml`
(SHA-256 `65c70265844a7ea94be80498546da2625b41bf2ea83beeafbda156ae70e28db8`) is superseded by
the frozen `configs/evaluation/m1_eval_v2_matched_three_model_v2.yaml`.

8.2 Rebound execution adapter:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `9e73da74be19402817862821f281d05ce9c69816b208fb3c089dbe9c114f7778`
- `scripts/study/execute_m1_eval_v2.py` —
  `85c5e8f0488cab89f787266e116262f806c46a5cdfba48842b7d1fadd3594d53`

8.3 Dual-route topology. The permitted DAG is:

```text
read-only final preflight
→ RTXA6000 array 0-71%8 over the qwen+smollm epoch snapshots (gpu:rtxa6000:1)
→ A10080 array 0-35%3 over the olmo epoch snapshots (gpu:a10080gb:1)
→ afterany family finalizer that projects the three M0 parent states
```

Array-local task ids map to global matrix indices through frozen offsets: the A100 array covers
indices 0–35 (olmo), the A6000 array covers indices 36–107 (qwen, smollm). All other §3
evaluation semantics — bundles, cadence, full-state cheap derivation, parent projection,
111/111 closure — are unchanged from Corrections 0 and 1.

8.4 Route policy. Only two GPU resource types are authorized for this wave:
`gres=gpu:rtxa6000:1` and `gres=gpu:a10080gb:1`. V100, RTX6000, RTX3090 and every other card type
are forbidden. The A6000 pool is expected to resolve to the currently idle gruenau7/gruenau8
nodes; the scheduler may place either route on any node offering the declared resource type.

8.5 Per-task GPU free-memory gate. Before scoring, every task probes free memory on its Slurm-
allocated GPU (`CUDA_VISIBLE_DEVICES`, first entry) via `nvidia-smi`. Fewer than
21,474,836,480 bytes (20 GiB) free is a fail-closed task failure recorded as `failed`; missing
values are never converted to zero or skipped. The gate threshold is frozen and not
outcome-aware.

8.6 Cancelled Correction-1 attempt. The Correction-1 wave was submitted as preflight job
`475878` (completed), evaluation array `475879` and finalizer `475880`. The user cancelled it
roughly fifteen minutes after the first three snapshot tasks started; no task had reached a
scientific result. The root `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v1` is preserved
read-only as the cancelled-attempt evidence with an appended cancellation marker, and the fresh
output root for this correction is `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v2`.
The cancellation consumed no scientific measurement and does not count as the one authorized
wave of this correction.

8.7 Authorization binding. The single authorization sentence must name this corrected contract
SHA-256 and the frozen v2 execution-config SHA-256. Authorization remains exactly one wave
across both arrays plus preflight and finalizer; no retry, rerun, throttle change after
submission, or threshold change is authorized.

8.8 Never-submitted root recovery. The first v2 start attempt passed the full hash closure,
created the fresh output root, and then failed at the `sbatch --test-only` stage because the
A6000 GRES name is `gpu:rtxa6000:1`; no job was submitted and no scientific artifact exists.
Re-running under this correction may re-initialize the SAME output root only when all of the
following hold, verified in code before any write: the root contains
`control/submission_manifest.json` whose status starts with `not_submitted`, zero
`results/*/*/task_result.json` files exist, and that manifest parses as JSON. Any other existing
root fails closed exactly as before. The re-initialized preflight record sets
`recovered_stale_root: true`. This recovery never applies to a root from a submitted wave; it
does not authorize deletion of any path.

## 9. Append-only correction 3 (2026-08-23, single A100 pool)

Recorded after the user explicitly chose the most conservative reliable path when the A6000
pool proved externally occupied. Where a statement below conflicts with earlier sections, the
statement below governs.

9.1 Cancelled Correction-2 attempt. The dual-route wave was submitted as preflight `475894`,
A6000 array `475895`, A100 array `475896` and finalizer `475897`. The per-task 20 GiB gate
correctly refused states landing on A6000 GPUs occupied by a non-Slurm external process
(~45 GiB in use); 68 tasks failed fast at the gate, zero scientific results were written, and
the user cancelled the wave. The root `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v2`
is preserved read-only as this cancelled-attempt evidence with an appended cancellation marker.
The cancellation consumed no scientific measurement.

9.2 Rebound execution adapter:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `acfee0ec5067fcbbac08ee2a8a92fd7f6f8708bebb7546d1048aa838635969a3`
- `scripts/study/execute_m1_eval_v2.py` — unchanged from Correction 2:
  `85c5e8f0488cab89f787266e116262f806c46a5cdfba48842b7d1fadd3594d53`

9.3 Single-route topology. The permitted DAG is:

```text
read-only final preflight
→ single A10080 array 0-107%6 over all 108 epoch snapshots (gpu:a10080gb:1)
→ afterany family finalizer that projects the three M0 parent states
```

The only authorized GPU resource type is `gpu:a10080gb:1` on either gruenau node that offers
it. V100, RTX6000, RTXA6000, RTX3090 and every other card type are forbidden. All §3 evaluation
semantics remain unchanged from earlier corrections; closure still requires 111/111.

9.4 Frozen gate probe schedule. Before scoring, every task probes free memory on its allocated
GPU. On gate failure the task waits exactly 600 seconds and re-probes, for at most 13 probes
total; only after all 13 fail does the task record `failed`. The schedule is frozen,
not outcome-aware, and bounded well inside the 1-day task limit. Missing probe values are
never converted to zero or skipped.

9.5 Frozen execution config. `configs/evaluation/m1_eval_v2_matched_three_model_v3.yaml`
(SHA-256 `3795bfda6c021d6c1063a6729d80ab13f2e98a5a091f24e437c1336cad25f629`) supersedes
`configs/evaluation/m1_eval_v2_matched_three_model_v2.yaml`
(SHA-256 `099d64b6b41250ab14081293e0be4ffce91dcb6efae49929d79cc9861bd5feec`). The fresh output
root is `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3`.

9.6 Authorization binding. The single authorization sentence must name this corrected contract
SHA-256 and the v3 execution-config SHA-256. Exactly one wave; no retry beyond the frozen
in-task gate schedule, no throttle change after submission, no threshold change.

## 10. Append-only correction 4 (2026-08-23, exact-prefix hotfix)

Recorded after the Correction-3 wave began executing and six tasks failed at the third
evaluation command. Where a statement below conflicts with earlier sections, the statement
below governs.

10.1 Cause. `src/transfer_vs_relearning/evaluation/evaluator.py` hard-required the manifest key
`local_path` (and `parameter_count`) when writing its run metadata. M0-era model manifests
carry those keys; the M1 training-binding manifests carry `local_path_absolute` /
`tokenizer_source_path_absolute` instead. The failure was environmental-code drift, not a model
score; all other commands of the affected tasks had already succeeded.

10.2 Hotfix. `evaluator.py` now resolves the snapshot through `_manifest_local_path` (which
already accepts both key spellings) and records `parameter_count` as optional metadata. No
metric, denominator, prompt or scoring definition changed.

10.3 Rebound execution adapter module:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `b92ca6a14d03f340b2657f6880b5b8f758d824991aa9d2c3d9471a2f62d515f5`

The entrypoint is unchanged from Corrections 2–3:
`85c5e8f0488cab89f787266e116262f806c46a5cdfba48842b7d1fadd3594d53`.

10.4 In-wave failed-attempt convergence. Within this single authorized wave, `run-task` may now
re-execute a state whose existing terminal `task_result.json` has `status: "failed"`. Before
re-execution the entire prior attempt directory is renamed in place to
`<checkpoint_id>__failed_<n>` and preserved read-only; complete states remain untouchable and
missing states behave exactly as before. The finalizer counts only canonical paths and still
closes only at 111/111. This does not authorize any deletion, any second submission after a
terminal family result, or any change to thresholds or measurement semantics.

10.5 Resubmission binding. The Correction-3 matrix and output root
(`/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3`) remain canonical; resubmission reuses
the existing initialized matrix without re-initialization. A new authorization sentence naming
this corrected contract SHA-256 and the rebound v3 execution-config SHA-256 (`12376c0df070df076abc6b7d0cdb46fe56a48db76cdec0fa1c8dd59574e2ae83`)
is required before the remaining array work continues.


## 11. Append-only correction 5 (2026-08-23, resume and preflight convergence)

Recorded after the Correction-4 resubmission stalled before execution: the stored matrix still
carried Correction-3 authorization hashes while the checkout already held Correction-4 files,
and the preflight freshness check refused terminal-failed results that Correction 4 explicitly
allows to converge. Both behaviors are now frozen as follows.

11.1 Superseded statements. The §10.3 module hash and §10.5 execution-config SHA-256 are
superseded by the identities below. No measurement semantics change.

11.2 Rebound execution adapter:

- `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `3a473327749746b502a9bb52e32f2608482860b60a1c070f9293b8c1093d62b6`
- `scripts/study/execute_m1_eval_v2.py` —
  `e3b8eefe6420f9c1eddf7f13a3548c32355ff203618b9a14c157f8047bebfd1a`

11.3 Preflight convergence rule. The read-only preflight rejects any canonical state whose
terminal result is `complete` or unreadable; canonical terminal-`failed` states are counted
(`preexisting_failed_results`) and allowed, because they are exactly what Correction 4's
in-wave convergence re-executes.

11.4 Resume operation. A new `resume` subcommand rebuilds the task matrix under corrected
identities and may replace a stored matrix ONLY when the rebuilt 108-task signature is
byte-identical to the stored one and the output root is unchanged; every rebinding is appended
to `control/resume_log.jsonl` with prior/new matrix digests. Any task divergence is refused.

11.5 Authorization binding. The single authorization sentence must name this corrected contract
SHA-256 and the rebound v3 execution-config SHA-256 recorded in `documentation/current/
PROJECT_STATE.yaml`. Exactly one wave continues; all earlier prohibitions stand.

## 12. Append-only correction 6 (2026-08-23, output layout, retry loop, sweeps)

12.1 Cause. The exact-prefix evaluator writes each run into a single timestamped
subdirectory of the configured raw root; the wave validator expected a flat layout, producing
false failures after otherwise successful evaluations. Separately, one task failed early with
an unknown transient error whose per-attempt logs were truncated by an array requeue.

12.2 Fixes. The validator now locates `summary_metrics.json` and `per_fact_results.csv` by
unique recursive match under the raw root (any single layout). Each array element now runs a
frozen retry script inside its own allocation: at most 24 attempts,
300 seconds apart, before recording `failed`. Per-attempt Slurm logs use
unique `%J` suffixes so requeues never truncate history. No metric, denominator, prompt or
scoring definition changed.

12.3 Bounded sweep convergence. The authorized wave is defined by its matrix identity and
output root: it may be resumed (`resume` subcommand, logged rebinding) repeatedly to sweep
terminal-`failed` states until either 111/111 canonical completeness or the user stops it,
with at most ten resumes for this correction. Complete states are never re-executed; deletions
remain forbidden.

12.4 Rebound execution adapter module:
`src/transfer_vs_relearning/study/m1_wave_executor.py` —
`2f2acc8a296348ade96eb5b6358c52e1aeca5574808b15bdff229e0d07aab97a`
(entrypoint unchanged: `85c5e8f0488cab89f787266e116262f806c46a5cdfba48842b7d1fadd3594d53`).

12.5 Authorization binding. A sentence naming this corrected contract SHA-256 and the rebound
v3 execution-config SHA-256 (`8136981802d4e8958c73f6a63fc93dfc35a784e7a4446303b4f1f85665d1f441`) authorizes continuing the running wave under
these semantics, including sweep resumes without further sentences.

## 13. Append-only correction 7 (2026-08-24/25, evaluation-array wall clock and derived-factual validator)

13.1 Cause. Two operational defects blocked full-bundle scientific states while dense states
completed normally:

(a) The frozen 24-hour array time limit is shorter than full-state runtime. Array element 17
(`olmo/epoch-018`, Slurm step job `476783`) was cancelled by the scheduler at
`2026-08-24T17:12:23` (`DUE TO TIME LIMIT`) after ~24 h of verified forward progress and wrote
no `task_result.json`. Array element 35 (`olmo/epoch-036`) reached the same wall with live log
writes minutes earlier. Dense states complete in roughly 30–35 minutes, so this limit had never
been exercised before the full states. An in-allocation `scontrol update TimeLimit` extension was
attempted and denied by cluster policy (`Access/permission denied`); the partition `MaxTime` is
`4-00:00:00`.

(b) The full→cheap factual derivation always failed its own final validation. On 2026-08-25 the
running wave recorded the first live terminal failure (`qwen/epoch-018`, element `_53`):
`Factual output is incomplete; expected 1500 probes`. Root cause: `derive_cheap_factual_from_full`
writes summary status `completed_derived_from_full_without_rescoring`, while
`validate_factual_output` accepted only exactly `completed`, so every full state failed at final
validation after completing all expensive scoring stages. The executor tests did not catch this
because they mock the derivation function.

13.2 Fixes. Two fail-closed corrections, no scientific semantics changed:

(a) The evaluation-array wall clock is raised from `1-00:00:00` to `2-12:00:00`, applied through
one frozen module constant (`EVALUATION_TIME_LIMIT`) used identically by the
`sbatch --test-only` route validation and the real array submission. Control preflight and
finalizer limits are unchanged.

(b) `validate_factual_output` now accepts both frozen complete statuses — native `completed` and
derived `completed_derived_from_full_without_rescoring` — via an explicit allowlist constant;
unknown statuses still fail closed. A dedicated regression test exercises the real derivation
end-to-end (12,000-row synthetic full evidence, 1,500-row frozen cheap registry) plus positive
and negative validator paths.

No metric, denominator, prompt, seed, scoring definition, route, GRES identity, throttle or
topology value changed in either fix.

13.3 Continuity. These corrections change no completed result and touch no output directory. The
bounded sweep semantics of Correction 6 continue unchanged with the same maximum of ten resumes
for this wave; the next sweep re-executes only terminal-failed or never-completed states under
the corrected wall clock and the corrected validator. All other archived `__failed_*` attempts
under the wave root predate the Correction 6 submission; the only C6-era recurrence is defect
(b) above.

13.4 Rebound identities.
- Adapter module: `src/transfer_vs_relearning/study/m1_wave_executor.py` —
  `eacb239142435dd1bfa0ddaea624207a03c34c0bfbf35e4c1752765a723b5315` (adds an early
  `already_complete` skip guard in `run_task`, makes `preflight_matrix` count pre-existing
  complete results instead of rejecting them, and auto-archives hard-killed attempt directories
  without a terminal result as `<id>__killed_<n>` evidence before re-execution; unreadable state
  result files still fail closed)
- Validation module: `src/transfer_vs_relearning/study/m1_eval_validation.py` —
  `66fb5f4c1bdcc5c6f0501420001fd892bd6eea1f29ec8b81ae6dd6c72c412779`
- Entrypoint unchanged from Correction 5:
  `scripts/study/execute_m1_eval_v2.py` —
  `e3b8eefe6420f9c1eddf7f13a3548c32355ff203618b9a14c157f8047bebfd1a`
- Rebound v3 execution config: `configs/evaluation/m1_eval_v2_matched_three_model_v3.yaml` —
  `3fd83349e7da1986651b5bfceb0942ed491b7671ff97ff33d4a9b89444ece83b`

13.5 Authorization binding. A sentence naming this corrected contract SHA-256 and the rebound
v3 execution-config SHA-256 (`3fd83349e7da1986651b5bfceb0942ed491b7671ff97ff33d4a9b89444ece83b`)
authorizes sweep resumes of the running wave under these semantics. This correction authorizes no
M1/M2 training, corpus materialization, cleanup, deletion, publication or second-wave submission.
