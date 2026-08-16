# M0 OLMo eval-v1 qualification wave v1

**Status:** `frozen` | **Owner:** project | **Created:** 2026-08-16
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
submission was fail-closed until the implementation/environment identities were inserted and the
companion config was frozen; those v4 bindings are now complete below. It does not authorize
scientific M0 evaluation, training, corpus
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

The qualification execution bindings are frozen as follows:

- implementation commit: `7ba5099215103266afc17cfad1b45b7cfcc399b2`;
- operator entrypoint SHA-256:
  `800127f937f2e2128eb45a1aabd27c38ce09137abfae2d568171ddb58ac02785`;
- parallel controller SHA-256:
  `9c3f6aafcf0b00c56102f60b3956bfeec856770099cbe973a358a6ba389cd869`;
- Harness adapter SHA-256:
  `917e63abab19cb0a7bb86e054040abf24658f83ff9939c742b802bc7de6ee883`;
- project adapter SHA-256:
  `279d3adc7916919d8507df472ecb1457b315ad8e263343b53709d70116fc2dd3`;
- v3 environment lock SHA-256:
  `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`;
- v3 environment identity SHA-256:
  `9061cbc59d021676ca6b768f7688eb7da10e5460bf4919b963c9931eefcc7d71`;
- companion config SHA-256:
  `85caf5157338e1aa2a6e2f8185ebcc9bf386395ddbc88cd7e5ff2ed5996e009b`.

The selected route is one V100-32GB per active lane, FP16, with at most three concurrent lanes.
Dataset content manifests are outputs of the authorized online data preflight, not circular
prerequisites for starting that preflight.

### Append-only Slurm partition correction

The first frozen submission attempt created only the planned namespace
`/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v1`. Slurm rejected the very first `sbatch`
because the CPU-only data preflight was sent to partition `gpu` without a GPU GRES request. No job
ID was issued; task-data preflight, network retrieval, model load, GPU allocation and scoring were
all zero. The root contains only the plan/bundle status and is preserved without reuse or cleanup.

The semantics-neutral operational repair routes the CPU/data preflight and finalizer to `std`, keeps
the seven evaluation lanes on `gpu` with `gpu:v10032gb:1`, records Slurm stderr on any future
submission rejection and uses the new root
`/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v2`. All model, task, limits, precision, seeds,
cache bounds and scientific prohibitions remain unchanged. The repair must bind a new implementation
commit plus exact config hashes before resubmission.

Those repair bindings are now frozen:

- repaired implementation commit: `31686cf07b6edb2d64cdb0b9ec44ba838a0ada84`;
- repaired submitter SHA-256:
  `3d21321941628b83c31ac6f7da28efa6b8fe782447676c0d66e907f2ec2c9fd1`;
- factual qualification config SHA-256:
  `a953177c55ddce313f47a1996a96c2bbd43ca52e8b84160fd32d5ac8f9f60437`;
- generation qualification config SHA-256:
  `354f5fd1bc818c09cd8f1fca17f9614fa297b2268169c48160e4bae02b359279`;
- repaired companion config SHA-256:
  `2ac4edf6248a64dffab4a33ebd5c57a5cbae78b6fa00cc4ca3cbab2826832dc5`.

Slurm `--test-only` accepted the exact `std` 8-CPU/32G/2h data route, the
`gpu:v10032gb:1` 8-CPU/64G/4h evaluation route and the `std` 2-CPU/8G/30m finalizer route. The
original 2026-08-16 test-only execution authorization remains in force for this semantics-neutral
repair and fresh v2 namespace.

### Append-only task materialization and project-input correction

The v2 Slurm route was accepted. Data preflight job `460950` discovered and validated all ten task
IDs, but Harness `validate` does not instantiate tasks or download datasets; the resulting cache
manifest contained zero files and zero bytes. The faulty gate allowed array `460951` to start.
WikiText, Pile-10k and BLiMP each failed before scoring because offline mode could not reach their
datasets. The factual lane failed before model load because the registry path was absent from the
active monorepo checkout. Other lanes were cancelled; the generation lane reached weight loading
but produced no completed lane result or accepted score. Finalizer `460952` recorded zero complete
lanes, `partial_invalid`, `normalization_allowed=false` and gate `blocked`. All 62 inventoried files
under `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v2` are preserved without reuse or cleanup.

