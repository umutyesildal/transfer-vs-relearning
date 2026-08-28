# Current project status

**As of:** 2026-08-28

**Current branch:** `agent/m2-three-model-vngrs-d0`

**Execution state:** M1 eval-v2 wave v3 is terminal `complete`: 111/111 canonical scientific
states, consisting of 108 GPU snapshots and 3 M0 parent projections. Full execution history,
final result and delegation boundaries:
`documentation/records/evaluation/M1_EVAL_V2_WAVE_EXECUTION_AND_CORRECTIONS_2026-08-23.md`.
The detailed M0↔M1 result ledger is
`documentation/records/evaluation/M1_EVAL_V2_WAVE_RESULT_2026-08-27.md`.

**Current preparation boundary:** the three-model M2 scope is OLMo, Qwen and SmolLM, each with
full M2-A/M2-B sibling training from its own frozen M1 epoch-036 parent. No single primary model
is selected. The active corpus artifact is the frozen vngrs D0 v3 contract at
`documentation/contracts/corpora/vngrs-m2-three-model-d0-v3.md`, using the previously verified
systematic 32-shard subcorpus. Its single authorized job `481844` has materialized all 32 objects /
9,502,315,428 bytes, then stopped fail-closed because the mandatory lightweight audit returned
`BLOCKED`. The V3 implementation persisted only the generic exception, not the exact
contamination/encoding reason. It created no split or review packet. No retry or M2 training is
authorized. D0 v2 job `481838` requested one real corpus object and preserved its 448,718,347-byte
partial after a fail-closed identity-semantic mismatch; no object was published. V3 keeps the
accepted transport object ID distinct from full-byte SHA-256, computes byte SHA only from received
bytes, atomically freezes those hashes, and revalidates them before Parquet row loading.
The deterministic lightweight audit, text-free 64-ID human-review selection, exact 10,000-ID
held-out split and three-tokenizer accounting schemas are also implemented locally. These remain
validated operators rather than corpus results.
The exact six-file read-only inspection is frozen separately in
`documentation/contracts/corpora/vngrs-m2-d0-tokenizer-manifest-inventory-v1.md`; execution is
complete and consumed. All six expected hashes matched; 5,988 compact manifest bytes were read,
HU writes were zero, and the OLMo/Qwen/SmolLM tokenizer asset registries all closed. D0 remained
unqualified at that historical checkpoint; the later registry/storage closure supersedes that
narrow status without rewriting the earlier evidence.
A fail-closed local extractor for those 32 identities is now offline tested. The exact one-ledger
plus filesystem-metadata read-only discovery contract is frozen at
`documentation/contracts/corpora/vngrs-m2-d0-source-registry-storage-discovery-v1.md`; it is
consumed and stopped fail-closed at the HU-incompatible `df -i --output` combination before inode
output or ledger payload return. Ledger size/SHA, proposed-root absence and byte capacity passed;
HU writes and downloads were zero. The source registry therefore remains open. A narrow frozen,
unexecuted retry changes only the inode observation to `df -Pi` at
`documentation/contracts/corpora/vngrs-m2-d0-source-registry-storage-discovery-retry-v1.md` and
requires new exact SHA-bound user authorization. That corrected pass subsequently completed inode
and byte observations but the generic Codex output display truncated the compressed ledger before
local extraction. Its preserved result has zero HU writes/downloads and a still-open registry. A
final narrow correction pipes stdout directly into the committed fail-closed parser without
persisting the transcript or raw ledger. It is frozen at
`documentation/contracts/corpora/vngrs-m2-d0-source-registry-capture-retry-v1.md` and remains
unexecuted pending new exact SHA-bound authorization.
The authorized direct-pipe pass then delivered the full ledger and exposed a genuine evidence
semantic mismatch: `9,468,474,036` is the Parquet row-group compressed-byte aggregate, while the
32 downloadable objects total `9,502,315,428` bytes. The registry rejected the conflation. The
operator and D0 draft now gate both totals separately; the frozen byte-semantics repair contract
`documentation/contracts/corpora/vngrs-m2-d0-source-registry-byte-semantics-repair-v1.md` is
unexecuted and needs new exact SHA-bound authorization.
The authorized byte-semantics repair subsequently completed PASS: 32/32 immutable LFS-derived
full-object identities closed, full-object bytes are `9,502,315,428`, Parquet compressed bytes are
`9,468,474,036`, and canonical registry SHA-256 is
`b1c80bf78ff40de5c02e14f08082a51cc17cc90a9853028eaf866cb63326e41f`.
HU writes, corpus reads and downloads remained zero. Storage arithmetic is now closed at a
`30,029,406,455`-byte calculated peak, rounded to a frozen 32 GiB peak with mandatory fresh
40 GiB/1,024-inode execution gates. The exact Parquet loader, stage orchestration, typed
post-materialization failures and atomic self-reference-free evidence chain passed the compatible
then-current 168-test suite. The later two-phase freeze extends that qualified checkpoint. The
production HU preflight, reviewed HTTPS/tokenizer adapters and explicit two-phase 64-document
human-review handoff are frozen. The pre-correction branch was pushed and HU tests passed 45/45,
but submission was stopped before any Slurm job when the launcher was found to write preflight/log
files outside the sole allowed root. No corpus request or output root occurred. Corrected V1A
kept preflight in memory and suppressed filesystem Slurm logs; HU targeted tests passed 46/46.
Its single job `481608` ran for `00:02:10` and stopped before output-root creation or network access
when the exact HU-home `du` exceeded its 120-second timeout. This is operational `NOT_RUN`
evidence, and the V1A authorization is consumed. V1B changed only that timeout to 300 seconds and
added bounded best-effort Slurm-comment status evidence. Its single job `481711` started on
`gruenau4` but stopped before root creation or network access; after controller purge the comment
was unavailable and broken `sacct` could not recover the exact exception. V1B is operational
`NOT_RUN` and its authorization is consumed. V1C job `481836` then durably recorded
`accepted read-only evidence closure drift` with zero network/object writes. Read-only diagnosis
proved the root itself unchanged at 104 files / 18,025,945 bytes: exact historical
`relative_path size\n` serialization reproduces `120cdd7b...`, while the V1 validator's canonical
JSON produced `268ebe81...`. The V1C root is preserved. D0 v2 corrected that serialization and its
authorized job `481838` downloaded the first object to the v2 partial namespace. Its exact size,
Parquet magic, accepted footer and accepted trailer all passed, but the old validator incorrectly
required the byte SHA `d72ae7…` to equal the LFS/Xet object ID `a81097…`. V2 stopped with zero
published objects and is preserved read-only. Frozen D0 v3 repaired only this semantic on a fresh
root. Its authorized job `481844` produced a verified 32-row materialization manifest with
SHA-256 `bb413e9a…`, then terminated at the audit gate with failure SHA-256 `a341e478…`.
Document 181 is the append-only result record. The frozen, unexecuted
`vngrs-m2-oscar-audit-recovery-v1` contract reads those bytes in place, tests exact
`corpus == "OSCAR"`, and persists exact label counts plus bounded audit reasons before stopping.
It creates no split/review packet and requires separate exact SHA authorization.

