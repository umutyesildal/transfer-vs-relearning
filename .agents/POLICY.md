# Orchestrator Policy

## Source hierarchy

1. System/developer constraints and the user's current explicit instruction.
2. Workspace-root `AGENTS.md`.
3. The applicable frozen contract.
4. `documentation/current/AGENT_BRIEF.yaml` and the current gate projection.
5. Full `documentation/current/PROJECT_STATE.yaml` plus exact contract for scientific/external work.
6. `.agents/GOAL.md` for the current bounded objective.
7. The single task packet named by `GOAL.md`.
8. `.agents/state/decision.json` for the current worker turn.

Lower items never expand authority granted by higher items. Old handoffs and numbered records are
evidence, not reusable authorization.

## Role separation

### Sol

- Acts only as decider and reviewer.
- Uses a read-only sandbox.
- Selects exactly one next task.
- Does not edit, implement, execute, or infer missing authority.

### Luna

- Executes only the current structured decision.
- Uses read-only sandbox for `local_read_only` and workspace-write for `local_write`.
- Changes only `allowed_paths`.
- Does not choose the next task or expand scope.

## Automatically dispatchable

- `local_read_only`
- `local_write`

All other scope classes stop for the user. Prior session text cannot authorize a new turn.

## Never automatic

- HU/SSH or any remote host;
- Slurm, GPU, training, evaluation, inference, or scoring;
- model, tokenizer, corpus, benchmark, or broad dataset retrieval;
- push, publish, release, deploy, merge, or external messages;
- deletion, cleanup, reset, restore, checkout, stash, force operations, or overwrites;
- secret/credential access or environment-policy changes;
- writes to frozen artifacts, prior evidence roots, or immutable result records.

## Repository and scope guard

The workspace is one Git repository. Snapshot its HEAD and full porcelain status before and after
each worker turn. A HEAD change is never path-allowed. Preserve all pre-existing dirty and
untracked files. Unexpected paths stop the loop without automatic revert.

## Loop and context limits

- Limits come from `config.json`.
- `.agents/STOP` ends the loop before the next role turn.
- Every role reads the required live files and only task-named evidence.
- An active goal names exactly one validated Markdown packet under `.agents/task-packets/`.
- Task packets are capped by `max_task_packet_lines` and may name at most eight context files.
- One Luna turn should implement one bounded, testable task.
