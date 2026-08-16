# Current project status

**As of:** 2026-08-16 | **Phase:** evaluation foundation design
**Readiness:** `ready_to_measure = false`, `ready_to_train = false`

## Executive state

The project is not restarting and the existing code is not disposable. The completed Qwen pilot,
model-screening runs, evaluation scripts, corpus tooling, Slurm launchers, scientific records,
papers, and study notes have been preserved in one verified local monorepo.

The next scientific bottleneck is measurement stability. Document 178 gives the end-to-end design,
and the first eval-v1 design pass now fixes the hybrid architecture, upstream harness release/task
semantics, metric roles, normalized schema and proposed dense/full cadence. eval-v1 remains a draft:
exact dataset revisions, environment/runtime evidence, parity checks, cheap-panel identity and
numeric scientific margins are not frozen. No new training family can open before those close.

The local pipeline foundation is now opt-in and fail-closed. It derives an exact epoch/update/batch
schedule, records tokenization and optimization traces, preserves model-only epoch snapshots behind
storage guards, plans dense/full evaluation in order, and initializes typed `planned_not_run`
artifact/presentation namespaces. It does not yet execute LM Eval or project evaluation stages.

The full-study controller now expresses the 15-stage M0→M1→M2-A/M2-B dependency graph, preserves
the sibling-parent and matched-budget gates, and produces one bounded Luna adapter packet per stage.
The M0 standard and project adapters plus a single seven-lane parallel Slurm-array controller now
exist locally; the full-study CLI remains dry-run because their frozen bindings and all later-state
adapters/execution authority do not exist yet.
The former flat entrypoint roots were losslessly grouped: 129 scripts and 135 Slurm files are mapped
by `configs/entrypoints/catalog.json`; historical numbered documents were not rewritten.

The first machine-readable M0 preflight has now run on the new M0 branch. It stopped before model
load, inference or scoring, as designed. The current blockers are the draft study/eval contracts,
unresolved model/output bindings, `ready_to_measure = false`, the absent dedicated `lm_eval`
HU environment and, at that time, the absent M0 standard/factual adapters. Those two adapter files
are now locally implemented, but they remain unqualified and unexecutable. The local dependency is
locked and installed directly from Harness v0.4.12 commit
`6d642546f4688648fced259eb3302efd36ece5af`; its installed VCS identity passed preflight. This is
`blocked_pre_scoring`, not an M0 scientific result.

The next boundary is written as the
[`M0 OLMo qualification draft`](../contracts/evaluation/m0-olmo-qualification-v1.md) with a
machine-readable companion config and one operator-facing entrypoint. The proposed topology is
one task-data preflight followed by seven independent GPU lanes—WikiText, Pile-10k, BLiMP, other
English capability, Turkish capability, factual access and generation integrity—with at most three
V100 lanes active, followed by an `afterany` evidence finalizer. It binds the
exact OLMo and Harness revisions, separates limited smokes from scientific scores, requires fresh
immutable artifacts, and enumerates the environment/data/parity/resource fields still needed for
freeze. The user authorized the bounded qualification attempt on 2026-08-16. Environment preparation
may proceed; task retrieval and test-only scoring remain fail-closed until the exact implementation
and environment identities are inserted into a frozen config.

## Evaluation design result

- LM Evaluation Harness is pinned prospectively to v0.4.12 commit
  `6d642546f4688648fced259eb3302efd36ece5af` in a dedicated future lock.
- Official WikiText BPB is primary English retention; word/byte PPL remain reported.
- v0.4.12 already includes `pile_10k`, so no custom replacement is currently needed.
- BLiMP, HellaSwag, WinoGender slices, XNLI-EN, TurBLiMP and XNLI-TR form the proposed capability
  bundle; TurkishMMLU remains conditional on access.
- Project-native factual ranking, robust intersections, relation swaps, paired subject bootstrap
  and generation integrity are preserved.
- Canonical results are long tables; one-row-per-checkpoint output is a generated view.
- Future dense evaluation covers the parent and every epoch end; full evaluation is proposed at
  entry/midpoint/endpoint. Historical OLMo remains limited to its seven existing weight states.
- Retention is raw BPB plus ΔBPB; PPL ratio is companion evidence and retention score is plot-only.
- Training trace, typed normalized tables and presentation metadata are mandatory future outputs.

See the [`evaluation read set`](../evaluation/README.md) and
[`eval-v1 draft`](../contracts/evaluation/eval-v1.md).

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

The valid next work is bounded evaluation qualification:

1. freeze exact dataset revisions/content manifests and the dedicated environment;
2. run task validation and bounded OLMo base/runtime smoke under separate authority;
3. prove canonical WikiText and TurBLiMP normalization parity;
4. decide Pile-10k cadence and TurkishMMLU inclusion;
5. freeze the cheap factual probe registry and numeric scientific margins;
6. add deterministic parity, identity, normalization and resume tests;
7. only then freeze `eval-v1`.

The planner/tracing and M0 adapter implementation may be tested and reviewed locally. Exact runtime,
dataset, project-evaluator and resource bindings remain before qualification execution; they must
not be bypassed with ad-hoc commands.

The 2026-08-16 authorization is limited to the qualification implementation, bounded HU preflight,
fresh scratch environment/task cache and test-only Slurm wave described above. It does not authorize
scientific M0 evaluation, training, corpus materialization, cleanup, deletion or writes to prior
evidence roots.

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
preserved state. The shared HU Python environment has not been modified and does not yet contain
`lm-eval`; eval-v1 will use a separately frozen dedicated environment.

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
