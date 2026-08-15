# Bounded Sol/Luna orchestrator

This optional local control plane runs a persistent Sol reviewer and Luna executor through the
Codex CLI. It is designed for small, bounded local tasks with explicit acceptance criteria.

It does not expand project authority. External work stops for user authorization.

## Context model

Every role starts with the small live set:

1. root `AGENTS.md`;
2. `documentation/current/PROJECT_STATE.yaml`;
3. `.agents/POLICY.md`;
4. `.agents/GOAL.md`;
5. the current decision/report and only its named evidence.

The complete numbered record and `LUNA_WORKER_CURRENT_HANDOFF.md` are no longer mandatory per-turn
reads. A task may name them when they are actually relevant.

## Roles

- **Sol (`gpt-5.6-sol`)**: read-only director/reviewer; decides one next task.
- **Luna (`gpt-5.6-luna`)**: executes only that task inside its allowed paths.

Luna is the default implementation worker because bounded micro-tasks do not need a large inherited
conversation. Sol checks meaning, scope, and evidence between tasks.

## Files

```text
.agents/
├── config.json
├── POLICY.md
├── GOAL.md
├── orchestrator.py
├── prompts/
├── schemas/
├── tests/
├── state/       # ignored local runtime state
└── runs/        # ignored local evidence
```

## Safe workflow

1. Write one concrete `GOAL.md` with `Status: ACTIVE`, a unique Goal ID, acceptance criteria,
   allowed paths, and prohibitions.
2. Review the goal against the root state and applicable contracts.
3. Run local checks:

   ```bash
   python .agents/orchestrator.py doctor
   python .agents/orchestrator.py run --dry-run
   ```

4. Bootstrap persistent sessions only when desired; this creates external model calls:

   ```bash
   python .agents/orchestrator.py bootstrap --yes
   ```

5. Start the bounded loop:

   ```bash
   python .agents/orchestrator.py run
   ```

6. Inspect `.agents/state/` and `.agents/runs/`; they are local evidence and are not committed.

## Dispatch boundary

Only `local_read_only` and `local_write` decisions are automatically dispatchable. The loop stops
for HU/SSH, Slurm/GPU, network retrieval, evaluation/scoring, training, push/publication,
destructive work, secret access, or changes to frozen evidence.

The worker may touch only `allowed_paths`. The orchestrator snapshots the single monorepo before
and after the turn and stops without reverting if an unexpected path or Git HEAD changes.

## Micro-task design

A good Luna task has:

- one objective that fits a single context window;
- explicit files or narrow globs;
- observable acceptance criteria;
- a short evidence list;
- no need to infer a scientific decision;
- no reliance on chat memory.

Examples: add one schema validator, inventory one evaluator family, normalize one historical output
shape, or write tests for one resume invariant.

A bad task is “finish the experiment,” “read all documents and decide,” or a mixed code + remote
execution + interpretation wave.

## Goal lifecycle

`GOAL.md` is a replaceable task packet, not a project status document.

- `NOT_SET`: no active orchestrator goal;
- `ACTIVE`: one bounded goal may run;
- `COMPLETED`: retained only until its evidence is recorded, then reset to the template.

Project truth remains in `documentation/current/PROJECT_STATE.yaml` and immutable evidence.

## Tests

```bash
python -m pytest .agents/tests
```

The pre-control-plane 1,147-line manual is preserved byte-for-byte under
`documentation/records/workspace-guidance/`.
