# Start here — agent context boundary

Read only this small sequence before acting:

1. root `AGENTS.md` for stable rules;
2. `AGENT_BRIEF.yaml` for the current phase, gates and next boundary;
3. the user's current instruction or exactly one bounded task packet;
4. only the contract, code, tests and evidence named by that task.

Do not recursively read `documentation/`. Do not start from the numbered documents, old handoffs,
the master synthesis, the long timeline, or a previous chat transcript.

## Current scientific boundary

- active evaluation protocol: eval-v2;
- Pile-10k: retired from canonical evaluation;
- M0: 21/21 non-Pile lanes available plus completed exact-prefix evidence;
- M0 projector: implemented and tested; read-only source-binding discovery passed 24/24;
- v1b SHA-bound reference projection: complete with 24 source rows and zero metric rows;
- metric normalization operator: v1a/v1b audits fail-closed on source-schema details; v1c path-aware adapter is fixture-validated;
- next boundary: separately authorize one read-only M0 metric-source audit v1c;
- M1/M2 training: not ready and not authorized.

## When to open larger files

| Need | Add exactly |
|---|---|
| Scientific interpretation | `STATUS.md` and the cited result record |
| Authority or external execution | full `PROJECT_STATE.yaml`, `AUTHORITY.md`, exact contract |
| Evaluation implementation | `eval-v2.md`, `eval_v2_registry.yaml`, named tests/code |
| Historical investigation | only the numbered chain cited by current state/evidence |
| HU/Slurm | exact authorized contract plus `ssh-client/README.md` |

The machine-readable routing policy is `READING_PROFILE.yaml`. Retirement means “not a default
read”; it never means deletion or permission to ignore cited evidence.
