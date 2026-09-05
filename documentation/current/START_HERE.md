# Start here — agent context boundary

Read only this small sequence before acting:

1. root `AGENTS.md` for stable rules;
2. `AGENT_BRIEF.yaml` for the current phase, gates and next boundary;
3. the user's current instruction or exactly one bounded task packet;
4. only the contract, code, tests and evidence named by that task.

Do not recursively read `documentation/`. Do not start from the numbered documents, old handoffs,
the master synthesis, the long timeline, or a previous chat transcript.

## Current scientific boundary

- **2026-09-05 terminal override:** the M2 OSCAR evaluation family is complete at 63/63 with zero
  missing/failed tasks. The executed bootstrap collapsed repeated prompt variants by `fact_id`;
  its rows are preserved but superseded by the tested `probe_id` correction, now canonically
  published by CPU-only job `484357` with unchanged source inputs and no model/inference. No model
  passes every frozen primary gate. Read
  `documentation/records/evaluation/M2_EVAL_RECOVERY_V1A_TERMINAL_RESULT_2026-09-05.md` for the
  scientific result and
  `documentation/records/evaluation/M2_EVAL_BOOTSTRAP_CORRECTION_EXECUTION_RESULT_2026-09-05.md`
  for the correction audit. No GPU/evaluation rerun is needed or authorized.

- **Current reporting plan:** extend the existing dependency-free `tools/m0-dashboard/` site with
  the compact M0/M1/M2 result layers, corrected contrast intervals, trajectories, diagnostic
  breakdowns and thesis exports. The implementation-ready boundary is recorded in
  `documentation/records/evaluation/M2_RESULTS_WEBSITE_AND_THESIS_REPORTING_PLAN_2026-09-05.md`;
  it requires no HU, GPU, model load or new evaluation.

- **Reporting implementation:** the validated multi-stage web-data layer, five-view bilingual
  dashboard and deterministic thesis CSV/Markdown/SVG exports are locally complete. Read
  `documentation/records/evaluation/M2_RESULTS_WEBSITE_AND_THESIS_PACKAGE_IMPLEMENTATION_RESULT_2026-09-05.md`.

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
- Phase 2 V1 was locally implemented, fixture-validated and frozen as a CPU-only evidence
  contract: revalidate population/split/decisions, load only the exact
  OLMo/Qwen/SmolLM tokenizer assets, and produce six train/held-out token-accounting reports.
  Its contract/config/operator/runner/submitter remain preserved;
- authorized V1 job `481910` subsequently stopped fail-closed before tokenizer accounting because
  the historical inventory recorded the first hexadecimal character of OLMo `tokenizer.json`
  SHA as `b` while both the exact asset and frozen snapshot manifest record `c`; the other five
  assets matched. V1 root and inventory remain preserved, no model weight/GPU/training ran;
- authorized V1A CPU job `481980` completed PASS under the fresh retry root. The corrected
  inventory and mandatory snapshot-manifest cross-check passed for OLMo/Qwen/SmolLM; all three
  tokenizer compatibility reports and all six train/held-out accounting reports are hash-closed,
  with zero tokenizer exceptions and zero zero-token documents. No model weights or GPU were
  accessed and no tokenized corpus was persisted;
- M2 primary source: cleaned OSCAR-2201-derived rows within vngrs; the exact 344,482 train / 10,000
  held-out split, 64/64 usable human review and three-model tokenizer accounting are complete. mC4
  is excluded from main training and preserved;
- vngrs: Phase-2 evidence is `D0_EVIDENCE_COMPLETE`, but `ready_to_train=false` because the matched
  M2-A/M2-B execution contract is not yet frozen;
- M2 design: Document 191 freezes a non-executable three-model plan at 49,938,432 model-native
  tokens per arm, 762 updates, 512-token blocks, approximately 1% Branch-B factual replacement,
  dense evaluation every approximately 10% dose and full eval-v2 at entry/midpoint/endpoint;
