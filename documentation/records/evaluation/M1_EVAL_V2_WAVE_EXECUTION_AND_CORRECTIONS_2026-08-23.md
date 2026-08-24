# M1 eval-v2 wave execution and corrections record (2026-08-23)

**Purpose.** Single delegation-ready record of the matched three-model M1 eval-v2 wave on
2026-08-23: every submission, cancellation, contract correction, root cause, fix, live state and
the exact procedure a future agent must follow. Read `AGENTS.md`,
`documentation/current/START_HERE.md` and this file; then the cited contracts/configs.

**Status at snapshot time:** wave RUNNING under Correction 6 — 4/111 canonical complete,
0 failed, 3 tasks running (`476315_4/_5/_6`), throttle 3 of 6, snapshot UTC
`2026-08-23T13:10:39Z`.

## 1. Starting context

- M1 training was complete: retry family `/vol/tmp2/yesildau/m1_matched_three_model_retry_v1`
  (jobs 475850–475852), 37 tracked states per model (parent + 36 epoch snapshots), 111 total.
- The prior session's adapter existed but its frozen contract bound stale code hashes and its
  final audit round was unfinished: `src/transfer_vs_relearning/study/m1_eval_validation.py`
  was orphaned (imported nowhere), parents were scheduled for GPU re-scoring, full→cheap
  derivation and per-output validation were not wired.

## 2. Correction chain, submissions and cancellations

| # | Contract state | Config | What happened | Jobs | Outcome |
|---|---|---|---|---|---|
| C0 | draft | — | Hash-mismatch discovered (contract §4 vs disk); fail-closed, nothing ran | — | fixed by rebinding |
| C1 | append-only §7 | `..._v1.yaml` `65c70265…` | Single A100 array `0-110%3` frozen → corrected pre-execution to 108 GPU tasks + parent projections before any submission | — | superseded pre-execution |
| C1 exec | §7 final `37ce73bf…` | `65c70265…` | Submitted; user cancelled ~15 min in to accelerate | pre `475878`, array `475879`, fin `475880` | 0 scientific results; root `_v1` preserved + `cancellation.json` |
| C2 | §8 `00f4f9dd…`→`14775401…` | v2 dual-route | GRES name wrong (`a6000` ≠ `rtxa6000`) → test-only refused; never-submitted-root recovery added; resubmitted | pre `475894`, arrays `475895/96`, fin `475897` | external non-Slurm user occupied RTXA6000 GPUs (~45 GiB); 20 GiB gate failed 68 tasks fast; user cancelled ("solid path") ; root `_v2` preserved + marker |
| C3 | §9 `145bc669…` | v3 single pool `3795bfda…` | All-108 A100 array throttle 6; started, then 6 tasks failed at exact-prefix step | pre `475976`, array `475977`, fin `475978` | cancelled after root cause found |
| C4 | §10 `43f52098…` | v3 rebound `12376c0d…` | Hotfix: evaluator required manifest key `local_path`/`parameter_count` that M1 binding manifests lack (`local_path_absolute`); added in-wave failed-attempt archival convergence | — | see C5 stall |
| C5 | §11 `3baabbaa…` | v3 rebound `b6947d3c…` | Resume subcommand + preflight tolerance for terminal-failed states; first resume stalled (stale matrix hashes + fresh-root check), refixed | pre `476217`, array `476218`, fin `476219` | ran 33 min, then superseded mid-flight by C6 fixes |
| **C6 active** | **§12 `c5df1a3a…`** | **v3 final `81369818…`** | Exact-prefix output-layout validator fix (timestamped run subdir); per-task retry loop (24 × 300 s) inside each allocation; `%J` unique logs; bounded sweep rule (≤10 resumes) | **pre `476314`, array `476315`, fin `476316`** | **RUNNING** |
| C7 staged (not authorized) | §13 `e379966f…` | v3 rebound `faeabb9e…` | Full-bundle states exceed the 24 h array wall: `olmo/epoch-018` killed at limit (step `476783`, no result file), `olmo/epoch-036` reached the same wall with live progress; in-allocation `scontrol update TimeLimit` denied by cluster policy; array wall raised to `2-12:00:00` via one frozen module constant; zero scientific changes; Correction 6 sweep budget unchanged | — | prepared 2026-08-24, awaits user authorization |

