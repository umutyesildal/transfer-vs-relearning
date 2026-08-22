# Current project status

**As of:** 2026-08-22 | **Phase:** Pile-10k retired; eval-v2 frozen; M0 projection pending
**Readiness:** `ready_to_measure = true`, `ready_to_train = false`

## Executive state

The project is not restarting and the existing code is not disposable. The completed Qwen pilot,
model-screening runs, evaluation scripts, corpus tooling, Slurm launchers, scientific records,
papers, and study notes have been preserved in one verified local monorepo.

The active measurement boundary is now eval-v2. On 2026-08-22, before M1 training and before any
M1/M2 scientific result, the user retired Pile-10k from the canonical protocol. eval-v2 inherits
every other eval-v1 identity, metric, gate, cadence and missingness rule; WikiText remains primary
English retention. Pile is no longer a task, lane, gate, normalization denominator or blocker, and
no Qwen Pile retry is required. The historical eval-v1 contract, 24-lane submission, raw results
and operational failures remain immutable evidence.

All seven non-Pile lanes already exist for each of OLMo, Qwen and SmolLM, giving 21/21 source lanes
for a hash-closed eval-v2 M0 projection. The three-model exact-prefix supplement is also complete.
The fail-closed projector is implemented and tested locally. Its authorized read-only discovery
pass resolved exactly 21 non-Pile scientific lanes plus three exact-prefix supplement rows, with
all 24 lane hashes and four top-manifest hashes verified. It rejected no source, mutated no HU
file, and performed no rescoring. The observed hashes are preserved in
`documentation/evaluation/M0_EVAL_V2_SOURCE_BINDING_DISCOVERY_2026-08-22.md`; the frozen
pre-discovery config remains unchanged, so projection still requires a new SHA-bound config and
separate authority.
The execution-enabled v1b projection completed in its fresh HU root with exactly 24 hash-verified
source rows and zero metric rows. The reference closure is complete, but metric extraction and
normalization remain a separate authority boundary; M1/M2 work and cleanup remain closed.
eval-v2 freeze does not authorize normalization execution, M1/M2 training, HU/Slurm work, cleanup
or publication; `ready_to_train` remains false.

A separate no-retraining M1 historical inventory and trajectory-table schema are also prepared.
They cover the retained Qwen seed-42/43, OLMo dose/Pareto and SmolLM control families, preserve
missing epochs explicitly and defer all large-weight hashing. They have not run and do not make the
heterogeneous historical recipes a matched three-model M1 comparison.

The local pipeline foundation is now opt-in and fail-closed. It derives an exact epoch/update/batch
schedule, records tokenization and optimization traces, preserves model-only epoch snapshots behind
storage guards, plans dense/full evaluation in order, and initializes typed `planned_not_run`
artifact/presentation namespaces. It does not yet execute LM Eval or project evaluation stages.

The full-study controller now expresses the 19-stage M0→M1→M2-A/M2-B dependency graph, preserves
the sibling-parent and matched-budget gates, and produces one bounded Luna adapter packet per stage.
The M0 standard and project adapters plus a single operator-facing controller now exist locally.
That controller performs task-data preflight, submits seven independently GPU-routed lanes, joins
them with one finalizer and writes a consolidated result plus hashed raw-artifact manifest. The
full-study CLI remains dry-run because all later-state adapters/execution authority do not exist yet.
The former flat entrypoint roots were losslessly grouped: 129 scripts and 135 Slurm files are mapped
by `configs/entrypoints/catalog.json`; historical numbered documents were not rewritten.

The three-model matrix now expands that workflow across the exact OLMo, Qwen2.5-1.5B and
SmolLM2-1.7B assets. It contains 39 nodes in thirteen three-job waves: 24 state-evaluation nodes,
nine training nodes and six local preflight/analysis nodes. It can render 39 one-model/one-stage
Luna packets. Exact-prefix is mandatory at M0, M1, M2-A and M2-B and blocks downstream analysis
when incomplete. The matrix is `planned_not_authorized`; its scientific
M0 bindings now exist and have a separate single-wave authorization, while M1/M2 recipe configs
remain explicit blockers rather than inferred placeholders.