The next semantics-neutral repair uses fresh root
`/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v3`. Its CPU preflight must instantiate the exact
TaskManager task/group set online, require a non-empty bounded cache, instantiate the same set again
with every offline flag enabled, and only then release the GPU dependency. It also verifies every
factual/generation input byte hash before model load. The factual registry is read-only at its
preserved legacy path with SHA-256
`2cf9bf4a61f7ef3771e71caf61f03a3e59d22707ef4d5367a6ef6184a18f664b`; the legacy Git worktree
itself is not modified or reused. A new implementation commit and exact config hashes are required
before v3 execution.

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

The v2 repair correctly installed Torch 2.6.0+cu124 and Harness 0.4.12 at the pinned commit, but a
final metadata-name gate compared upstream `lm_eval` without normalizing it to distribution name
`lm-eval`; the command stopped before writing a completed environment identity. The v2 root is also
preserved, immutable and excluded from reuse. No data preflight, model load, GPU job or scoring used
it.

The v3 repair bindings are frozen:

- implementation commit: `28589d1c3f01a1824ae3e4c30b357ccb340a0935`;
- parallel materializer/controller SHA-256:
  `a012ed1d6dbe76112e9e16c6584f70ee27b725134f339653ac2e83a37c99daf9`;
- project-input adapter SHA-256:
  `5b8a49003e151454c3028c2eb135fda943a9169037a1a4b9d04ae5a0810fcde6`;
- factual config SHA-256:
  `e9193dddc87ae7143b015378205461e941d9b748da615fb5ba836f78fe92fbbf`;
- generation config SHA-256:
  `bc15f21b15906806cf605138473bd829dadbaa25d4abb844532af203235caf79`;
- repaired companion config SHA-256:
  `d29ebf6c9e0fd55b7ea529a4a4d75739860575371ee18a57b0ae72648a39cbad`.

The original user authorization remains limited to this test-only, non-scientific qualification
attempt. V3 is fail-closed and may release the GPU dependency only after materialized-cache,
offline-reload and project-input gates all pass.

### Append-only XNLI repository-identity compatibility correction

V3 data preflight `460959` correctly materialized 338 files / 409,436,401 bytes and verified both
project-input lanes before model load. It then failed closed during TaskManager construction because
Harness v0.4.12's XNLI common YAML uses legacy single-segment `dataset_path: xnli`. The current Hub
resolves the official dataset as `facebook/xnli`; the existing path produced an invalid `hf://`
URI under the pinned environment. Offline reload consequently failed as well. Array `460960` never
received a GPU and no model load or scoring occurred; dependency-dead array cancellation allowed
finalizer `460961` to record 0/7 lanes, normalization disabled and gate `blocked`. The entire v3
root is preserved without reuse or cleanup.

The v4 correction introduces only two pinned local task IDs,
`xnli_en_facebook_v1` and `xnli_tr_facebook_v1`. Their prompts, choices, label target, splits,
accuracy metric and zero-shot settings reproduce Harness v0.4.12 XNLI EN/TR; the overlay changes
only `dataset_path` to `facebook/xnli`, pins Hub revision
`b8dd5d7af51114dbda02c0e3f6133f332186418e`, and renames the task IDs so the compatibility variant
cannot be confused with upstream. The other eight required task IDs are unchanged. Overlay file
hashes, adapter hashes, project configs and the fresh v4 namespace are frozen as follows:

- implementation commit: `e227fba0df311c5149b12c6bb8cca39522156985`;
- operator entrypoint SHA-256:
  `3d21321941628b83c31ac6f7da28efa6b8fe782447676c0d66e907f2ec2c9fd1`;
- parallel controller/materializer SHA-256:
  `3e1d77068239dec45521777e274d60e548fca7618c7f958118bd91a7e39aae9a`;
- Harness adapter SHA-256:
  `0e8ee7a842e2cdb93c0f1bee6ce59dda773e3fe3ba10c01e1e6a9c246c6d5499`;
- project adapter SHA-256:
  `5b8a49003e151454c3028c2eb135fda943a9169037a1a4b9d04ae5a0810fcde6`;
- XNLI common overlay SHA-256:
  `24e2a5784870f6a204b3d4b134195c735c366bbb7ddd5525605a924fb3941fc5`;
- XNLI EN overlay SHA-256:
  `786e1bba364a7165663f73b15191e42953d0702ff6b1665b449b08ed07f6ee89`;