- M2 exact block execution: Document 192 and contract
  `vngrs-m2-oscar-exact-block-materialization-v1` froze the tested CPU-only operator. Its one
  authorized wave was consumed by job `481990`: the 250-row fact registry was written, but zero
  OLMo/Qwen/SmolLM block files and no terminal manifest were published. Because Slurm accounting
  was unavailable and job logs were routed to `/dev/null`, the exact operational trigger remains
  unresolved. Document 195 is the terminal partial result; the partial root is read-only,
  `ready_to_train=false`, and no retry is authorized;
- M2 exact block recovery preparation: Document 196 freezes a fresh-root, CPU-only recovery with
  early non-OSCAR memory release, streaming sibling-arm writers proven equivalent to the frozen
  algorithm, persistent progress/exception/Slurm/resource evidence and 20 passing tests. Contract
  SHA is `d49a221a7b1f8b02682330b4d46762cc57140023a5426f0f5ad77b4d10f8e0d9`; it is unexecuted and
  needs separate exact user authorization;
- M2 recovery queue/relocation: Document 197 froze a pending-only relocation to 4 CPU after 03:00
  Europe/Berlin, but job `482007` started and terminalized before that decision. Its contract SHA
  is `29b95dedc826c43e833d4332fe2a8756907436fe1f2a3981d5daf602ddf35413`; the relocation remains
  unexecuted and is now ineligible;
- M2 recovery terminal result: job `482007` started before the relocation decision and stopped
  fail-closed at OLMo `stream_train_blocks` because `FrozenTokenizerAdapter` has no direct
  `eos_token_id` property. Persistent evidence records exit 1, zero block files, no manifest and
  max RSS 32,807,744 KiB (~31.29 GiB), excluding OOM. Document 198 is authoritative; the pending-
  only 4-CPU relocation is now ineligible and no retry is authorized;
- M2 adapter repair: Document 199 freezes the narrow nested-`eos_token_id` compatibility repair,
  a fresh root and one 4 CPU / 64G / 6h CPU-only route. The compatible suite passes 12/12. Contract
  SHA is `711deae9853287f9eeea62f35cc397a27a9c3ae3c3f8bbf2f65a8637d647508f`; it is unexecuted and
  requires new exact SHA-bound authorization;
- M2 exact-block terminal result: the authorized adapter repair completed as job `482027` with
  exit 0. All OLMo/Qwen/SmolLM M2-A, M2-B and shared-validation artifacts passed exact audits;
  manifest SHA is `68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63`.
  Document 200 is the result authority. The 21-file root is preserved; training remains unopened
  and `ready_to_train=false` until a separately frozen M2 training/measurement contract exists;
- M2 training-readiness evidence: Document 201 freezes one CPU-only fresh-root wave that validates
  all epoch-036 parent model-file hashes, creates/validates six execution-disabled configs,
  computes conservative storage and produces an all-250-fact HTML review handoff. Contract SHA is
  `071252e2c1477f4fbc5e7d132a2bc0f418f2e51ee57120641f7de57bbcec1168`; it is unexecuted and
  does not authorize GPU, optimizer smoke, training or evaluation;
- M2 readiness v1 result/repair: authorized job `482035` stopped fail-closed before evidence
  publication because the reader expected weight hashes in the compact model manifest rather than
  its exact linked snapshot manifest. Document 202 preserves the five-file terminal root and
  Document 203 freezes the v1a repair. The authorized v1a job `482040` then completed PASS:
  all three epoch-036 parent asset sets, six M2-A/M2-B configs and storage evidence passed. Document
  204 is the current result/gate authority; its terminal state remains
  `EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE`, `ready_to_train=false`;
- M2 review/smoke preparation: Document 205 adds an exact 250-fact human-decision validator and a
  smoke-only three-model A100 route that cannot submit training or finalization jobs. The local
  combined suite passes 16/16. It remains non-executable until the user exports all 250 verdicts,
  the validator returns `M2_FACT_REVIEW_PASS`, and a separate SHA-bound smoke contract is frozen
  and authorized;