All hashes above are SHA-256. Full prior-hash chain lives in
`documentation/current/PROJECT_STATE.yaml → stage_readiness.m1_evaluation`.

## 3. Root causes and their permanent fixes

1. **Stale hash binding** — contracts must be re-hashed after ANY code edit; executor verifies
   contract+config+adapter hashes at build and preflight (fail-closed).
2. **GRES identity** — cluster names are `gpu:a10080gb:1` and `gpu:rtxa6000:1`; always verify
   with `scontrol show node <n> | grep Gres=` before freezing a route.
3. **Externally occupied GPUs** — Slurm `AllocTRES` empty does NOT mean physically idle. The
   frozen per-task gate (`assert_free_gpu_memory`, 20 GiB via `CUDA_VISIBLE_DEVICES` +
   `nvidia-smi -i <idx>`) is mandatory and stays.
4. **Manifest key drift** — M0-era manifests carry `local_path`; M1 binding manifests carry
   `local_path_absolute`. `evaluation/evaluator.py` now resolves through `_manifest_local_path`
   and treats `parameter_count` as optional. No metric changed.
5. **Exact-prefix output layout** — evaluator writes one timestamped subdir under the raw root;
   `validate_exact_prefix_output` locates files by unique recursive match.
6. **Convergence gaps** — terminal-failed states are archived as `<id>__failed_<n>` (renamed,
   never deleted) and re-executed in-wave; killed-partial dirs were moved once to `__killed_0`
   by hand under C6 authority (17 preserved evidence dirs total). Preflight tolerates
   terminal-failed states but still rejects ANY `complete` result or unreadable state.

## 4. Live operating rules (do not break)

- Exactly ONE wave = matrix identity + output root
  `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3`. Sweeps use ONLY the `resume`
  subcommand (max 10, each logged to `control/resume_log.jsonl`). Never re-initialize, never
  delete anything, never touch `__failed_*`/`__killed_*` dirs.
- Complete states are untouchable; only `status:"failed"` states may be archived+re-executed.
- Finalizer closes `complete` ONLY at 111/111 canonical results (108 measured + 3 M0-parent
  projections from canonical v1f evidence). Missing/failed are recorded honestly, never zeroed.
- Pile-10k forbidden; seeds/prompts/thresholds are frozen; no outcome-aware changes.
- Routes: ONLY `gpu:a10080gb:1`. V100/RTX6000/RTXA6000/RTX3090 are forbidden (C3 decision).
- Gate schedule: 13 probes, 600 s apart. Task retry loop: 24 attempts, 300 s apart.

## 5. Monitoring and sweep procedures

```bash
# status snapshot (from ssh-client/, helper reads .env)
./scripts/hu_ssh_expect 'R=/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3/results; \
  echo COMP=$(grep -rl "\"status\": \"complete\"" $R --include=task_result.json | grep -vE "__failed|__killed" | wc -l); \
  echo FAIL=$(grep -rl "\"status\": \"failed\""  $R --include=task_result.json | grep -vE "__failed|__killed" | wc -l); \
  squeue -j 476315 -h -t RUNNING -o "%.12i %.8M %N"'
```

Observed dense-task duration: **~30–35 min** (e002=2008 s, e003=2105 s, e004=1815 s).

If tasks end `failed` after exhausting retries and the cause is fixed and committed:

```bash
# sweep (Correction ≤6 semantics): rebuild matrix under current identities + resubmit
PYTHONPATH=src /vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python \
  scripts/study/execute_m1_eval_v2.py resume \
  --config configs/pipelines/eval_v2_m1_matched_{olmo,qwen,smollm}_v3.yaml \
  --repo-root . --contract documentation/contracts/evaluation/m1-matched-three-model-eval-v2-v1.md \
  --contract-sha256 c5df1a3a1ac3c072648f561b5eb6a7921015c98bed5a1900fc83f6271ca14a5d \
  --execution-config configs/evaluation/m1_eval_v2_matched_three_model_v3.yaml \
  --execution-config-sha256 8136981802d4e8958c73f6a63fc93dfc35a784e7a4446303b4f1f85665d1f441 \
  --matrix /vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3/control/task_matrix.json
```