- XNLI TR overlay SHA-256:
  `cb8c66fe0baffe22849d1ce361b4f59a493779ab0fa7f1542ccb23d6da8d5c1e`;
- factual qualification config SHA-256:
  `9d9b293ffac2b18182ddced629885d2d383eb5a30b5b343af6ebc6d9beb8d6c2`;
- generation qualification config SHA-256:
  `5ab21222221d3368a68d4e33f6455c588c9d5320d1c7e3f325a990cf814bb3d9`;
- companion config SHA-256:
  `d4efdaf7713a860c96d151d9734c4d7303f77d8a498686d0bb31a81355b6462f`;
- fresh execution root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v4`.

The v4 wave is execution-ready and authorized only as bounded `test_only_non_scientific`
qualification. The v1--v3 roots remain immutable evidence and are not reused.

### Append-only automatic GPU-route correction

The first v4 binding above was not submitted and its proposed root remained absent. Before
execution, the user required the one-command evaluator to avoid manual GPU rerouting. The current
operational binding therefore replaces only the fixed single-V100 submission route with a
scheduler-probed candidate table. Every candidate is checked with `sbatch --test-only`; rejected
routes and their scheduler messages are written to `gpu_route_selection.json`. Exactly one route is
selected by earliest estimated start time, with declared order as the tie-breaker, and exactly one
seven-lane array is submitted. No duplicate/racing evaluation arrays are allowed.

The frozen candidate order is V100-32GB, A100-80GB, RTX3090, RTX6000 and RTX A6000. V100, A100,
RTX6000 and RTX A6000 use partition `gpu`; RTX3090 uses `wbimlgpu`. Each route requests one GPU and
64 GiB host memory. Live qualification inspection showed the current `yesildau` association is not
permitted on `wbimlgpu`; this does not abort the wave when another candidate passes, and the denial
must remain visible in the route ledger. The selector does not bypass Slurm permissions or inspect
foreign GPU processes.

The current automatic-route bindings are:

- implementation commit: `24795de90b65abe508d10b9268523960b52ae510`;
- operator entrypoint SHA-256:
  `ae2c0b4a595250c404cc1e7e3778c8f6a5efdb4be298ffb51e2c3dc03cb8e3bd`;
- parallel controller/materializer SHA-256:
  `7d3971849df0af8ce8e32d5eeae61f8118f2dc3de0d39c816a4a3144788cfb38`;
- companion config SHA-256:
  `5593c566755e06c658cf23be331a2484e7d2d1abcc1df8a26a398fb806cb5466`;
- fresh execution root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v4`.

The CPU data preflight, selected GPU array and `afterany` finalizer are submitted by one command.
After submission, Slurm owns dependency waiting; no interactive agent wait is required.

### Append-only active-task removal

On 2026-08-16 the user removed XNLI from the thesis evaluation protocol. V4 data job `461253` was
still in CPU task discovery/materialization; array `461254` was dependency-pending, so no GPU,
model load or scoring had started. Those two jobs were cancelled and finalizer `461255` recorded
0/7 lanes, `scientific_result=false`, normalization disabled and gate `blocked`. Its 18-file,
3,668,858-byte root remains immutable. The prior local overlay did not complete an end-to-end
qualification and is removed from the active repository.

The replacement v5 task set contains eight Harness task IDs across the same five Harness lanes:
WikiText, Pile-10k, BLiMP, HellaSwag, three WinoGender slices and TurBLiMP. The two project-native
lanes remain unchanged. XNLI is absent from the active registry, task matrix, configs and commands.
The compatibility evidence and a bounded future upstream-repair outline are preserved separately in
[`../../evaluation/XNLI_HARNESS_COMPATIBILITY_INCIDENT.md`](../../evaluation/XNLI_HARNESS_COMPATIBILITY_INCIDENT.md).

The v5 replacement bindings are frozen:

- implementation commit: `1c3791a9c140777df0fc3df66a817fcafcfd4bc6`;
- operator entrypoint SHA-256:
  `ae2c0b4a595250c404cc1e7e3778c8f6a5efdb4be298ffb51e2c3dc03cb8e3bd`;
- parallel controller/materializer SHA-256:
  `2fd4caa8c686c59925957ed41b9c6b4423e17ab42c3f0fa3d95ec5a100349e68`;
- Harness adapter SHA-256:
  `5480e4f01ef89047d979ca5a00511514283da11487ea8d2842e2e46eb38d8598`;
