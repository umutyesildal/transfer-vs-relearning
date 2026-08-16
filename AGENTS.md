# Project Agent Instructions

These instructions apply everywhere in this monorepo. They are deliberately short and stable.
Live status belongs in `documentation/current/PROJECT_STATE.yaml`; historical facts belong in the
scientific record.

## Mandatory reading

Before any task, read:

1. this file;
2. `documentation/current/PROJECT_STATE.yaml`;
3. the user's current instruction or the current bounded task packet;
4. only the relevant contract, code, tests, and evidence named by that task.

For scientific interpretation, also read `documentation/current/STATUS.md`. For authority
questions, read `documentation/current/AUTHORITY.md`.

`AGENTS.md` alone is not sufficient for scientific execution. It defines durable behavior, not
the current model, dataset, gate, or authorization.

## Authority order

When instructions conflict, use this order:

1. system and developer instructions;
2. the user's current explicit instruction;
3. this `AGENTS.md`;
4. the current applicable frozen contract;
5. `documentation/current/PROJECT_STATE.yaml` and current gate;
6. task-local plans and implementation notes;
7. historical records.

Lower levels never create permission denied by a higher level. A plan, README, old authorization,
job script, or existing artifact is not execution authority.

## Project invariants

The research states are:

```text
M0   frozen pretrained base model
M1   M0 after controlled English factual adaptation
M2-A M1 after general Turkish adaptation without target-fact re-exposure
M2-B the same M1 after matched Turkish adaptation with controlled re-exposure
```

- M2-A and M2-B are parallel sibling arms from the same frozen M1 parent.
- M2-B must not receive extra total tokens merely because it contains factual rows.
- Training/evaluation budgets, seeds, sequence policy, checkpoints, and analysis rules must be
  matched or their differences explicitly contracted.
- The evaluation bundle must apply to M0, M1, M2-A, and M2-B. State-specific estimands may differ;
  measurement definitions must not silently drift.
- Missing results are not zero. Operational `NOT_RUN` evidence is not a scientific negative.
- A failed runtime, memory, tokenizer, or optimizer guard is not a model score.
- A positive point estimate is not automatically a replicated causal effect.
- Raw token perplexity is not automatically comparable across different tokenizers.
- Checkpoints, metrics, gates, and thresholds are not selected after seeing outcomes.

The completed Qwen pilot, three-model screen, dose/Pareto work, and corpus-access attempts remain
historical evidence. New work does not overwrite their outcomes.

## Current default boundary

Unless the user's current instruction and a relevant exact contract say otherwise:

- use the readiness and contract lifecycle values in `documentation/current/PROJECT_STATE.yaml`;
- a frozen evaluation contract does not itself authorize measurement;
- `ready_to_train: false` unless the current exact training contract says otherwise;
- the corpus contract is not frozen;
- no primary model is selected for the new main study;
- no HU/SSH, Slurm/GPU, training, evaluation, inference, scoring, model/tokenizer/corpus retrieval,
  push, publication, cleanup, or deletion is authorized.

An agent may inspect local files and make local changes that the user explicitly requested. A
local planning or documentation task does not authorize external work.

## Preservation and zero-loss rules

- Treat numbered scientific documents, manifests, results, paper sources, study notes, and local
  artifacts as project records.
- Never rewrite an old result to hide a failure or superseded decision.
- Prefer append-only correction or a new decision/contract when meaning changes.
- Preserve pre-existing dirty and untracked work. Do not reset, restore, stash, clean, or delete it.
- Never delete, overwrite, relocate, or deduplicate scientific/user material without an explicit,
  target-specific retention decision and a verified inventory.
- Before any later cutover, compare source and destination inventories and keep a rollback path.
- The original pre-monorepo worktrees remain rollback sources until cutover is separately approved.

## Monorepo rules

This workspace is one Git repository. The former synthetic-data repository lives at
`tools/synthetic-data/`. Its commit topology was imported without squash, then generated
`output/` paths were removed from the reachable monorepo history under the documented
publication-sanitization decision. The exact source history remains in the original repository and
a verified private pre-filter bundle.

- Inspect the repository before editing and preserve unrelated changes.
- Use repository-relative paths in docs, configs, manifests, and agent reports.
- Do not create a second source of truth by copying live code between top-level projects.
- Do not commit secrets, `.env` files, caches, virtual environments, raw model weights,
  checkpoints, large corpus shards, or generated run trees.
- Git-ignored data is still protected data; ignore rules are not cleanup permission.
- Commit only intentional files. Push, merge, release, or default-branch changes require the
  user's explicit request.

