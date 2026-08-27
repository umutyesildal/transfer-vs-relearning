# Current project status

**As of:** 2026-08-27

**Current branch:** `agent/m2-three-model-vngrs-d0`

**Execution state:** M1 eval-v2 wave v3 is terminal `complete`: 111/111 canonical scientific
states, consisting of 108 GPU snapshots and 3 M0 parent projections. Full execution history,
final result and delegation boundaries:
`documentation/records/evaluation/M1_EVAL_V2_WAVE_EXECUTION_AND_CORRECTIONS_2026-08-23.md`.
The detailed M0↔M1 result ledger is
`documentation/records/evaluation/M1_EVAL_V2_WAVE_RESULT_2026-08-27.md`.

**Current preparation boundary:** the three-model M2 scope is OLMo, Qwen and SmolLM, each with
full M2-A/M2-B sibling training from its own frozen M1 epoch-036 parent. No single primary model
is selected. The current local-only artifact is the execution-disabled vngrs D0 draft at
`documentation/contracts/corpora/vngrs-m2-three-model-d0-v1.md`, using the previously verified
systematic 32-shard subcorpus. No corpus retrieval/materialization or M2 training is authorized.
The local fail-closed full-object operator is now implemented and offline-fixture validated. It is
transport-injected, disabled by default, and cannot create the production root until the exact
32-object size/SHA-256/LFS registry closes. No real corpus byte was requested or written.
The deterministic lightweight audit, text-free 64-ID human-review selection, exact 10,000-ID
held-out split and three-tokenizer accounting schemas are also implemented locally. Tokenizer
assets remain unbound/unloaded, so these are validated operators rather than corpus results.

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

`vngrs-ai/vngrs-web-corpus` is reserved for the later M2-A/M2-B Turkish adaptation arms. It is not
an M1 training input. `trwiki-20260601` remains the Turkish cross-domain control.

## Current safety boundary

The completed M1 family is terminal evidence. No duplicate submission, cleanup, deletion,
M2-A/M2-B execution, or primary-model promotion is implied. The active local boundary is to
qualify the three-model vngrs D0 contract and offline operator. External materialization remains a
separate exact authorization boundary.

## Read next

- agent entry: [`START_HERE.md`](START_HERE.md)
- small machine projection: [`AGENT_BRIEF.yaml`](AGENT_BRIEF.yaml)
- ordered work: [`ROADMAP.md`](ROADMAP.md)
- measurement contract: [`../contracts/evaluation/eval-v2.md`](../contracts/evaluation/eval-v2.md)
- pipeline interface: [`../pipeline/README.md`](../pipeline/README.md)

Historical numbered documents and the earlier M0 failure/recovery records remain preserved. They
are evidence, not the default source of current status.