The first machine-readable M0 preflight has now run on the new M0 branch. It stopped before model
load, inference or scoring, as designed. The current blockers are the draft study/eval contracts,
unresolved model/output bindings, `ready_to_measure = false`, the absent dedicated `lm_eval`
HU environment and, at that time, the absent M0 standard/factual adapters. Those adapters are now
implemented and frozen for the bounded qualification wave. The local dependency is
locked and installed directly from Harness v0.4.12 commit
`6d642546f4688648fced259eb3302efd36ece5af`; its installed VCS identity passed preflight. This is
`blocked_pre_scoring`, not an M0 scientific result.

The next boundary is written as the
[`M0 OLMo qualification draft`](../contracts/evaluation/m0-olmo-qualification-v1.md) with a
machine-readable companion config and one operator-facing entrypoint. The current topology is
one task-data preflight followed by seven independent GPU lanes—WikiText, Pile-10k, BLiMP, other
English capability, Turkish capability, factual access and generation integrity—distributed across
scheduler-qualified GPU types where capacity exists, followed by one `afterany` evidence finalizer.
It binds the
exact OLMo and Harness revisions, separates limited smokes from scientific scores, requires fresh
immutable artifacts, and enumerates the environment/data/parity/resource fields still needed for
freeze. The user authorized the bounded qualification attempt on 2026-08-16. Two rejected scratch
environment attempts were retained before any data/model/GPU work; the accepted v3 environment
proves Torch 2.6.0+cu124, CUDA 12.4 and exact Harness commit identity. Implementation hashes,
environment lock, V100 route, limits and resources are now inserted into the frozen config. The
CPU/data preflight and dependent test-only array are the next executable action.

The first submission attempt was operational `NOT_RUN`: Slurm rejected the CPU-only data preflight
before issuing any job ID because it was routed to `gpu` without a GPU request. The planned v1
namespace is preserved; no task retrieval, model load, GPU work or scoring occurred. A narrow repair
now routes control jobs to `std`, retains evaluation lanes on V100 and targets a fresh v2 namespace.
Its new implementation/config hashes must be frozen before resubmission.

The repair identities are now frozen: control jobs use `std`, GPU lanes retain the exact V100
request, and all three routes passed Slurm `--test-only`. After the final fast-forward and runtime
preflight, the fresh v2 namespace may be submitted under the existing test-only authorization.

The v2 run is now closed as blocked qualification evidence. Harness task validation returned 10/10
but materialized a zero-byte cache; three offline Harness lanes therefore failed before scoring.
The factual lane exposed an absent active-checkout registry path, and cancellation caught the
generation lane after weight load but before a completed result. The finalizer recorded 0/7 complete,
`partial_invalid`, normalization disabled and no scientific result. The preserved v3 repair must
perform online task instantiation, non-empty cache inventory, offline re-instantiation and exact
project-input hash checks before another GPU dependency can open.

The v3 materializer/project-input repair is now hash-frozen under the existing test-only
authorization. The next action is final HU fast-forward plus readiness preflight; only then may its
fresh namespace submit the online-materialize → offline-reload → dependent V100 chain.