- M2 fact-translation correction: the user's 250-row review found seven issues. Four exact
  translations were corrected and three valid Turkish terms were accepted unchanged. Corrected
  registry SHA is `46a1071d228758013d73fae4ab3925538523eb338001e00bde9d5fe178f1c4a2`;
  the corrected ledger passes `250/250 usable`. Document 206 and contract
  `vngrs-m2-oscar-fact-translation-repair-v1` froze a CPU-only fresh-root repair that rewrites
  only the three M2-B block files from immutable M2-A blocks. Its authorized launcher stopped at
  `sbatch --test-only` because HU has no `cpu` partition; no real job was submitted and the first
  root contains only the preserved 110-byte submission-state file. Document 207 records this
  fail-closed result. The authorized v1a route corrected the partition and submitted real job
  `482057`, but `conda run` created a runtime file under the root-bound `tmp/` before Python, so
  the strict precreated-root validator stopped before tokenizer/source/block work. Document 208
  preserves the four-file, zero-block root. V1b allowed only runtime-owned `tmp/` files and used
  a fresh retry-v2 root. Authorized job `482066` completed PASS: all three corrected M2-B files
  contain 97,536 blocks, the terminal manifest SHA is
  `96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486`, predecessor M2-A and
  validation remained read-only, and no GPU/model/training access occurred. Document 209 is the
  current result/gate authority;
- M2 corrected optimizer smoke: Document 210 froze a corrected-family-bound, smoke-only
  `0-2%1` A100 array for OLMo/Qwen/SmolLM. Each role performs one BF16 effective-batch AdamW step
  from M2-A only after exact corrected M2-A/M2-B artifact verification; no checkpoint or training
  job can be submitted. Its authorized array `482103` completed three `OPTIMIZER_SMOKE_PASS`
  reports on A100-80GB with finite losses/gradient norms, BF16 parameters/gradients/optimizer
  moments, one optimizer step per role, zero checkpoints and `scientific_training=false`.
  Document 211 is the terminal result authority. At that gate the smoke was closed but M2 training
  remained unauthorized pending a new exact training/measurement contract;
- M2 scientific training freeze: Document 212 and contract
  `vngrs-m2-oscar-scientific-training-v1` now freeze the exact six-run OLMo/Qwen/SmolLM ×
  M2-A/M2-B wave. Corrected M2-B configs are regenerated only in a fresh CPU preflight; three
  immutable smoke PASS reports, live 386,596,220,128-byte/8,192-inode storage gates and one
  `0-5%3` A100-80GB array are mandatory. Ten checkpoints per run and the 63-state measurement
  matrix are precommitted. Contract SHA is
  `748e2aae5c7e3ec95acaf639e4536e6024686e5a854ad09dc6013feb47490222`; it is unexecuted and
  needs exact user authorization. Scoring/evaluation remains separately gated;
- M2 scientific training v1 result: the authorized CPU preflight `482206` completed PASS, but all
  six array tasks `482207_[0-5]` stopped in 3–4 seconds before model load because every gruenau10
  A100 carried at least one foreign compute process; GPU1 also missed the 61,440 MiB free-VRAM
  gate. No training run, optimizer update, checkpoint, binding or evaluation matrix exists.
  Finalizer `482208` is dependency-never-satisfied and was not cancelled. Document 213 is the
  terminal operational `NOT_RUN` authority; the single-wave authorization is consumed and no
  retry/fallback is authorized;
- M2 scientific training recovery: Document 214 and frozen contract
  `vngrs-m2-oscar-scientific-training-recovery-v1` preserve the full v1 scientific recipe while
  replacing only the shared-node launch guard. Each serial task requests all three A100-80GB GPUs,
  atomically records their VRAM/process ledger and trains on the deterministic safest single GPU
  only if `free >= 61,440 MiB` and `used <= 20,480 MiB`. Task failure audit is persistent and the
  old root remains read-only. Contract SHA is
  `c6f07cdc69003406d2ea44d8bb2c71b9c89ffd4694e224fd708460fb7374da13`; it is frozen/unexecuted
  and needs exact user authorization plus publication commit. Evaluation/scoring and automatic
  retry remain unauthorized;
