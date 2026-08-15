# Orchestrator Policy

## Source hierarchy

1. The user's current explicit instruction.
2. The workspace-root `AGENTS.md`.
3. The current applicable frozen contract, gate, and `LUNA_WORKER_CURRENT_HANDOFF.md`.
4. `.agents/GOAL.md` for the current bounded objective.
5. `.agents/state/decision.json` for the current worker turn.

Lower items never expand authority granted by higher items.

## Role separation

### Sol

- Acts only as decider and reviewer.
- Uses a read-only sandbox.
- Does not implement, edit files, authorize work, or claim that missing authority exists.
- Produces exactly one structured decision.

### Luna

- Executes only the current structured decision.
- Uses read-only sandbox for `local_read_only` and workspace-write for `local_write`.
- Does not choose the next task or expand allowed paths.
- Produces exactly one structured worker report.

## Automatically dispatchable scopes

- `local_read_only`
- `local_write`

All other scope classes require the loop to stop. Prior authorization text in a persistent session
is historical context and cannot authorize a new turn.

## Never automatic

- HU/SSH or another remote host
- Slurm, GPU, training, evaluation, inference, or benchmark scoring
- model, tokenizer, corpus, or broad dataset retrieval
- push, publish, release, deploy, or sending external messages
- deletion, cleanup, reset, restore, checkout, stash, force operations, or overwrites
- credentials, secret access, or environment-policy changes
- writes to frozen artifacts, prior evidence roots, or reserved chronological documents

When any item is necessary, Sol must return `awaiting_authorization` with a precise bounded request.

## Loop limits

- Maximum rounds, rework count, repeated decisions, per-turn timeout, and wall-clock time come from
  `config.json`.
- The presence of `.agents/STOP` ends the loop before the next role turn.
- Unexpected changed paths stop the loop without attempting an automatic revert.

## Multi-repository rule

The workspace root is not a Git repository. Inspect each configured repository with `git -C` and
preserve its pre-existing dirty/untracked state. Root documentation is checked separately by file
fingerprints.