V3 then proved that the new materializer gate works: it created 338 cache files / 409,436,401 bytes
and kept the GPU array closed when offline reload failed. The remaining blocker is upstream XNLI's
legacy `dataset_path: xnli`, incompatible with the current Hub's official `facebook/xnli` identity.
No v3 GPU/model/scoring work ran. A compatibility overlay was prepared for v4, but the user removed
that task family from the thesis protocol before v4 CPU materialization completed. Jobs `461253`
and `461254` were cancelled before GPU work; finalizer `461255` recorded 0/7 lanes, no scientific
result and a blocked gate. The 18-file root is preserved. V5 keeps the same seven-lane topology but
uses eight standard Harness task IDs and no local task overlay. The compatibility failure and a
possible future upstream repair are isolated in the evaluation incident note. V5 implementation,
project configs, task set and fresh namespace are now hash-frozen under the existing bounded
test-only authorization. V5 then materialized all task data but failed after TaskManager returned,
when the controller tried to sort mixed string/`ConfigurableGroup` result keys. No GPU/model/scoring
work ran. V6 replaced only that diagnostic with a JSON-safe loaded-entry count. Its data preflight
then passed all eight task constructions and offline reload, and its factual/generation lanes
completed. Five Harness lanes stopped before scoring because pip-installed Harness could not find
the repository test-root required by redundant CLI `--check_integrity`; v6 is preserved as a 2/7,
blocked, non-scientific run. V7 keeps the successful controller preflight, removes only that
packaging-dependent duplicate check, submits seven independent per-lane GPU jobs from the same
script and adds `evaluation_results.json` alongside the complete raw-artifact manifest. Its exact
implementation, project configs, companion config and fresh v7 namespace are frozen under the
user's bounded test-only rerun authorization. V7 submission then showed that six lanes had immediate
V100/RTX6000 estimates while the seventh had been assigned to an RTXA6000 estimate almost twenty
hours later. The entire v7 chain was cancelled during incomplete CPU preflight and before any GPU
lane, model load or scoring; its seven control files are preserved. V8 adds a frozen 900-second
earliest-start window: later eligible routes remain audited but are excluded, and near-term declared
slots are reused for overflow lanes. The one-command evaluation/result behavior is unchanged and the
fresh v8 namespace was executed once. Six lanes completed; `english_capability` failed before
scoring on an RTX6000 occupied by a foreign 20.41 GiB process. The frozen recovery verified all six
source lanes by identity/hash, reused the existing offline cache, required 16 GiB free VRAM and ran
only the missing lane on V100 job `461595`. Finalizer `461596` produced a 7/7 composite bundle with
normalization enabled. The bundle is still `test_only_non_scientific`; its qualification gate is
blocked only by WikiText count/result/heading parity and TurBLiMP 16-subtask macro parity. No
scientific M0 result or training authority follows.

That parity boundary is now closed. The frozen v2 parity wave reproduced canonical WikiText word
PPL, byte PPL and BPB exactly, reproduced TurBLiMP's 16-subtask `acc_norm` macro at `0.40625`, and
completed the predefined Markdown-heading sensitivity on V100 job `461668`; finalizer `461669`
reported `parity_pass`. An earlier pre-submission root is preserved because it exposed and stopped
on a validator error: upstream `acc_norm` uses Python Unicode string length, while byte-normalized
accuracy is a distinct descriptive sensitivity. Document 179 records both roots and hashes. The
qualification gate is `qualified_for_eval_v1_freeze_review`. Document 180 then froze the exact
scientific dataset/environment identities, Pile cadence, TurkishMMLU/XCOPA exclusions, 12,000-row
full and 1,500-row cheap factual registries, numeric margins and checkpoint-binding policy.

## Evaluation design result

- LM Evaluation Harness is pinned prospectively to v0.4.12 commit
  `6d642546f4688648fced259eb3302efd36ece5af` in the frozen dedicated environment lock.
- Official WikiText BPB is primary English retention; word/byte PPL remain reported.
- Pile-10k was qualified historically under eval-v1 but is retired from eval-v2; it has no active
  task, gate, lane or retry.
- BLiMP, HellaSwag, WinoGender slices and TurBLiMP form the frozen capability bundle;
  TurkishMMLU and XCOPA-TR remain outside eval-v2.
- Project-native factual ranking, robust intersections, relation swaps, paired subject bootstrap
  and generation integrity are preserved.
- Canonical results are long tables; one-row-per-checkpoint output is a generated view.
- Future dense evaluation covers the parent and every epoch end; full evaluation is proposed at
  entry/midpoint/endpoint. Historical OLMo remains limited to its seven existing weight states.
- Retention is raw BPB plus ΔBPB; PPL ratio is companion evidence and retention score is plot-only.
- Training trace, typed normalized tables and presentation metadata are mandatory future outputs.

See the [`evaluation read set`](../evaluation/README.md), the active
[`eval-v2`](../contracts/evaluation/eval-v2.md), and the
[`Pile retirement decision`](../decisions/PILE_10K_RETIREMENT_AND_EVAL_V2_DECISION_2026-08-22.md).

## Fixed design direction

```text
M0 → M1
      ├── M2-A: matched fact-free Turkish adaptation
      └── M2-B: matched Turkish adaptation + controlled factual re-exposure
```

