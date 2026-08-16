# M0 OLMo eval-v1 qualification wave v1

**Status:** `implementation_ready_environment_binding_pending` | **Owner:** project | **Created:** 2026-08-16
**Supersedes:** none

## Purpose and estimand

This bounded wave will qualify the runtime, task data and normalization path needed before the
scientific M0 evaluation can be frozen. Its target is the exact pretrained OLMo checkpoint chosen
by the evaluation-first design. It does not estimate M0 capability or retention and cannot produce
thesis results.

The wave answers only these engineering questions:

1. can the pinned Harness environment discover and validate every proposed task;
2. can the exact OLMo model and tokenizer load on the selected runtime route;
3. do bounded test-only task smokes produce finite, schema-valid raw artifacts;
4. do WikiText and TurBLiMP normalization reproduce the declared upstream semantics; and
5. what runtime and storage evidence is needed to freeze the scientific M0 wave.

Any invocation using `--limit`, a reduced task subset or a test fixture is qualification evidence
only. Its metrics must be labelled `test_only_non_scientific` and must never enter a paper table,
model comparison, gate or trajectory plot.

## Scope and prohibitions

The user explicitly authorized running and trying this qualification wave on 2026-08-16. That
authorization covers Git publication of the narrow implementation, fast-forward synchronization of
the clean HU monorepo, bounded HU read-only preflight, one new scratch-only environment, bounded
task-data retrieval, one CPU/data preflight and the test-only Slurm array described below. Scoring
submission remains fail-closed until the implementation/environment identities are inserted and the
companion config is frozen. It does not authorize scientific M0 evaluation, training, corpus
materialization, cleanup or deletion. Prior model, corpus and evaluation roots stay read-only.

## Immutable identities at draft stage

- model: `allenai/OLMo-2-0425-1B`;
- model revision: `a1847dff35000b4271fa70afc5db10fd29fedbdf`;
- historical model-manifest path:
  `/vol/tmp2/yesildau/m1_provenance_screen_v3/models/allenai__OLMo-2-0425-1B/model_manifest.json`;
- historical model-manifest SHA-256:
  `8702b80d5b7e4c996c8ce2ff5fe771ada08ab0080bde1926c0b1f53c607303dc`;
- LM Evaluation Harness: v0.4.12, commit
  `6d642546f4688648fced259eb3302efd36ece5af`;