- M2 recovery submission/preflight: the exact recovery contract was authorized and commit
  `a8978b1` was ordinary-pushed/preservation-checked fast-forwarded on HU. HU M2 tests passed
  `60/60`; preflight `482224` completed `M2_SCIENTIFIC_TRAINING_PREFLIGHT_PASS`. The one serial
  array `482225_[0-5%1]` is currently `PENDING(Resources)` with a non-guaranteed scheduler estimate
  of 2026-09-06 13:16; finalizer `482226` is dependency-pending. Old never-started finalizer
  `482208` was conditionally cancelled after exact checks. Document 215 is the current operational
  progress authority; no scientific training has started and duplicate/fallback/retry is forbidden;
- M2 one-GPU relocation preparation: read-only Slurm evidence showed both A100 nodes have exactly
  one Slurm-free GPU, explaining the 5-day three-GPU co-allocation estimate. Document 216 freezes
  a science-identical gruenau10-bound `gpu:a10080gb:1`, serial `0-5%1`, fresh-root relocation with
  persistent selector/task audit. Contract SHA is
  `ffea82ac9f9d0bbd9228c13cff7eec9d87c16fd381b92ab35021345413c83792`; it is unexecuted and
  requires exact authorization before pending jobs `482225/482226` may be cancelled;
- M2 one-GPU relocation execution: the exact contract was authorized, old never-started jobs
  `482225/482226` were verified/cancelled, and HU was fast-forwarded to `c15c123`. HU M2 tests
  passed `62/62`; preflight `482231` passed and serial array `482232` completed all six OLMo/Qwen/
  SmolLM × M2-A/M2-B tasks. All six manifests are `complete`, all task audits PASS and all 60
  checkpoints exist. CPU finalizer `482233` then failed only because trainer-recorded checkpoint
  paths are lexicographically rather than numerically ordered; exact ten-path membership passed
  read-only verification for every run. Document 218 is the current completion/failure authority;
- M2 finalizer order repair: frozen contract
  `vngrs-m2-oscar-finalizer-numeric-order-repair-v1` permits only an exact-membership-then-numeric-
  order normalization and one fresh-root 4-CPU binding/matrix finalizer. Contract SHA is
  `c30efe60dc76e2701434c0f87ba2cb269d8deeda1ccd3f6f84b7c5194b17054e`. Authorized job `483682`
  completed PASS: family binding is 6/6 runs and 60/60 checkpoints; prepared matrix contains 60
  dense tasks, 12 full tasks and 63 unique states with `evaluation_authorized=false`. Final audit
  SHA is `f3360545...`; Document 219 is the result/gate authority. GPU, training, evaluation/
  scoring, cleanup and automatic retry remain forbidden;
- M2 remaining preparation after a separately authorized successful recovery: bounded Turkish
  fact-registry review, exact epoch-036 parent weight/config hashes, memory decomposition/optimizer
  smoke, storage/runtime estimate and tested training/evaluation DAG;
- M2 local training preparation: Document 193 implements a six-config generator/validator, exact
  non-uniform checkpoint callback for updates 76..762 and an authorization-gated three-model
  optimizer-smoke → six-run training DAG fixture. It is non-executable; evaluation adapters and a
  final training contract remain open;
- M2 local output/evaluation preparation: Document 194 adds the exact 60-checkpoint model-only
  finalizer and a 60-dense/12-full/3-projected-parent eval-v2 matrix. The M2 runtime evaluation
  adapter is intentionally unregistered, so inference/scoring remains impossible and unauthorized;
- M2 scientific training and model-only binding: complete for all six sibling-arm runs and all 60
  checkpoints. The active boundary is local eval-v2 execution-adapter/contract preparation;
  evaluation/scoring remains separately frozen and authorized future work.

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