- project adapter SHA-256:
  `5b8a49003e151454c3028c2eb135fda943a9169037a1a4b9d04ae5a0810fcde6`;
- factual qualification config SHA-256:
  `7c2919fef13fa95f069cba94b919134becf749fc692a6193879322f321dc3502`;
- generation qualification config SHA-256:
  `9f34d8d825823dffe6ed714f9e369b1bddc71ad49faf7cddca5d393211017eee`;
- companion config SHA-256:
  `37640365560929e1a62ee216a246a2738061964e9c65d82698ef28ee52eec1a2`;
- fresh execution root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v5`.

The existing bounded test-only authorization permits this reduced replacement wave; it does not
convert v5 into a scientific M0 run.

### Append-only TaskManager result-serialization correction

V5 data job `461284` discovered and validated all eight task IDs and materialized 404 cache files /
413,883,954 bytes. After `load_task_or_group` returned successfully, the preflight diagnostic tried
to evaluate `sorted(d)`. Harness returned a mapping containing both string and `ConfigurableGroup`
keys, so Python raised `TypeError: '<' not supported between instances of 'str' and
'ConfigurableGroup'`. Offline reload reached the same diagnostic failure. This was a controller
serialization bug after task construction, not a dataset/task failure.

Array `461285` never received a GPU and finalizer `461286` preserved 431 files / 417,737,203 bytes,
0/7 lanes, no scientific result and a blocked gate. The v5 root is immutable. Its preflight-result
SHA-256 is `3a2db3eafe9a86ed57a9e2a8a6c4192362a43e062e7bbea0d7b873699cfc682e` and
qualification-result SHA-256 is
`8c27a4522958e6803690685b5b4bc4a48c228c707a814ac36badc184ee1e8a36`.

The v6 repair changes only the diagnostic payload to
`{"loaded_entry_count": len(d)}`. It does not alter TaskManager inputs, task identities, datasets,
cache bounds, offline flags, model, lane limits, GPU routes or evaluation semantics. A regression
test requires both online and offline generated commands to use the JSON-safe count and forbids
`sorted(d)`. The v6 repair bindings are frozen:

- implementation commit: `abe4f72bdd570b05f7c1d35cd62629a5387eff73`;
- operator entrypoint SHA-256:
  `ae2c0b4a595250c404cc1e7e3778c8f6a5efdb4be298ffb51e2c3dc03cb8e3bd`;
- parallel controller/materializer SHA-256:
  `67393a9894bd54c712663eb38b06705be8c291a5a44664e88d093d8aca4d5625`;
- Harness adapter SHA-256:
  `5480e4f01ef89047d979ca5a00511514283da11487ea8d2842e2e46eb38d8598`;
- project adapter SHA-256:
  `5b8a49003e151454c3028c2eb135fda943a9169037a1a4b9d04ae5a0810fcde6`;
- factual qualification config SHA-256:
  `8c2b1ef0a09cad91e7bdc9685d5851f7224f892b391ed61e4f6c48ee785c24bb`;
- generation qualification config SHA-256:
  `25f6837d74aa8e862e7349569a9c469a5916c7efc578b922db97b302ca3b2141`;
- companion config SHA-256:
  `29ad59b7c9c665fded8e25f534a3258b4329a649421a9fc4f89a51677dd76772`;
- fresh execution root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v6`.

The existing bounded test-only authorization permits this semantics-neutral controller repair.

### Append-only installed-package integrity and independent-lane correction

V6 data job `461301` completed in 401.94 seconds, resolved all eight task IDs, materialized 404
cache files / 413,883,545 bytes and passed the offline reload. Array `461302` then loaded the exact
model and cached task data. The factual-access and generation-integrity lanes completed, while all
five Harness lanes stopped before scoring with the same
`FileNotFoundError: Unable to find package root within 3 upwards` from Harness
`run_task_tests`. This is the installed VCS wheel layout lacking the repository test-root expected
by CLI `--check_integrity`; it is not evidence that a task, dataset or model failed. Finalizer
`461303` recorded 2/7 complete lanes and a blocked, non-scientific result. The immutable v6 root
contains 489 files / 417,993,720 bytes. Its exact hashes are:

