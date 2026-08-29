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
- current boundary: V1A/V1B/V1C remain preserved operational NOT-RUN evidence; D0 v2 job `481838`
  preserved its exact first-object partial; D0 v3 job `481844` then materialized and byte-verified
  all 32 objects / 9,502,315,428 bytes, but stopped fail-closed at the mandatory lightweight audit;
  its generic failure did not preserve the exact contamination/encoding trigger, no split or
  64-document review packet was created, and the V3 root is now immutable/read-only evidence;
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
  exact Parquet loader, typed failures, reviewed adapters and atomic output chain passed 191
  compatible tests;
- first OSCAR audit-recovery job `481863`: exact label inventory PASS; observed lowercase `oscar`
  has 354,482 documents / 1,553,923,133 UTF-8 bytes, while `mc4` has 5,317,204 documents; V1
  stopped before audit because its candidate was uppercase `OSCAR`;
- lowercase V1a job `481886` completed the 354,482-document OSCAR audit, but its flattened
  600-surface gate blocked on 439,906 exact / 935,276 normalized document-pattern pairs; bounded
  examples are object-only, so isolated ordinary cities/professions/industries cannot support a
  factual-contamination verdict by themselves;
- fact-pair job `481904` completed PASS over all 354,482 exact OSCAR documents: subject-only,
  exact/normalized paired-fact and invalid-encoding counts are all zero; the prior atom hits are
  therefore object/answer-only diagnostics, and all three terminal artifacts are hash-closed;
- split/review job `481906` completed: the exact 344,482 train / 10,000 held-out split is valid and
  frozen, but all 64 review rows were labelled `oscar|q0`; because q1--q3 population counts were
  not persisted, the packet is provisional for verdict entry. One excerpt also contains literal
  U+0085, exposing a `splitlines()` reader bug; the JSONL remains valid and the LF-only reader fix
  is regression-tested;
- the review-coverage repair was limited to measuring q0--q3 and producing the authoritative
  pre-verdict 64-packet with a one-per-nonempty-stratum floor; it did not rewrite the split, enter
  verdicts, access tokenizers/models, open Phase 2 or train;
- review-coverage job `481908` completed PASS: all 354,482 OSCAR documents genuinely belong to q0
  and q1--q3 are empty, so q0-only sampling is valid. The new authoritative 64-packet is bound to
  semantic SHA `73329e45...`;
- human review is complete and packet-bound: 64/64 unique documents were marked `usable`, with
  zero `unusable` or `unsafe`; the exact decision ledger is tracked and hash-closed;
- Phase 2 has a local unexecuted plan in Document 187: revalidate population/split/decisions, load
  only the exact OLMo/Qwen/SmolLM tokenizer assets, and produce train/held-out token accounting.
  Operator/config/launcher/contract are not implemented or frozen yet; no tokenizer/model/HU job,
  Phase 2 execution or training is authorized;
- M2 primary source direction: cleaned OSCAR-2201-derived rows within vngrs, pending exact label,
  volume and quality qualification; mC4 is excluded from main training and preserved;
- vngrs: the reservoir is materialized, the OSCAR fact-pair gate passed and the split is frozen;
  review coverage, human verdicts and later gates remain incomplete, so it is not training-ready;
- M2 execution: not authorized; the diagnostic recovery, later selection and all training stages
  each require their own exact contract boundary and explicit user authorization.

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
