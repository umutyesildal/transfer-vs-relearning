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
- M0: closed with 21/21 active lanes, 3/3 exact-prefix and 42 v1f normalized observations;
- M1: fixed OLMo/Qwen/SmolLM cohort, Relation V2 facts and eval-v2 policy;
- M1: training and eval-v2 complete at 111/111 states;
- current boundary: the three-model vngrs D0 two-phase launcher and human-review handoff are
  frozen and unexecuted; Phase 1 awaits exact SHA-bound authorization;
- D0 audit/split/tokenizer-accounting operators: locally implemented and offline validated;
- tokenizer inventory: PASS for all three M1 epoch-036 parents with zero HU writes;
- source-registry extractor: locally implemented and offline validated; exact accepted ledger has
  not been read for this step;
- first registry/storage discovery: preserved operational NOT_RUN at incompatible inode `df`
  syntax, with zero HU writes and no ledger payload returned;
- corrected inode retry: filesystem observations complete, but local command display truncated the
  ledger before extraction; zero HU writes/downloads;
- direct-pipe capture: complete ledger reached the extractor; it blocked because the historical
  Parquet compressed-byte total was incorrectly used as the full-object total;
- byte-semantics repair: PASS; 32/32 LFS identities and both exact byte aggregates are closed;
- storage/orchestration qualification: 32 GiB frozen peak, 40 GiB plus 1,024-inode fresh gate,
  exact Parquet loader, typed failures, reviewed adapters and atomic output chain passed 181
  compatible tests;
- next boundary: authorize only Phase 1, which must stop at `AWAITING_HUMAN_REVIEW`; Phase 2
  requires the resulting 64-document packet and a separate later authorization;
- vngrs: conditional systematic 32-shard M2 input; not materialized or training-ready;
- M2 execution: not authorized; external materialization requires a later frozen SHA-bound
  contract and separate explicit user authorization.

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
