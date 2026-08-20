# M0 Three-Model Seven-Lane Exclusive-A100 Recovery Contract v1

Date: 2026-08-20  
Status: `FROZEN / UNEXECUTED / EXACT AUTHORIZATION REQUIRED`

## 1. Purpose

Complete only the seven missing scientific M0 lanes while preserving the 17 valid source lanes.
This contract is an operational isolation repair for the terminal NOT-RUN result recorded in
`documentation/records/evaluation/M0_SEVEN_LANE_RECOVERY_EXECUTION_2026-08-20.md`. It does not
change eval-v1, model identity, tokenizer, precision, seeds, prompts, datasets, metric semantics,
batch behavior or any scientific pass/fail threshold.

## 2. Frozen evidence

- original source root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1`;
- original source family bundle SHA-256:
  `75fcd7cf1e388eb5a4e883264c6aa14db83797b2e7832a4bbc8e40bb38865db1`;
- retained complete lanes: `17`;
- missing lanes: `7`;
- first recovery root, now immutable:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_v1`;
- first recovery composite SHA-256:
  `a714ce0dc891641ab0c6f99a3366d941ba2b3f8f3e2b0d4db8b28f4e90125f06`;
- first wave scientific scores: `0`;
- first wave terminal class: all seven stopped before model load/scoring at the frozen free-memory
  guard.

The first wave showed why a scheduler-level single-GPU request is insufficient on HU. Slurm
selected GPU0 on `gruenau10`, which had only `39,630,471,168` free bytes, while a read-only
three-device audit immediately afterward showed GPU1 with approximately 78.7 GiB free. The repair
must therefore bind and audit the complete three-device A100 node allocation before selecting a
UUID.

## 3. Immutable scientific targets

The exact target order is:

1. OLMo English capability;
2. OLMo Turkish capability;
3. OLMo Turkish perplexity;
4. Qwen Pile-10k English retention;
5. Qwen Turkish capability;
6. Qwen Turkish perplexity;
7. SmolLM English capability.

The six non-Pile lanes keep their exact `30,064,771,072`-byte free-memory minimum. Qwen Pile-10k
keeps its exact `68,719,476,736`-byte minimum. No threshold is lowered.

## 4. Fresh namespace

The only writable scientific root is:

`/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_isolation_v1`

HU home, the original M0 family root, the first recovery root, model roots and dataset caches are
read-only. The fresh root must be absent at preflight. No cleanup or namespace reuse is permitted.

## 5. Exclusive allocation and UUID selection

The GPU controller requests exactly:

- node: `gruenau10`;
- partition: `gpu`;
- GRES: `gpu:a10080gb:3`;
- node allocation: `--exclusive`;
- visible device count: exactly `3`;
- GPU name: exactly `NVIDIA A100 80GB PCIe`;
- minimum physical total per device: `85,899,345,920` bytes.

Before every lane, the controller records all three UUID/name/total/free rows, filters by the
unchanged lane-specific free-memory gate and selects deterministically by maximum free bytes then
UUID. If no eligible device exists, it polls every 60 seconds for at most 7,200 seconds. It does
not load a model while waiting and never intervenes in foreign processes. Timeout is a terminal
NOT-RUN result, not permission to lower the gate or resubmit.

Each lane runs in a fresh child process with `CUDA_VISIBLE_DEVICES` bound to the selected UUID.
Offline dataset/model flags and the exact repository `src` import path are explicit. A child cannot
see or score a non-target lane.

## 6. One five-job DAG

After a passing final preflight and Slurm `--test-only` route gate, exactly one DAG may be submitted:

1. one exclusive three-A100 controller executing the seven lanes sequentially;
2. three `afterany` model finalizers;
3. one `afterany` family finalizer.

This is five Slurm jobs total. Sequential execution trades throughput for deterministic device
selection and prevents seven independent scheduler choices from repeatedly landing on occupied
GPUs. The job limit is 24 hours. There is no automatic resubmission or fallback route.

## 7. Composite integrity

Every recovered lane must produce a complete `lane_result.json` whose artifacts, byte sizes and
SHA-256 values validate under the fresh model root. The finalizers then bind:

- 17 original source lane results by their already frozen hashes;
- seven new recovery lane results by newly computed hashes;
- exactly eight lanes per model and 24 lanes family-wide.

Only a complete 24/24 composite may set `normalization_allowed: true`. Missing, blocked or invalid
lanes remain missing; they are never represented as zero scores.

## 8. Final fail-closed preflight

Execution requires all of:

- exact contract/config/implementation identities;
- clean HU checkout at an implementation-descendant commit;
- source 17+7 hash ledger validation;
- fresh isolation root absence;
- first recovery root preservation;
- exact HU-home usage at or below 30 GiB, with no HU-home writes;
- no `m0r-v1-*` duplicate jobs;
- eligible exclusive `gruenau10` three-A100 Slurm route.

## 9. Prohibitions

This contract forbids rescoring the 17 complete lanes, modifying either prior root, changing
scientific semantics, lowering memory gates, selecting a non-A100 GPU, non-deterministic device
selection, parallel independent lane submissions, automatic resubmission, a second isolation
wave, M1/M2 work, corpus/network work, cleanup, deletion, HU-home writes and foreign-process
intervention.

## 10. Frozen implementation

- implementation commit: `1bf87f84cff5b67c1a45d5a2b4244a59fa226337`;
- operator SHA-256:
  `99ba9adb0e74f14f7a4b3e3b20e5e4ccd1c3a61fea0747ac34fc0544a6942d39`;
- recovery module SHA-256:
  `6274c6f3ca502744611efaf4f96055272bb6cd0c114e84f90b7b191ef683eab1`;
- recovery tests SHA-256:
  `440d8d5665ab34eab7ff5f911c957089e03d0c193d6a65ad11004de4e66c4c3f`;
- config SHA-256:
  `0fcd32da2c29eb9f2c8d0d838d160746890ddbec0d51d833bce9c1cc9943aa35`.

The implementation identity includes one preflight-only correction discovered during the first
authorization attempt: isolation mode now reads the dedicated
`m0_seven_lane_exclusive_a100_recovery` scoped authorization key instead of the consumed first-wave
key. That attempt stopped at preflight with 14/15 checks passing; it created no recovery root and
submitted no job. The correction changes no execution topology or scientific behavior.

## 11. Authorization boundary

The config remains `execution_authorized: false`. Preparation, tests, publication and HU read-only
inspection do not open the wave. Execution requires a new exact user instruction binding this
contract's final SHA-256 or config SHA-256 and authorizing publication/HU fast-forward, one final
preflight, creation of the fresh root, exactly one five-job DAG and read-only monitoring.

That future authorization will not cover normalization, scientific interpretation, M1/M2,
cleanup or any retry after this isolation wave.