## Documentation rules

Each document has one role:

- root `README.md`: project and repository map;
- root `AGENTS.md`: stable operating rules;
- `documentation/current/PROJECT_STATE.yaml`: machine-readable live state;
- `documentation/current/STATUS.md`: concise human-readable synthesis;
- `documentation/current/AUTHORITY.md`: reading and authority routing;
- `documentation/current/ROADMAP.md`: ordered future work without granting execution;
- `documentation/contracts/`: exact prospective protocols and bounded execution contracts;
- `documentation/decisions/`: durable decisions and rationale;
- `documentation/records/` plus existing numbered docs: immutable evidence/history;
- manifests, JSONL, CSV, and result tables: exact artifact and metric data.

Do not put live job IDs, long run diaries, or repeated result tables in `AGENTS.md`. Do not create a
new global sequence number for routine progress. Update the smallest owning file and link to the
canonical evidence.

Numbered Documents 00–180 remain at their current paths until a separately reviewed link-safe
archive move. New current work uses the directories above.

## Contract discipline

A scientific or external execution contract must bind, as applicable:

- model, tokenizer, dataset, corpus, code, and environment identities;
- exact input and output namespaces;
- objective, sequence policy, budgets, optimizer, precision, seeds, and checkpoint grid;
- evaluation task names, revisions, prompts, few-shot settings, metrics, aggregation, and gates;
- failure semantics, resume policy, artifact schema, retention policy, and verification steps;
- allowed actions and explicit prohibitions.

Contract lifecycle is `draft → qualified → frozen → executed/superseded`. “Frozen” means semantic
changes require a new version or an explicit append-only correction before execution. No contract
may be called frozen while required task IDs, revisions, schemas, or thresholds are unresolved.

## Evaluation discipline

The target is one versioned evaluation contract reused across M0, M1, M2-A, and M2-B. Before it is
frozen:

- inventory current custom evaluators and historical outputs;
- pin and validate the LM Evaluation Harness version and exact task IDs;
- reconcile official WikiText rolling metrics with custom PPL behavior;
- qualify English retention/capability, Turkish capability, factual access, degeneration, and
  integrity panels;
- define a cheap checkpoint panel and precommitted full-suite milestones;
- freeze normalized result schemas, denominators, missingness semantics, confidence intervals,
  and gate directions;
- prove deterministic identity, resume safety, and base/checkpoint correctness with tests.

Document 178 is a design input, not the frozen `eval-v1` contract.

## Reproducibility and artifacts

- Every run must resolve immutable code, model/tokenizer, data, config, and environment identities.
- Use fresh output namespaces unless a contract explicitly defines safe resume behavior.
- Write manifests atomically and distinguish planned, started, partial, failed, `NOT_RUN`, and
  completed states.
- Keep raw evidence immutable; derive normalized tables and figures from it reproducibly.
- Large artifacts belong on approved scratch storage, never in Git or ordinary HU home storage.
- Before any HU family, read `ssh-client/README.md` and the applicable storage/experiment contract.
- Record hashes for selected or frozen artifacts before retention or cleanup decisions.

## Working method

- Inspect before changing.
- Make the smallest coherent change that satisfies the task.
- Reuse existing code and tests; current code is not disposable.
- Prefer configuration and schemas over duplicated one-off scripts.
- Separate diagnosis from implementation when the user asked only for analysis.
- Run tests proportional to risk and report exactly what ran.
- If a task would change scientific meaning, external state, cost, or retained evidence beyond the
  user's instruction, stop and request direction.

## Agent context budget

- Load the mandatory reading set first; do not read the complete chronological record by default.
- Follow links only when they are relevant to the current task.
- Put exact state in manifests/YAML and concise rationale in Markdown.
- End each task with a compact handoff: outcome, changed paths, tests, unresolved questions, and
  exact next boundary.
- Luna-sized workers should receive one bounded task, explicit allowed paths, acceptance criteria,
  and a small evidence list. A fresh worker should be able to start without inherited chat memory.

## Stop conditions

Stop rather than improvise when:

- the current state and applicable contract disagree;
- an immutable identity or required input cannot be verified;
- an action would exceed allowed paths or authority;
- output would overwrite an existing run/evidence namespace;
- a secret may be exposed;
- storage, GPU, dataset, or dependency preflight fails;
- preservation cannot be demonstrated;
- the result would require silently changing a metric, denominator, threshold, or protocol.

Use `documentation/current/AUTHORITY.md` to find the minimum additional reading set. The preserved
pre-control-plane instructions are indexed under `documentation/records/workspace-guidance/`.