- model backend: `hf`;
- prompt mode: no chat template and no system instruction;
- Python, NumPy, Torch and few-shot seeds: 42;
- proposed new root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v1`.

The implementation commit, adapter hashes and complete environment lock remain unresolved until the
preparatory commit and environment creation finish. The selected qualification route is one
V100-32GB per lane, FP16, at most three concurrent lanes. Dataset content manifests are outputs of
the authorized online data preflight, not circular prerequisites for starting that preflight.

## Protocol

### Q0 — local implementation and tests

- implement an M0 standard-task adapter that accepts only a frozen model manifest, registry and
  fresh output namespace;
- implement the M0 project-factual/probing adapter without changing existing scoring semantics;
- expose one user entrypoint which submits a seven-lane Slurm array: WikiText, Pile-10k, BLiMP,
  the remaining English capability tasks, Turkish capability tasks, factual access and generation
  integrity;
- allocate one independent model/GPU process per lane and cap concurrency through the frozen array
  bound; do not run multiple model processes concurrently on one GPU;
- attach one `afterany` finalizer which always records missing/failed lane state but emits the
  complete evaluation manifest only when all seven lanes have matching identities and complete;
- preserve raw Harness/project outputs and normalize them in a separate idempotent step;
- reject `--limit` unless the run classification is exactly `test_only_non_scientific`;
- add identity, task-resolution, schema, partial-result, resume-mismatch and duplicate-key tests.

Q0 is local engineering. Passing Q0 does not make the contract executable.

TurkishMMLU is explicitly excluded from qualification v1 because access is unresolved. This is not
an eval-v1 exclusion decision. If it is later included, it receives a separate five-shot lane in a
new contract version; it may not be inserted silently into the zero-shot Turkish lane.

### Q1 — bounded read-only HU preflight

The authorized read-only inspection verified the clean active HU monorepo, historical model
manifest and exact model revision, proposed-root absence, scratch capacity/inodes, a compatible
Torch 2.6/CUDA 12.4 V100 base environment, three idle V100-32GB GPUs and absence of duplicate
project jobs. HU home, the dirty legacy checkout and all previous evidence roots remain read-only.

### Q2 — environment and task-data qualification

The first prepared environment root
`/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v1` is preserved and rejected: a
nested-venv path-resolution bug inherited shared Torch 2.7/CUDA 12.8 instead of the requested
Torch 2.6/CUDA 12.4 compatibility packages. No data preflight, model load, GPU job or scoring used
that environment. It is immutable and must not be reused or cleaned by this wave.

The repair uses the fresh dedicated root
`/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v2`, preserves the parent compat
prefix path without resolving it to the shared interpreter and asserts the exact base and final
runtime identities before accepting its lock:

- prove the installed `lm_eval` source identity equals the pinned commit;
- record Python, Torch, Transformers, Datasets, tokenizers, CUDA and GPU identities;
- run task discovery and validation for the exact proposed task IDs;
- resolve immutable dataset revisions and record byte/content manifests sufficient for offline
  reload;
- resolve TurkishMMLU access as either included with an exact revision or explicitly excluded;
- record Pile-10k runtime evidence without converting a limited smoke into a scientific subset.

### Q3 — test-only OLMo smoke and parity

Use the exact OLMo revision and bounded, predeclared smoke limits: Harness limit two per
task/subtask, eight ordered factual probes, 31 generation prompts and 31 generic completion items.
Every included task receives a
finite-forward and output-schema smoke. WikiText additionally receives canonical count/result
parity plus the declared heading sensitivity. TurBLiMP receives explicit 16-subtask macro parity
despite the upstream duplicate YAML key. No Q3 metric is a scientific M0 score.

The adapter must write a machine-readable classification beside every raw result and the
normalizer must refuse to combine `test_only_non_scientific` rows with scientific rows.

### Q4 — qualification result and freeze gate

Write one compact result record containing identities, task resolution, dataset manifests,
runtime/storage measurements, parity evidence, tests, failures and unresolved blockers. The gate
may be only `qualified_for_eval_v1_freeze_review` or `blocked`. It may not be `M0_PASS`,
`M0_FAIL`, `ready_to_train` or a model-selection result.

## Inputs, outputs and schemas

The proposed root is fresh and fail-closed. Required future outputs are:

- `qualification_manifest.json`;
- `environment_lock.json`;
- `model_identity.json`;
- `task_resolution.jsonl`;
- `dataset_content_manifest.jsonl`;
- `runtime_measurements.jsonl`;
- `parity_results.jsonl`;
- `raw_artifact_manifest.jsonl`;
- `qualification_result.json`;
- `final_inventory.json`.

The parallel controller additionally writes `parallel_plan.json`, `submission_manifest.json`, one
`lanes/<lane-id>/lane_result.json` per lane and `bundle_status.json`. These operational manifests
do not replace the qualification outputs above. A partial array remains visible and cannot open
normalization or create a complete evaluation manifest.

All JSON files use atomic write-then-rename. Raw artifacts are immutable. Every result row includes
contract name/version, implementation commit, model/checkpoint identity, task ID, task-config hash,
dataset revision, environment fingerprint, run classification, status and raw-artifact pointer.
The normalized schema follows `documentation/evaluation/RESULT_SCHEMA_V1.md`.

## Gates and missingness

Structural identity gates precede model load and scoring. A missing revision, hash mismatch,
unexpected existing root, unresolved task, non-finite value, incomplete denominator, schema error
or parity mismatch fails closed. Partial outputs are retained as evidence but never zero-filled or
promoted to scientific results. No outcome-aware rerun is allowed.

Missing parity evidence, unresolved dataset identity, the Pile-10k cadence decision and the final
TurkishMMLU access decision block promotion to eval-v1 freeze review; they do not prevent this
bounded qualification wave from recording the missing evidence. Until they close, the final
qualification gate remains `blocked` even when all seven smoke lanes complete.

## Preflight, resume and rollback

- require exact contract/config/implementation hashes and a fresh namespace;
- permit offline reuse only when content identity is proven;
- resume only if the complete identity fingerprint matches;
- never overwrite a completed raw artifact or prior root;
- a repair writes a new versioned namespace and preserves the failed evidence;
- normalization must be idempotent and reject duplicate metric keys.

## Verification before freeze

1. exact adapter and CLI tests pass locally and on the selected HU environment;
2. pinned Harness source identity is proven from the installed environment;
3. all final task IDs pass discovery, validation and bounded model smoke;
4. WikiText count/result parity and heading sensitivity pass reviewed tolerances;
5. TurBLiMP 16-subtask aggregation parity passes;
6. dataset revisions/content manifests and offline reload evidence are complete;
7. Pile-10k runtime/cadence and TurkishMMLU inclusion are decided;
8. output/resume/partial-result protections pass;
9. the final implementation commit, resource bounds, Slurm plan and all artifact hashes are bound;
10. the reviewed document receives a final SHA-256 and exact user authorization.

## Qualification execution bindings

- implementation commit and adapter hashes;
- exact environment-lock hash after fresh scratch-only installation;
- final contract/config SHA-256 binding after those identities are inserted.

The GPU route, resource limits, seven included task lanes, per-task smoke limits, cache bounds and
fresh output root are fixed in the companion config.

## Eval-v1 promotion blockers

- dataset revisions and content manifests from the data preflight;
- TurkishMMLU include/exclude decision;
- WikiText and TurBLiMP numerical parity tolerances;
- Pile-10k scientific cadence rule;
- final output schemas, inventory rule and retention class;

## Authority boundary

Environment preparation may run under the 2026-08-16 user authorization. The CPU/data preflight and
GPU array may run only after the remaining execution bindings are recorded and the config becomes
`frozen`. Any semantic or resource change after that freeze needs new user authorization and a new
namespace. Scientific M0 evaluation always requires a later, separate frozen execution contract.

## Change policy

Before freeze, corrections edit this draft with review. After freeze, changing model/revision,
Harness commit, task set, dataset revision, prompt, few-shot count, smoke limit, parity tolerance,
runtime route, output schema or resource bound creates a new contract version. A semantics-neutral
implementation repair may be append-only only when equivalence evidence is explicit and the failed
namespace is preserved.
