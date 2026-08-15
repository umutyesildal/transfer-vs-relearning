# Current project status

**As of:** 2026-08-15 | **Phase:** evaluation foundation design
**Readiness:** `ready_to_measure = false`, `ready_to_train = false`

## Executive state

The project is not restarting and the existing code is not disposable. The completed Qwen pilot,
model-screening runs, evaluation scripts, corpus tooling, Slurm launchers, scientific records,
papers, and study notes have been preserved in one verified local monorepo.

The next scientific bottleneck is measurement stability. Document 178 gives the end-to-end design,
but it does not yet freeze exact LM Evaluation Harness task IDs, revisions, datasets, prompts,
few-shot settings, metrics, normalization schemas, checkpoint cadence, missingness semantics, or
gates. Those details must be qualified and frozen as `eval-v1` before opening a new training
family.

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

The valid next work is local evaluation inventory and qualification:

1. map existing custom evaluators, configs, schemas, and historical result formats;
2. identify which metrics are already scientifically usable and which need parity repair;
3. pin and validate the intended LM Evaluation Harness task matrix;
4. define one normalized row schema for M0/M1/M2-A/M2-B checkpoints;
5. freeze cheap versus full evaluation cadence and failure/missingness semantics;
6. add deterministic parity, identity, and resume tests;
7. only then freeze `eval-v1`.

This status does not authorize downloading tasks, running evaluation, accessing HU, using Slurm,
training a model, materializing a corpus, pushing the migration branch, or cleaning artifacts.

## Repository state

The migration branch `migration/monorepo-v1` is local-only. It preserves the main repository
history and imports the synthetic-data history under `tools/synthetic-data/` without squash. The
original two worktrees remain rollback sources. See the
[`migration record`](../migration/REPOSITORY_MIGRATION_V1.md).

Publication is still blocked. The imported synthetic-data history contains eight reachable blobs
at or above 10 MiB (about 361 MB total, largest about 76.6 MB). New ignore rules do not rewrite
existing history. No blob was removed because that would require an explicit choice among full
history preservation, Git LFS migration, or a rewritten history backed by an external archive.

## Canonical links

- Machine state: [`PROJECT_STATE.yaml`](PROJECT_STATE.yaml)
- Authority/read routing: [`AUTHORITY.md`](AUTHORITY.md)
- Ordered work: [`ROADMAP.md`](ROADMAP.md)
- End-to-end design: [`../178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md`](../178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md)
- Supervisor evaluation-first direction: [`../177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md`](../177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md)