The prospective primary M2 training source is now the cleaned OSCAR-2201-derived subset within
the preserved vngrs release. mC4-derived rows are excluded from the main M2 training population
and remain preserved. This is an accepted direction, not a frozen filtered release: after the
recovery evidence closes, a new contract must bind the verified OSCAR label/predicate, volume,
contamination disposition,
10,000-document split, 64-document human-review packet and three-model tokenizer accounting.
The decision record is
`documentation/decisions/M2_OSCAR_ONLY_PRIMARY_TURKISH_CORPUS_DECISION_2026-08-28.md`.

## The short answer

M0 is finished. The matched three-model M1 training wave and its eval-v2 checkpoint family are
complete: `/vol/tmp2/yesildau/m1_matched_three_model_retry_v1` produced 37 tracked states per
model, and `/vol/tmp2/yesildau/m1_eval_v2_matched_three_model_v3` closed at 111/111. The M1
eval-v2 contract is hash-closed and the derived result layer is recorded with denominators and
source hashes.

The earlier stalls were control-plane/validator issues, not scientific scores. Their correction
history remains append-only in the execution record. The final sweep preserved the one hard-killed
Qwen attempt as `__killed_0`, then produced a complete canonical result without overwriting prior
evidence.

## Historical local pre-execution audit (2026-08-23)

- Hash chain re-verified after commit `a273f56`: contract, execution config, adapter module and
  entrypoint hashes on disk match `PROJECT_STATE.yaml` exactly (18/18 checks).
- Runner-schema parity confirmed: exact-prefix config keys, generation-integrity config keys,
  Turkish-perplexity CLI flags and harness flags (`--seed 42,42,42,42`, `dtype=float16`,
  no `--include_path`) match the proven M0 adapter behavior; `winogender_*`/`turblimp_core`
  resolve inside the pinned environment as in M0.
- Tests: focused executor suite 6/6; combined study + experiment-pipeline suites 82 passed.
- At that historical point, the remaining blocker was the exact SHA-bound user authorization
  sentence; the later authorized sweep and its terminal result are recorded above.

## Revision 2 — dual-route acceleration (2026-08-23, later the same day)

The Correction-1 single-A100-array wave (preflight 475878 complete; array 475879; finalizer
475880) was cancelled by explicit user decision roughly fifteen minutes after its first three
tasks started; zero scientific results were written. Contract Correction 2 and frozen config
`m1_eval_v2_matched_three_model_v2.yaml` now authorize a dual-route topology: a 72-task
`gpu:a6000:1` array (qwen+smollm, throttle 8) plus a 36-task `gpu:a10080gb:1` array (olmo,
throttle 3), one preflight and one afterany finalizer. Every task passes a fail-closed 20 GiB
free-memory gate before scoring. V100, RTX6000 and RTX3090 remain forbidden. The preserved
v1 output root keeps the cancelled attempt read-only; the fresh v2 root is required by contract.
Expected wall time drops from roughly 25–35 hours to roughly 8–12 hours.