M2-A and M2-B start from the same frozen M1 checkpoint. Their total budgets and evaluation bundle
must be matched. The primary causal contrast is M2-B minus M2-A; M2-A versus M1 measures transfer
after fact-free Turkish adaptation.

## Preserved evidence

- The Qwen Wikipedia-only family remains a historical pilot with verdict
  `primary_success_criterion_not_met`.
- The OLMo/Pythia/Falcon 500-fact screen produced three valid negative results and no automatic
  primary-model selection.
- The later dose/Pareto family remains incomplete at 15/18 cheap-evaluation rows because Falcon
  checkpoints 126, 210, and 252 are missing. No family summary or selected model follows.
- vngrs remains a conditional corpus materialization candidate. It is not materialized or frozen
  for training. `trwiki-20260601` is a cross-domain control; CulturaX remains access-blocked.

These are constraints and evidence, not reasons to throw away existing implementation.

## Active work boundary

The active task is a local, read-only-to-source eval-v2 M0 projection:

1. select exactly the seven completed non-Pile lanes for each of OLMo, Qwen and SmolLM;
2. verify every selected source path and SHA-256 without rescoring;
3. attach the completed three-model exact-prefix supplement;
4. normalize only after 21/21 lane identity and schema checks pass;
5. preserve the historical eval-v1 family, every Pile attempt and all failure evidence unchanged.

No Qwen Pile retry is needed. No evaluation, training, HU synchronization, Slurm work, cleanup or
publication is authorized by the eval-v2 decision. M1/M2 remain blocked until their exact model,
corpus and training contracts are frozen and separately authorized.

M1/M2 training, corpus materialization and scientific scoring remain unauthorized. They must not be
bypassed with ad-hoc commands.

The 2026-08-16 qualification/recovery/parity authorization remains consumed. A separate 2026-08-16
overlay authorized exactly one scientific three-model M0 wave and was consumed by the recorded
submission. It grants no automatic retry, second wave, M1/M2, corpus materialization, cleanup,
deletion or HU-home writes. The matrix planning contract itself still grants no external execution.

## Repository state

The monorepo cutover is complete. GitHub `main` is now fast-forwarded through
`9054392bdc17f1f4b6453f03b83a2d93ace297ac`; the evaluation and entrypoint changes are published,
and the active development branch is `agent/m0-evaluation`. Remote `main` includes `.agents`, documentation,
synthetic-data tooling, paper material, scripts, configs, and tests. The original two worktrees
remain rollback sources. See the
[`migration record`](../migration/REPOSITORY_MIGRATION_V1.md).

HU now has a separate clean monorepo checkout at
`/vol/tmp2/yesildau/transfer-vs-relearning-monorepo-v1`, tracking `agent/m0-evaluation` with
fast-forward-only pulls. The legacy HU `corpus-update` checkout is dirty and remains untouched as
preserved state. The shared HU Python environment has not been modified and does not contain
`lm-eval`; eval-v1 uses the separately frozen dedicated environment under `/vol/tmp2`.

The legacy HU `artifacts`/`runs` retention inventory is complete and source-preserving. It records
9,825 files / 742,915,363,463 bytes with manifest SHA-256
`daad386c19a74186f37e1319f7cf07a39161d5571c2478549710d7a25d138966`. The meaningful reclaim
candidate is not cache: 203 optimizer files from 34 closed training namespaces total
426,066,757,577 bytes. They remain proposal-only until every run has a selected/frozen model map
and separate exact cleanup authorization. See [`HU retention status`](HU_RETENTION_STATUS.md).

The reachable monorepo history now contains zero blobs at or above 10 MiB. Before filtering, the
exact 249-commit branch was preserved in a verified private Git bundle; the original source repos
were not changed. See the
[`history-sanitization record`](../migration/GENERATED_OUTPUT_HISTORY_SANITIZATION.md). Push and
cutover completed without force or merge commit. No additional push or branch mutation is
authorized by this status.

## Canonical links

- Machine state: [`PROJECT_STATE.yaml`](PROJECT_STATE.yaml)
- Authority/read routing: [`AUTHORITY.md`](AUTHORITY.md)
- Ordered work: [`ROADMAP.md`](ROADMAP.md)
- End-to-end design: [`../178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md`](../178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md)
- Supervisor evaluation-first direction: [`../177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md`](../177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md)