- preflight result: `392f52d37086d88faad510eec22120df18a473dc0c6cd7cd703be02af4de940d`;
- bundle status: `d2e13eeefad1929d0c71fdb144b0e6a2c6bedc6c9990a941de17ebc5fc4d29de`;
- qualification result: `1f2c386e8e1ae2378b0166b5d6b3e335c3a8e0a4f692956b748667fed09e7bd6`;
- final inventory: `1d22a689ca92aaf74a02da72fee237eab9768b9d7c25cbbcd7e56b12eda7cfb2`.

V7 removes only the redundant Harness CLI `--check_integrity` invocation. The controller retains
the stronger execution preflight already evidenced in v6: exact task discovery/validation,
TaskManager construction during online materialization, bounded content inventory and a second
TaskManager construction with all network routes disabled. Model identity, Harness commit, task
IDs, few-shot values, limits, datasets, seeds, precision and metric implementations are unchanged.
Numerical WikiText/TurBLiMP parity remains an explicit later blocker and is not implied by this
repair.

V7 also replaces the one-GPU-type array with seven independent lane jobs created by the same
operator command. Each lane receives one scheduler-tested route, exact route/job identity is stored
with its result, and one `afterany` finalizer depends on every lane job. Declared physical route
slots allow three V10032GB, three A10080GB, one RTX3090, three RTX6000 and four RTXA6000 candidate
assignments, but only routes passing `sbatch --test-only` are eligible. This maximizes concurrent
launch across GPU types without claiming that unavailable hardware ran. The finalizer always writes
`evaluation_results.json` with all lane statuses, runtimes, route identities and parsed metric or
project summary documents; `raw_artifact_manifest.jsonl` retains every raw artifact path, byte count
and SHA-256.

The v7 bindings are frozen:

- implementation commit: `d39cdc2653a558c1cf494f6791b00a4aaef3ba08`;
- operator entrypoint SHA-256:
  `1ec72fd68afe3668a7663d456fd6dac94bdc75fda839adf98409843a81b80687`;
- parallel controller/finalizer SHA-256:
  `874b2739c96191a954d9af7d1a8c7352db847dc94af51413b3fa3a10a4c00b90`;
- Harness adapter SHA-256:
  `953f1958b6051be33e96c2b94ecb86ae79c5b19ce9a9376cd00f16af7ecdcfa5`;
- project adapter SHA-256:
  `5b8a49003e151454c3028c2eb135fda943a9169037a1a4b9d04ae5a0810fcde6`;
- factual qualification config SHA-256:
  `0f3d385847a6652279418b9914224e6c51d8a511e0986a282ceed4122fbfc75e`;
- generation qualification config SHA-256:
  `15790e1272448b4ddf17b00acea9aefc07482a6a45163e41b0abefa67f8038ca`;
- companion config SHA-256:
  `baa039ba2827256f33466a3018fa49afe325588536784ae492c97958b8cc5f26`;
- fresh execution root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_v7`.

The user's 2026-08-16 instruction to implement this repair and keep the one-command complete result
pipeline authorizes this bounded v7 qualification wave. It remains test-only and cannot create a
scientific M0 score.

The corrected repair uses the dedicated root
`/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3`, preserves the parent compat
prefix path without resolving it to the shared interpreter, normalizes distribution names and
asserts the exact base/final runtime identities before accepting its lock. That preparation passed
with Python 3.11.15, Torch 2.6.0+cu124, CUDA 12.4, Transformers 5.13.0, Datasets 5.0.0,
Accelerate 1.14.0 and Harness 0.4.12 at the pinned commit:

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
- `evaluation_results.json`;
- `qualification_result.json`;
- `final_inventory.json`.

The parallel controller additionally writes `parallel_plan.json`, `submission_manifest.json`, one
`lanes/<lane-id>/lane_result.json` per lane and `bundle_status.json`. These operational manifests
do not replace the qualification outputs above. A partial lane set remains visible and cannot open
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

Environment preparation completed under the 2026-08-16 user authorization. The CPU/data preflight
and test-only independent GPU lane jobs may now run through the frozen companion config. Any
semantic or resource change after this freeze needs new user authorization and a new namespace.
Scientific M0 evaluation always requires a later, separate frozen execution contract.

## Change policy

Before freeze, corrections edit this draft with review. After freeze, changing model/revision,
Harness commit, task set, dataset revision, prompt, few-shot count, smoke limit, parity tolerance,
runtime route, output schema or resource bound creates a new contract version. A semantics-neutral
implementation repair may be append-only only when equivalence evidence is explicit and the failed
namespace is preserved.