## Revision 3 — single A100 pool (2026-08-23, final)

The dual-route wave hit an external non-Slurm process occupying most RTX A6000 GPUs (~45 GiB);
the frozen 20 GiB gate correctly refused 68 tasks before scoring, zero scientific results were
written, and the user cancelled the wave choosing the solid path. Correction 3 freezes a single
`gpu:a10080gb:1` array over all 108 tasks (throttle 6 across both A100 nodes), a bounded
in-task gate schedule (13 probes, 600 s apart), and fresh root `..._v3`. Both preserved roots
(`_v1`, `_v2`) keep the cancelled attempts read-only.

## Closed M0 boundary

- active protocol: frozen `eval-v2`;
- Pile-10k: retired prospectively and absent from every active lane, gate and denominator;
- OLMo, Qwen and SmolLM: 21/21 active non-Pile M0 lanes available;
- exact-prefix: complete for all three models, 500 probes per model;
- source projection: 24/24 hash-verified references in v1b;
- canonical normalization: complete in v1f with 42 metric observations;
- rescoring or another M0 recovery: not required.

The v1b projection itself contains references rather than metric rows. The canonical observations
were written later by the separately authorized v1f normalizer. Both statements are true and no
longer treated as contradictory.

## Fixed M1 scientific design

M1 is a fresh matched comparison across exactly OLMo-2-0425-1B, Qwen2.5-1.5B and SmolLM2-1.7B at
their frozen M0 revisions.

All three use the same tracked Relation V2 release: 100 subjects, 500 facts, 3,500 training rows,
seed 42, 36 epochs, 252 updates and effective batch 500. Model-specific microbatch/accumulation
decompositions are allowed only where the effective recipe remains identical.

Every run must save the parent plus every epoch-end model state, producing 37 states per model and
111 states in total. The trace records loss, learning rate, gradient norm, token counts, fact
exposures, optimizer/update counts, storage checks, hyperparameters and immutable snapshot hashes.
This is the source for Max's fact-access/retention-over-epochs table.

## Fixed M1 evaluation policy

M1 inherits the active M0 `eval-v2` protocol. Exact-prefix is mandatory rather than optional.
Dense evaluation at parent and every epoch includes factual access, 500-probe exact-prefix,
WikiText English retention, Turkish retention control and cheap generation-integrity signals.
Full evaluation at entry, midpoint and endpoint adds the full factual suite, BLiMP, HellaSwag,
WinoGender, TurBLiMP and the full integrity panel.

```text
three identity/storage preflights
  → three independent M1 trainings with epoch traces
  → hash-close training/checkpoint manifests
  → checkpoint evaluations
  → canonical normalization
  → trajectory and presentation bundle
```

## Readiness is stage-specific

| Gate | Current state |
|---|---|
| M0 | complete |
| M1 scientific inputs/recipe | ready locally |
| M1 first training wave | preserved NOT_RUN: import-path failure before model load, jobs 475832–475834 |
| M1 training retry wave | COMPLETE: jobs 475850–475852, 111 checkpoint states under `m1_matched_three_model_retry_v1` |
| M1 checkpoint evaluation adapter/contract | frozen v3; 108 GPU tasks + 3 parent projections from canonical M0 v1f evidence |
| M1 execution | COMPLETE: final sweep jobs 479444/479445/479446; 111/111 terminal |
| M2 corpus and sibling contract | not frozen; does not block M1 preparation |

The cleaned OSCAR-2201-derived rows within `vngrs-ai/vngrs-web-corpus` are the prospective primary
M2-A/M2-B adaptation source. mC4 rows remain preserved but training-excluded. This is not an M1
input. `trwiki-20260601` remains the Turkish cross-domain control.

## Current safety boundary

The completed M1 family is terminal evidence. No duplicate submission, cleanup, deletion,
M2-A/M2-B execution, or primary-model promotion is implied. The active boundary is to verify the
single running D0 v3 Phase-1 wave at terminal state and then freeze a separate OSCAR-only selection
contract. Phase 2, another D0 wave and every M2 training action remain separate future authority
boundaries.

## Read next

- agent entry: [`START_HERE.md`](START_HERE.md)
- small machine projection: [`AGENT_BRIEF.yaml`](AGENT_BRIEF.yaml)
- ordered work: [`ROADMAP.md`](ROADMAP.md)
- measurement contract: [`../contracts/evaluation/eval-v2.md`](../contracts/evaluation/eval-v2.md)
- pipeline interface: [`../pipeline/README.md`](../pipeline/README.md)

Historical numbered documents and the earlier M0 failure/recovery records remain preserved. They
are evidence, not the default source of current status.
