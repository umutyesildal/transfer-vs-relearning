# M0 OLMo eval-v1 qualification wave v1

**Status:** `draft_not_executable` | **Owner:** project | **Created:** 2026-08-16  
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

Preparation scope is limited to local implementation, tests, manifests and contract review. A
future separately authorized execution may use one fresh scratch namespace for task/runtime
qualification and bounded model smokes.

This draft does not authorize HU/SSH, network retrieval, model or dataset download, Slurm/GPU,
evaluation or scoring, training, corpus materialization, cleanup, deletion, publication or push.
It does not authorize the scientific M0 evaluation. Prior model, corpus and evaluation roots stay
read-only.

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

The implementation commit, adapter hashes, complete environment lock, CUDA/GPU route, dataset
revisions and content manifests remain unresolved. They must be inserted before this contract can
be reviewed for freeze.

## Protocol

### Q0 — local implementation and tests

- implement an M0 standard-task adapter that accepts only a frozen model manifest, registry and
  fresh output namespace;
- implement the M0 project-factual/probing adapter without changing existing scoring semantics;
- preserve raw Harness/project outputs and normalize them in a separate idempotent step;
- reject `--limit` unless the run classification is exactly `test_only_non_scientific`;
- add identity, task-resolution, schema, partial-result, resume-mismatch and duplicate-key tests.

Q0 is local engineering. Passing Q0 does not make the contract executable.

### Q1 — bounded read-only HU preflight

A future authorized wave must verify the exact repository commit, clean relevant paths, historical
model-manifest bytes, proposed-root absence, scratch capacity/inodes, runtime route and absence of
duplicate project jobs. HU home and all previous evidence roots are read-only.

### Q2 — environment and task-data qualification

In one dedicated, content-locked environment:

- prove the installed `lm_eval` source identity equals the pinned commit;
- record Python, Torch, Transformers, Datasets, tokenizers, CUDA and GPU identities;
- run task discovery and validation for the exact proposed task IDs;
- resolve immutable dataset revisions and record byte/content manifests sufficient for offline
  reload;
- resolve TurkishMMLU access as either included with an exact revision or explicitly excluded;
- record Pile-10k runtime evidence without converting a limited smoke into a scientific subset.

### Q3 — test-only OLMo smoke and parity

Use the exact OLMo revision and bounded, predeclared smoke limits. Every final task receives a
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

All JSON files use atomic write-then-rename. Raw artifacts are immutable. Every result row includes
contract name/version, implementation commit, model/checkpoint identity, task ID, task-config hash,
dataset revision, environment fingerprint, run classification, status and raw-artifact pointer.
The normalized schema follows `documentation/evaluation/RESULT_SCHEMA_V1.md`.

## Gates and missingness

Structural identity gates precede model load and scoring. A missing revision, hash mismatch,
unexpected existing root, unresolved task, non-finite value, incomplete denominator, schema error
or parity mismatch fails closed. Partial outputs are retained as evidence but never zero-filled or
promoted to scientific results. No outcome-aware rerun is allowed.

The numerical parity tolerances, exact smoke limits, Pile-10k cadence decision and TurkishMMLU
decision remain freeze blockers. Until they are fixed, the only valid status is `draft_not_executable`.

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

## Freeze blockers

- implementation commit and adapter hashes;
- exact Python/package/CUDA/GPU environment;
- download/file/byte limits and scratch capacity bound;
- dataset revisions and content manifests;
- final task IDs and per-task smoke limits;
- TurkishMMLU include/exclude decision;
- WikiText and TurBLiMP numerical parity tolerances;
- Pile-10k scientific cadence rule;
- exact Slurm resources, timeouts and job topology;
- final output schemas, inventory rule and retention class;
- final contract/config SHA-256 and explicit authorization.

## Authority boundary

This file and its companion config are design artifacts only. No qualification command may run
until all freeze blockers are closed, the status becomes `frozen`, exact hashes are recorded and
the user explicitly authorizes that exact frozen wave. Scientific M0 evaluation requires a later,
separate frozen execution contract after qualification succeeds.

## Change policy

Before freeze, corrections edit this draft with review. After freeze, changing model/revision,
Harness commit, task set, dataset revision, prompt, few-shot count, smoke limit, parity tolerance,
runtime route, output schema or resource bound creates a new contract version. A semantics-neutral
implementation repair may be append-only only when equivalence evidence is explicit and the failed
namespace is preserved.