⚠️ After ANY new commit the contract/config SHAs change → recompute with `shasum -a 256` and
use the NEW values (this bit us twice). `PROJECT_STATE.yaml` is the hash source of truth.

## 6. Completion checklist (at 111/111)

1. `control/evaluation_family_result.json` → `status:"complete"`, `complete_count:111`.
2. Verify finalizer job `sacct -j 476316`; archive logs inventory sha256.
3. Record result in a new `documentation/records/evaluation/M1_EVAL_V2_WAVE_RESULT_<date>.md`;
   update `PROJECT_STATE.yaml` (m1_evaluation → executed_complete + jobs) and `STATUS.md`.
4. Next scientific boundary (separate authorization): trajectory normalization + presentation
   bundle from the 108×bundle outputs; M2-A/M2-B sibling planning stays blocked until then.

## 7. Delegation boundaries

The delegate may: monitor, run read-only diagnostics, execute sweeps per §12 within the ≤10
budget, and document results. The delegate may NOT: change routes/thresholds/seeds, cancel and
re-baseline without explicit user instruction, delete/relocate any artifact, authorize M2, push
to main, or treat missing results as zero. HU checkout moves only via
`git pull --ff-only origin agent/m1-pipeline-repair` after preservation checks (clean tree,
ancestor check, zero overlap).

## 8. Commit chain for this record's session

`2755751` freeze v2 → `866bd7b` rtxa6000 identity → `0a386fb` recovery semantics →
`b6bd5bb` correction-3 binding → `71f18a2` evaluator hotfix + convergence → `19757a7`
layout/retry/sweeps (C6, active) → subsequent commits update docs/state only.

## 9. Addendum (2026-08-24): Correction 7 preparation and live triage

Observed on HU (read-only diagnostics):

- 61/111 canonical results complete, 0 terminal failures under Correction 6 code.
- Array element 17 (`olmo/epoch-018`, step job `476783`) was killed by the scheduler at
  `2026-08-24T17:12:23 DUE TO TIME LIMIT` after ~24 h of verified progress; no
  `task_result.json` was written.
- Array element 35 (`olmo/epoch-036`, `_35`) was alive with log writes minutes before the same
  wall; a live `scontrol update JobId=476315_35 TimeLimit=…` extension attempt returned
  `Access/permission denied`.
- Triage of all 36 archived `__failed_*` attempts under `results/olmo/`: every archived failure
  predates the Correction 6 submission (stale layout/manifest/factual-incomplete evidence from
  Corrections 3–5 era). No crash-loop recurrence is evidenced under current code.

Prepared locally on branch `agent/m1-eval-walltime-correction`, not yet authorized or pushed:

- Contract append-only Correction 7 (§13): array wall clock `1-00:00:00` → `2-12:00:00`, one
  frozen module constant, control jobs unchanged, sweep budget unchanged.
- Rebound adapter module SHA `07f1ee77…`; entrypoint unchanged `e3b8eefe…`;
  rebound v3 config SHA `faeabb9e…` (`slurm.evaluation_time_limit` + rebound module binding).
- Focused test additions assert the new time limit in the submitted array command and the
  config↔module hash consistency.

Fastest-completion path proposed to the user on 2026-08-24, pending explicit authorization:
let the dense backlog drain, cancel the three remaining full-state array elements
(`476315_71` = `qwen/epoch-036`, `476315_89` = `smollm/epoch-018`, `476315_107` =
`smollm/epoch-036`) that would otherwise each hold a slot against the old 24 h wall, run the
afterany finalizer honestly at <111/111, then execute exactly one Correction-7-bound resume
sweep that re-runs every missing full state in parallel under the corrected wall clock.
