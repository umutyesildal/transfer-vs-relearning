# HU SSH And Slurm Launcher Runbook

**Audience:** AI agents and maintainers operating the HU cluster for this thesis.

Read the workspace `AGENTS.md` and
`documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md` before using anything in this
directory.

## 1. Security And Authority

`ssh-client/.env` contains HU credentials. It is local secret material.

- Never print, summarize, copy, commit, or document its contents.
- Never add `.env` to a shell trace or command output.
- A remote read-only inspection does not authorize training submission, file deletion, or model
  publication.
- Use Git to move source/config changes to HU. Do not SCP a repository or general run artifacts
  into HU home.
- Large datasets, checkpoints, caches, logs, and evaluations belong on `/vol/tmp/yesildau` or
  `/vol/tmp2/yesildau`, not the HU home filesystem. The only current exception is the separately
  authorized, verified model-only durability copy of the two selected Qwen M1 artifacts recorded
  in `AGENTS.md` and Documents 84/127.

## 2. Helper Selection

### `scripts/ssh_hu_gpu.sh`

Use this for a human-visible interactive SSH session. It:

- reads the username from `ssh-client/.env`;
- defaults to `gruenau10.informatik.hu-berlin.de`;
- tries an existing SSH ControlMaster first;
- otherwise asks the user for the HU password interactively;
- keeps the multiplexed connection available for up to 60 minutes.

Run from the `ssh-client` directory:

```bash
./scripts/ssh_hu_gpu.sh
```

Do not leave an unseen password prompt running. If the command asks for a password, return control
to the user or keep the interactive terminal visible.

### `scripts/hu_ssh_expect`

This is the non-interactive helper used by most historical `submit_*.sh` wrappers. It reads both
username and password from `.env`, connects to fixed host `gruenau10`, and has a 600-second silence
timeout.

Important implementation detail: it resolves `.env` relative to the **current working directory**,
not relative to its own file. Therefore historical wrappers must be invoked with
`ssh-client` as the working directory. Running them from the workspace root can fail with a missing
`.env` error.

This helper may transmit credentials automatically. Use it only for an authorized, reviewed
remote command. Never enable shell tracing around it.

### `scripts/hu_ssh_run.exp`

This older helper accepts `<host> <remote-command>` and has only a 30-second silence timeout. A
remote command can continue after the local helper reports a timeout. Do not use it for training,
evaluation, corpus generation, or any command that can remain silent for 30 seconds. Prefer a
reviewed job launcher that submits quickly and returns the Slurm job ID.

### SCP helpers

`hu_scp_expect` and `hu_scp_from_expect` are legacy credentialed transfer helpers. Prefer Git for
source/config synchronization and compact manifests/results. Never use them to copy model trees,
datasets, caches, or broad output directories into HU home. Resolve and validate every remote
target before an approved compact transfer.

## 3. Meaning Of The Shell Scripts

The scripts in this directory are a chronological operational record. They are not a reusable
current API.

- `submit_*direct.sh`, `submit_*stage*.sh`, and similar files submit one historical training
  condition.
- `submit_*eval.sh` and the initial/mid/late/final variants generate or submit checkpoint
  evaluations for a specific historical run.
- `summarize_*.sh` reads and summarizes a completed historical evaluation family.
- `inspect_general_capability_remote.sh` inspects the frozen capability-audit artifacts.
- `slurm_gpu_smoke_test.sh` is a legacy Slurm script and writes its logs to repository-local
  `logs/`; do not use it as the template for a new family without changing logs to absolute
  scratch paths.

Many historical scripts hard-code one or more of the following:

- an old YAML config;
- a historical run timestamp or job namespace;
- a specific checkpoint list;
- `gruenau9` or `gruenau10`;
- a past scratch directory;
- a repository-relative `runs/`, `artifacts/`, or `logs/` path;
- a fixed Git branch and pull step.

Do not execute a historical launcher merely because its filename resembles the next experiment.
Read the entire file, find the report that created it, and verify every path and scientific
condition. For new work, create a new versioned config and a new narrowly named launcher after the
corresponding numbered plan is frozen.

## 4. Repository And Remote Locations

Local code repository:

```text
/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/transfer-vs-relearning
```

Current local/remote development branch:

```text
corpus-update
```

HU code checkout:

```text
/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
```

HU Python:

```text
/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
```

Approved high-volume roots:

```text
/vol/tmp/yesildau
/vol/tmp2/yesildau
```

The HU checkout is allowed to contain source code, Git metadata, compact configs, and compact
manifests. High-volume outputs referenced by repository paths must resolve through symlinks to an
approved scratch root.

## 5. Required New-Job Workflow

For every new training or broad evaluation family:

1. Read `AGENTS.md`, Document 100, and the new numbered experiment plan.
2. Inspect both local repository worktrees; do not overwrite or commit unrelated generated files.
3. Implement and test locally in `transfer-vs-relearning`.
4. Use a new config with an absolute scratch `output_root`.
5. Use a new launcher whose Slurm stdout/stderr, caches, temporary files, datasets, and model
   outputs all point to scratch.
6. Commit narrowly and let the user push, unless the user explicitly asks the agent to publish.
7. On HU, use `git pull --ff-only origin corpus-update`; never reset the remote checkout to discard
   changes.
8. Run the mandatory storage and inode preflight from `AGENTS.md`. One combined preflight covers
   all sibling jobs in one unchanged, coordinated parallel submission wave; include their combined
   storage/inode estimate and every resolved destination.
9. Resolve `runs` and `artifacts` with `readlink -f`.
10. Validate dataset counts, hashes, fact membership, branch balance, training budget, expected
    checkpoint count, and estimated family size.
11. Inspect `squeue` before submission.
12. Submit once, capture the exact job ID, and inspect `squeue` immediately.
13. Confirm `RUNNING`, node/GPU allocation, resolved output path, and clean initial stderr.
14. If expected runtime exceeds five minutes, report the average and safe range and return control
    to the user. Do not sleep-monitor.
15. After completion, inspect `sacct`, stdout, stderr, metrics, selected checkpoint, artifacts, and
    post-run storage.
16. Freeze selected artifacts with manifests and SHA-256 hashes, document the result, and update
    Document 100 before opening the next phase.

## 6. Safe Status Checks

Status inspection should be read-only. The normal evidence set is:

- `squeue` for pending/running state and node;
- `sacct` for final state, exit code, elapsed time, and resources;
- the job's scratch stdout/stderr;
- the run/evaluation manifest and compact metric summary;
- `nvidia-smi` only when a running job's allocation needs confirmation;
- the preflight/post-run `du`, `df -h`, `df -i`, `readlink -f`, and large-home-file audit required
  by `AGENTS.md`.

Quiet logs are not evidence of failure. Do not submit a duplicate job without checking the queue,
accounting record, run manifest, and output directory.

## 7. Current Project-Specific Stop

Documents 105--116 are completed historical evidence. Document 117 is a historical operational
plan, preserved below for the chronological record; it is not the current project authority:

- the negative Turkish-bridge classification remains valid;
- one bounded Qwen seed-42 clean-English replay remediation is explicitly opened alongside a
  matched factual-only control;
- seed 43 opens only for a seed-42 treatment passing every unchanged factual and PPL gate;
- 500 subjects / 2,500 facts is then a mandatory scale gate;
- M2, M3, 1,000 subjects, and 5,000 subjects remain on HOLD.

No historical Document 105 launcher or old 100/500-subject script is a valid Document 117
entrypoint. New versioned configs, preflight, launchers, and storage estimates must be implemented
and reviewed before submission.

### Current-state revision (2026-08-07)

The Document 117 block above records a historical operational state. It must not be read as the
current experiment plan. The completed Qwen pilot and its operational/result authority are recorded
in Documents 136, 138, 140a, 142, and 143. The supervisor-driven scientific realignment and the
next literature-first route are recorded in Documents 144--151.

Documents 151a--151c record the first bounded model/corpus audit attempt: 151a is the frozen
read-only contract, while 151b and 151c record the attempt stopping in the approval layer before
the HU command executed. Those three documents did not contain sample results. The user later
explicitly authorized only the 151a bounded HU read-only continuation; its actual sample evidence
and decision gate are recorded append-only in Documents 151d and 151e.

This update does not authorize training, fine-tuning, GPU evaluation, full model/corpus downloads,
materialization, frozen-artifact mutation, cleanup, or HU-home output. Documents 152--154 remain
uncreated and require a separate frozen execution-contract stage.

### Current bounded-audit authority (2026-08-07)

Documents 151d and 151e are historical preliminary/provisional evidence and remain append-only.
Document 151f is the current **evidence-integrity correction and externally prompted validation**
authority; it is not a genuinely independent external review. Document 151g remains the frozen
repair contract, while Documents 151h and 151i record the completed vngrs repair execution and
post-repair gate. Document 151j is preserved as a `SUPERSEDED_UNEXECUTED_REQUIREMENTS_DRAFT` and
must not be executed. Document 151m is the frozen Phase-1 evidence-resolution contract and was
executed once; Documents 151n/151o remain historical preliminary/provisional execution and gate
records. Document 151p is the current Phase-1 local validation and blocker correction authority:
the synthetic-inventory provenance blocker and exact 65,717 inventory-reproduction component are
closed, while benchmark and source-model registries remain incomplete collection/extraction from
the executed bounded wave, not evidence of public-source absence. Document 151q is the frozen
bounded benchmark/source-model metadata registry contract with three append-only corrections and
was executed once under the user's explicit authorization. Its original SHA-256 is
`b55499242100263e0d9adbe946679b6175268012d1c3e897298413a2af1ef60c`; the first corrected SHA-256 is
`0acf5251bea811e07b6442681ec02c7bc4fa2ea584a55e8b48cbcb704d4209e3`; the second corrected SHA-256
is `c217f4d8395a8e3b657f96fd46f3e6443a11fcde6bbfbd6f7a8414933ccf89ee`; and the final
third-correction SHA-256 is `f1cdfe082a78fce612d7bc53766e88dae3182ffcf52a225f2aa81e24c2491561`. The third correction limits the
earlier no-HU/SSH language to the preparation/correction passes and makes a future separately
authorized wave eligible to use the documented `ssh-client` route, mandatory storage/path/inode
preflight, public HTTP retrieval within 151q's bounds and writes only under
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1`. HU home and prior
evidence roots remain read-only. Document 151r is the execution result and Document 151s is the
post-execution decision gate. The effective operational gate is
`blocked_by_operational_access`: the fixed EXAMS `test_with_para` response exceeded the 32 MiB
single-response bound and the wave failed closed. The global gate remains
`blocked_by_measurement_design`; future alias/template/overlap definitions and capability
measurement remain unresolved. CulturaX remains `excluded_access_blocked`. Benchmark scoring is
unconditionally forbidden. No further 151q execution is authorized by this result; a new attempt
would require a separately revised contract and explicit authorization. HU home, prior roots,
training, inference, model/tokenizer weights, corpus, GPU/Slurm, cleanup, Documents 151k/151l and
152--154 remain outside scope.

Current local SHA-256 of Document 151r is
`09ffb44bea8711e7c9e37dd7a4c5cea93d9c277f552bdc50bc556fdf55facfe8`; current local SHA-256 of
Document 151s is `cec364cf21716a186311d243094f669b998bd2cf558a02bd21fcb3438be61950`.

Document 151t was the frozen minimal 151q registry-completion retry contract; its pre-correction
SHA-256 is `eef968538b2022250803504ba1f206860c053663bb9ce74f761c3ae25c4c11cc` and its final
route-correction SHA-256 is
`63951ba5543c2c803e8466d0c43e0aace9637ca1239164dc1d9f5e49ea75f46b`. It preserved 151q/151r/151s
and kept the first execution root
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1` immutable/read-only.
Under one explicit authorization it was executed once using the new retry root
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1`; Documents 151u
and 151v record the execution result and post-retry gate. The retry PASS is scoped to the exact
EXAMS artifact and three raw model-card metadata rows. The prior `blocked_by_operational_access`
state from 151s is closed for this narrow registry-completion component; the global
measurement-design gate remains `blocked_by_measurement_design`, training is `BLOCKED`, and
`ready_to_train` is false. Scoring, inference, weights/tokenizers, corpus materialization,
GPU/Slurm, training, cleanup, deletion and prior-root writes remain forbidden. Documents 151k/151l
and 152--154 remain uncreated and unauthorized. The route correction's raw-byte, redirect-chain,
content-type and fail-closed requirements were evidenced in 151u.

Current local SHA-256 of Document 151u is
`579be50a33a8bc26c71b7f47969bfca4a9e30fde06172e3cbe21dfa772976909`; current local SHA-256 of
Document 151v is `5f822449cd5295cee26b9f550c5883d4c897276fb0ee754b20a8540393edb871`.

### Coverage and 151x protocol correction authority (2026-08-08)

Document 151w is the current validation authority for the 151u/151v coverage-matrix PASS;
SHA-256 `2b19bfbea496bb76efc4e06d24d815d2b83b06090e6ebdee6526773c5fb96de3`. The validation
read only the eight explicitly allowed registry/reconciliation/report files and parent-root
inventories on HU. It found six retry entity-summary rows instead of frozen per-entity-field
coverage, missing coverage metadata in all 132 first-wave rows, and incomplete retry benchmark
and model registry schemas. No HU file or root was modified. 151u/151v remain historical and
unchanged; their successful artifact/hash/storage facts are preserved, but their scoped coverage
PASS is `PROVISIONAL / UNSUPPORTED BY THE FROZEN COVERAGE RULE`.

Document 151x was the current frozen minimal repair contract and was executed exactly once under
explicit authorization. Its pre-correction SHA-256 is `a19ed3b7e15540fa2810d5f483b2015cc5badd2bd41949d8678f945d3a6fb32e`; final protocol-correction SHA-256 is
`9c66cb95ee264d8411750d8e79aff258eaaeb4d1789ffc77bc8e162ffc93555b`. The correction names `output_artifact_manifest.jsonl`, makes the final-audit
chain non-self-referential, freezes exactly 150 required field-level coverage rows and requires
the mandatory HU storage/path/inode preflight. Its new repair
root `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1` now contains
the nine contract outputs. Documents 151y/151z are the current execution result and post-repair
gate. The execution is `BLOCKED` by `blocked_by_benchmark_registry` and
`blocked_by_source_model_provenance`; the global gate remains `blocked_by_measurement_design`.
The repair root has 9 files / 203,993 bytes with inventory SHA-256
`7bce6b0d70c8069595d9c8ca96801b2eca1faf5a31973b8741e176926ef26e82`; the two prior roots remain
read-only and unchanged. No public HTTP/network, scoring, inference, weights/tokenizers, corpus,
GPU/Slurm, training, cleanup or Documents 152--154 is authorized. `ready_to_train` remains false;
no further 151x execution is authorized. Current local hashes are 151y =
`1309af278901009c22d2ee5b2438fdec886abe27cdaa60c4555dcd3af42ae6ba` and 151z =
`51e3cdda3db8a636f1308a42910c2dd76bfdca5ef0906a3a316dc639c4b984db`.

### Final evidence-gap and measurement-design authority (2026-08-08)

Document 151aa is the current read-only gap authority. It rechecked only the six existing
repair-root files on HU, found the output manifest has 7 rows (not 8), and classifies all 54
non-verified coverage fields. SHA-256:
`0a063d7d7465eb8bffdfa47a55fa95adc8420cef0a641e9d967c19ef6cdb69ae`.

Document 151ab remains the current frozen measurement-design/minimal baseline contract, now
executed once for its bounded inventory-only scope. Original pre-correction SHA-256:
`500b24f6945272cbf7ddb0f26e95449434857bcac89ed5fb5d593e3fd189b4dd`; first corrected final
SHA-256, preserved as the pre-operational-correction hash:
`3320516e674c12288d70396e31b33c059550c15365caabe9453e932e3858e2dc`; final operational correction
SHA-256:
`3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c`.
The operational correction resolves the HU/SSH versus scratch-write contradiction. A future
inventory wave may use this documented HU/SSH route only after separate authorization, mandatory
storage/path/inode preflight, an exact closed read-only source allowlist and the single new
scratch root `/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1`; HU home and all
prior evidence roots remain read-only. Public HTTP/download and recursive corpus reads are zero,
large weights are path/stat-only, and metadata/output file and byte bounds are frozen. The wave
may inventory candidate corpus evidence but may not select/materialize the primary in-domain
Turkish split; missing corpus evidence remains `blocked_by_corpus_selection_or_materialization`.
`trwiki-20260601` is control-only. `151ac/151ad` remain reserved and unused. The one authorized
inventory execution wrote exactly eight compact outputs under
`/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1`; existing sources, HU home and
prior roots remained read-only. Document 151ae is the execution result and Document 151af is the
post-execution gate. Their local SHA-256 values are
`b6a90ce5573de1c29828186dbc278c7c92c87dc1e435ef44965d0eff6f8e1601` and
`1e96a4b8d29edc50a8f151a34990c93edf3b5115dfb76416500261f8f8d817d1`.

The operational inventory passed, but the active scientific gate remains
`blocked_by_measurement_design`, with contributing blocker
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure` and `ready_to_train` are
false. No selected adaptation corpus or primary in-domain split was fabricated. No scoring,
inference, evaluation, model/tokenizer acquisition, GPU/Slurm, training, cleanup or Documents
152--154 action is authorized. Later corpus selection, scoring or measurement requires a separate
contract and explicit authorization.

### Corpus selection and materialization authority (2026-08-08)

Document 151ag is the current exact C1 reconciliation and corpus-selection decision. Its HU
inspection was limited to the six named inventory files and was read-only. It classifies
`vngrs-ai/vngrs-web-corpus` only as a **conditional primary materialization candidate**,
`trwiki-20260601` as a frozen cross-domain control, and `uonlp/CulturaX` as
`excluded_access_blocked`. vngrs is not `quality_pass`, selected, frozen for training or
`ready_to_train`. The exact C1 counts are 60 source-allowlist rows, 5 model/tokenizer rows, 6
evaluation-input rows and 17 C1 rows; the C1 status distribution is 12
`observed_existing_compact_evidence`, 2 `verified_existing_selected_manifest`, 1 `blocked`, 1
`existing_control_identity_stat_only` and 1 `existing_input_identity_stat_only`.

Document 151ah is the current frozen, **unexecuted** vngrs acquisition/materialization contract
with append-only metadata/structural and systematic-selection corrections. Its pre-correction
SHA-256 was `a8c1d1d2082ec3ae5b31ace5dc0a9506ace90f82d0f7bd1a2c1a528069ef2269`; its immediately
prior SHA-256 was `9151da7112b6d1ab9bbb3b483b202dec23449624beeddb53c23682569a0f598b`; current
SHA-256 is `18bf6d59b0552b044bec70f2f41852912c493ec098917dbd1ed87f5078eda1e8`. The bounded official
metadata pass verified immutable revision `ee5c6201ee84457a18182bfc483a7d8a7f3655ba`, 50,336,214
train rows, schema `text/corpus/original_id`, the 284-shard tree and CC BY-NC-SA 4.0 metadata.
The exact 32-path systematic midpoint set is frozen as ordinals
`00004,00013,00022,00031,00039,00048,00057,00066,00075,00084,00093,00102,00110,00119,00128,00137,00146,00155,00164,00173,00181,00190,00199,00208,00217,00226,00235,00244,00252,00261,00270,00279`;
selection payload SHA-256 is
`dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686`. Exact per-shard
LFS/SHA/footer/byte metadata, execution-time license byte hashes and sample-based tokenizer-yield
evidence remain unresolved; therefore 151ah remains `PREPARATION_BLOCKED`, and the path set is
not yet an executable download allowlist. The proposed root
`/vol/tmp2/yesildau/luna_vngrs_corpus_acquisition_materialization_v1` was not created. No public
HTTP/download, sample calibration, corpus materialization, scoring, inference, evaluation,
GPU/Slurm, training, cleanup or prior-root write is authorized. Documents 151ai/151aj remain
reserved and uncreated.

Document 151ak is the current frozen, **unexecuted** model-neutral bounded sample-calibration
contract. Its pre-correction SHA-256 was
`97a2d8a53cc8ff8390f71ddb833e9582d8b46fb9793deeb6673483a1384df012`; its immediately prior
SHA-256 was `8fc6d3dbc89f9b71e7b9e1f6ca787fce81bbcde2cf715abfa2fec54eb0b07bd5`; its previous current
SHA-256 was `eb520ece20b157ec342cd6511589907b561dd7cea5e4d68cb1cd84327c92bd8e`. The prior final
correction SHA-256 is `16f2978b10fc2b71490917ffe9ed549b574d2b364865675f0f1d900fb4320d68`; the prior
append-only final evidence-graph correction SHA-256 is
`1920f1c58d8ada250af50d1f088f5ad2fc3a15e8221f84d92f5458dab415154b`; the current
evidence-binding/sampling-schedule correction SHA-256 is
`9e35ba69fcd4885c339101e59f1d719681942571770a41023f20f6472782ea94`. The effective contract
freezes the 34-field raw record manifest, named source/footer/license/route and response evidence
artifacts with direct byte rehashing, the exact row-count-weighted midpoint schedule, request-ledger
aggregate reconciliation (`128` attempts, `100` successful-row maximum, `28` retries, `64 MiB`
total, `4 MiB` per response), contract-level final-decision validation and the self-reference-free
`output_artifact_manifest.jsonl`/`calibration_audit.json` chain. The local fixture is
`STRUCTURAL_SYNTHETIC_CONTROL`, not source or route evidence. Its exact schedule needs a computed
minimum of 373 contiguous windows and therefore fails the frozen 100-request envelope; arbitrary
windows, out-of-bounds/overlapping windows, unbound hashes or unbound near-dedup count/rate are
`BLOCKED`. Model-neutral calibration does not require tokenizer fertility; tokenizer yield/dose
adequacy belongs to later 151ah/materialization or model-specific planning. 151ak remains
`FROZEN — PREPARATION_BLOCKED — UNEXECUTED`; no route/source evidence is resolved. Focused local
verification is `30 passed, 1 skipped`; compatible verification is `260 passed, 8 skipped` with
the same three documented collection exclusions.

Document 151aq is the current bounded HU read-only operational diagnostic authority. It verified
the live/local `corpus-update` publication at `c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23`, the HU
checkout at old base `9f1755219ba003d4aaf962558b3c0512fc74f99a`, and exactly 42 status entries:
39 tracked `.D` worktree deletions plus three untracked top-level entries. The exact intersection
with the 13 paths in the published `9f17552..c1a3127` change set is zero. Its mandatory 30-second
`du -xsh` check returned exit 0, 32 stdout bytes, 0 stderr bytes and `14G`; the 30-second GNU
byte-form returned exit 0, 40 stdout bytes, 0 stderr bytes and exact `14687617024` bytes. The
read-only capacity/inode/path checks passed and the frozen 151an root remained absent. 151aq
SHA-256 is `5a48d297ef5475550df41fd7e2baace4278acf54bbfb32bbfe455909dde7dbea`. The dirty HU
checkout still keeps 151an blocked by operational access; owner-controlled reversible
reconciliation is only a separately authorized next step. Documents 151an/151ao/151ap remain
unchanged, and no source/footer access, PyArrow, executor, retry, corpus, scoring, evaluation,
GPU/Slurm, training, cleanup or Documents 152--154 action is authorized.

Documents 151ar and 151as are now the current result and post-execution gate for the one
preservation-checked 151an wave. HU was fast-forwarded once from old base
`9f1755219ba003d4aaf962558b3c0512fc74f99a` to
`c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23` only after the exact 42-entry status blob remained
unchanged (6,989 bytes, SHA-256
`71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9`, zero overlap). Mandatory
preflight and the independent PyArrow writer/parser check passed. The single 151an execution
failed closed on its first frozen direct-route request with non-retryable HTTP 302; no redirect
was followed, retries and response bytes were zero, and the root remained absent. 151ar SHA-256
is `e531443254133a3ade95fcdf004420cc8726d28f337c7171c730937de3019967`; 151as SHA-256 is
`03c603265836320b173489a6659f91916c97db7ec78ebdd7b8faf0c1122a0ceb`. The narrow operational
gate remains `blocked_by_operational_access` due route integrity and the global gate remains
`blocked_by_measurement_design`; no retry, corpus, scoring, evaluation, GPU/Slurm, training or
Documents 152--154 action is authorized.

Document 151at is the current frozen, unexecuted local/public-metadata-only Hugging Face route
correction contract (SHA-256 `d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa`). It permits zero or one
validated HTTPS 302 hop to the official `xethub.hf.co`/`cdn.hf.co` suffixes, preserves the exact
151an immutable revision/32 paths, stores only secret-safe Location metadata, strips
Authorization/Cookie on cross-host requests, and separates 121 logical attempts from 242 HTTP
hops. The local implementation/test correction is commit
`de4a14e3370326173bdf04ce33356aae7826ddda`, published by ordinary non-force push. 151at was not
executed. The one authorized 151an wave fast-forwarded HU with the 42-entry dirty state unchanged,
then failed closed on the mandatory 30-second home-usage `du` timeout before PyArrow or source
access. Document 151au records the result (SHA-256
`a83d832efa7478e86fa6bfa555cfe70d900f5284bf1bc862a8e5ca696d43fd8e`) and 151av records the gate
(SHA-256 `d25789ddece62628a9cd6913eb1cbb94306816413a5b0b7768fec85a2709944a`). The operational
gate remains `blocked_by_operational_access`; the global gate remains
`blocked_by_measurement_design`; no automatic retry or training is authorized.

Document 151aw's publication/synchronization ordering has now been followed. HU was fast-forwarded
to `de4a14e...` with its 42-entry status digest unchanged, but the mandatory home-usage preflight
timed out and the wave stopped before PyArrow/source access. A new bounded execution requires
separate explicit authorization after the preflight route is operational; merely reading this
README or Document 151aw authorizes nothing.

Document 151ax is the current frozen, unexecuted local HU storage-preflight resilience correction
(pre-clarification SHA-256 `15bdc5a7ae0e0356254c5d5ffd5ad47b091f459a52689ce4c0cb1ecc969ed22`; current final
SHA-256 `b32550966e29f3398239e7be778cb20e3344e427bbec6f664fdda062c0e9eaff`). Its primary live
home-usage command is `du -x -B1 -s /vol/fob-vol6/mi25/yesildau` with a 120-second bounded timeout;
the 30-second `du -xsh` form is diagnostic-only and does not independently block after a passing
exact-byte value below 30 GiB. It also requires bounded capacity/inode/path/root/write-policy
checks and a 120-second, manifest-hashed `>500 MiB` home-file audit with honest
PASS/BLOCKED/INCOMPLETE and pre/post reconciliation states. Top-level PASS now requires both
source-stage PASS and post-run-audit PASS; source evidence is preserved on audit failure. The
correction is local and unpushed; its narrow follow-up commit is
`92460a00ec136dd885b4940184bee9d954da9106` after predecessor
`6ff9ceb13bbf2b9a4de19ba1db7788f11d239570`;
it authorizes no HU/SSH, network, 151an/151at execution, source/footer, corpus, scoring,
evaluation, GPU/Slurm, training or later numbered documents. The next separately authorized wave
must explicitly include ordinary non-force push, preservation-checked HU fast-forward, corrected
preflight and exactly one bounded 151an/151at execution.

Documents 151ay/151az record the latest authorized wave stopping before publication. Live
`origin/corpus-update` was `2ff1cacdffd55820fdf9a8f633c2bc20bffac807`, while the expected base was
`de4a14e3370326173bdf04ce33356aae7826ddda`; therefore no push, HU/SSH, fetch, merge, preflight,
PyArrow or source/footer request was run. 151ay SHA-256 is
`a98ba8b8ddcd95742e7956c76c3ffc7364ade716ed4d0a45c8a6ca8fe352b23b`; 151az SHA-256 is
`c161a0eac7fe2c619511a30419d1ae6168c76ea83d25e4922e18cec2d968ede5`. The operational gate
remains `blocked_by_operational_access`; remote-base resolution requires separate authorization.

Documents 151ba/151bb are the revised-base follow-up result/gate. The live base
`2ff1cacdffd55820fdf9a8f633c2bc20bffac807` passed the ancestry guard (local ahead 2, remote
ahead 0); only the ordinary non-force `2ff1cac...92460a0` publication was made. HU was fetched
and fast-forwarded once with its 42-entry dirty state unchanged: 39 tracked `.D`, 3 untracked,
6,989 status bytes, SHA-256
`71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9`, and zero overlap with the
two incoming vngrs paths. Corrected 151ax preflight failed closed before PyArrow/source access
because exact-byte `du -x -B1 -s` timed out at 120 seconds; the `du -xsh` diagnostic also timed
out at 30 seconds. The mandatory post-run audit later PASSed with the root absent and 0 files/
0 bytes, but top-level result remains BLOCKED. A later read-only check observed the local and
remote branch at `210e47256a499d098da9879d7ade990527cdbe35`; it was not part of the authorized
push and no additional operation was performed. Current 151ba SHA-256 is
`d14c3b31b4d35517fbbcfaac2706b20f4108241c25f21b51c0e3157f0373ae26`; current 151bb SHA-256 is
`2ffaf1eed56a8c895dbb48715b4bab07d9e3d368363ee3a81dc7bdff2c34c606`. Operational gate remains
`blocked_by_operational_access`; global gate remains `blocked_by_measurement_design`; no automatic
retry or training is authorized.

Documents 151bc/151bd record the HU-only prewarmed retry. No push, fetch, merge or HU checkout
movement was performed, and `210e47256a499d098da9879d7ade990527cdbe35` remained out of scope.
The bounded read-only probe timed out after `30.004 s` with return code `null`, 226 stdout bytes
(spawn line only) and 0 stderr bytes, so live HEAD/status/root/manifest/exact-byte values were
not accepted from historical records. Internal preflight, PyArrow and executor invocation count
were zero; the mandatory post-run audit probe also timed out after `30.005 s` before a remote
result. 151bc SHA-256 is
`376c5e380ba1fa22262626b66b531d19f9333e168a2ffe3c86017b1218726edc`; 151bd SHA-256 is
`c9544bbe410c2d4353ef6b1f1c4c72debd269bb3122d0c0de559b46680d61683`. Operational gate remains
`blocked_by_operational_access`; global gate remains `blocked_by_measurement_design`; no automatic
retry or training is authorized.

Document 151an is the current frozen, unexecuted **execution-ready metadata/footer feasibility
only** contract. Its pre-correction SHA-256 is
`435e0c25cedd7fd8fcb70862c637040300c2d5b201bfb5fa25c2b20232e71096`; its prior corrected SHA-256
is `572a14636dfc44f23cdff5ac536838ea671a488ddcd24968097bc4942bb0d4e4`; its strict-parser
correction SHA-256 is
`e23ae18d35791e91d05f094fe7c675871214df6a9fe9714a660ae703fe84a0ac`; and its current retry/bound
correction SHA-256 is
`937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79`. It freezes the exact
32-path immutable source identity, one `parquet_footer_range` route-kind vocabulary, immutable
direct `/resolve/` routes, exclusion of Dataset Viewer `/rows`, the scratch root
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1`, seven top-level outputs, separate
full-object/LFS identity versus compact metadata-artifact hashes, a pure-Python compact-Thrift
parser for complete footer framing, two-stage trailer/exact-footer ranges, shared HEAD role
binding, explicit 429/503 and no-response retry semantics, actual response-byte binding and
`evidence/retry/` artifacts. The effective retry ceiling is `24`; nominal 32-shard accounting is
97 base artifacts plus 24 retry artifacts plus seven top-level files = 128 files/inodes within
the frozen attempt, byte, time, file and inode ceilings. Local verification is `40 passed, 2
skipped` focused and `270 passed, 9 skipped` compatible with the same three exclusions plus the
explicit independent-writer compatibility skip. The one authorized 151an wave is recorded in
Documents 151ao/151ap and is `BLOCKED` before source access. HU `corpus-update` was dirty at old
base `9f17552` with 42 status entries, while the exact reviewed three-commit chain was published
ordinary non-force to `c1a3127`; no pull was attempted because it could overwrite unrelated HU
work. The byte-form home `du` preflight also returned no parseable usage value. The frozen root was
absent, executor invocations and HTTP attempts were zero, and no remote output was created. 151ao
SHA-256 is `5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46`; 151ap SHA-256 is
`aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468`. This is not route-
unavailability evidence and does not authorize another 151an execution, source access, row
sampling, corpus materialization, scoring, evaluation or training without a new explicit request.

The effective gate remains primary `blocked_by_measurement_design` with contributing
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure` and `ready_to_train` remain
false. Existing helper scripts remain historical route tools and do not authorize 151ah execution.

### Current vngrs HU-only retry result (2026-08-12)

Document 151be's exact SHA-bound wave was authorized and executed exactly once. Connectivity,
preservation, bounded home/cache prewarm, internal preflight, independent PyArrow validation and
the 96 shard metadata/footer requests passed. The final immutable README/license request returned
HTTP 307, outside 151at's frozen 302-only redirect vocabulary, so the executor stopped fail-closed
at logical attempt 97 / HTTP hop 193. The scratch root remained absent and the post-run storage,
home, Git-status and 13-path source-hash reconciliations passed. Document 151bf records the result
(SHA-256 `e9a086f3be624ded0ac1271326ff57beefbd01b4a98dc936cb3ff6c135e1c9c5`) and Document 151bg is
the current gate (SHA-256
`80ed93e937f9fc1eda74f9ae90df76823d957688e803f92bfd9df4c17aa86d75`). The single invocation is
consumed. Any retry requires a new append-only license-route 307 semantics contract and exact user
authorization; no corpus row/full-shard access, sample calibration, materialization, GPU/Slurm,
training, cleanup or second executor invocation is authorized.

### Current M1 dose/Pareto HU result (2026-08-12)

Document 159b's exact OLMo BF16 wave completed as jobs `454283` and `454284_[0-5]`. Runtime,
BF16 parameter/gradient/AdamW-state smoke, checkpoint persistence, 252-update training and all six
cheap checkpoint evaluations passed integrity. Exact acquisition was 100% throughout, but PPL
ratios were 1.385--1.429 against the frozen 1.25 limit, so no OLMo hard suite opened and OLMo is a
valid scientific negative. Document 160 records this result (SHA-256
`9e995bc9cdff6ffa1da0e17194e050b590c2f7cbf8e2af0345672e6a425044de`).

The three-model family remains incomplete, not scientifically selected: Pythia has 6/6 cheap
gates, while Falcon has only 3/6 because evaluation tasks for checkpoints 126, 210 and 252 stopped
at the free-VRAM runtime guard before scientific evaluation. Document 161 is the current gate
(SHA-256 `eea7227ef433506755da53699af9adf30e36aa574caec22fce48f9db30224579`). Do not rerun Falcon
training or any completed evaluation. A Falcon-only clean-RTX3090 evaluation recovery and final
18/18-row summary require a new frozen exact-SHA contract and separate user authorization.

### Prepared next recovery contracts (2026-08-12)

Document 151bh freezes the vngrs license-only HTTP-307 resolve-cache repair; SHA-256
`57d8dbd0b84f5914e9b249b12d888cb1aa7c2ea6b6733197aaf117dbcb801853`. It permits a future
separately authorized wave to publish/synchronize the tested implementation and run exactly one
new metadata/footer executor invocation. Only the exact immutable README request may take one
same-origin `huggingface.co/api/resolve-cache/.../README.md` 307 hop. Shard 302 semantics and all
zero-row bounds remain unchanged. No push, HU/SSH, source request or retry is currently authorized.
The shared implementation commit is `37a7d29a182f049054483915f4ceee5bc7fdd1d4`; it is unpushed
and the compatible local suite passed 380/380.

Document 162 freezes the Falcon-only missing-evaluation recovery; SHA-256
`4ada146f01c777a2995d6bc4901e1cbaf9bae574b9d93263440fdfe9cca355fd`. It permits, only after a
new exact authorization, a 15/18-state preflight, one sequential `guppi5` RTX3090 array containing
only tasks `2,4,5` (checkpoints `126,210,252`), and one `afterok` family summary. Do not rerun
training or any completed evaluation, submit a second recovery array, relax the 20 GiB runtime
guard, or promote a model automatically.
The same unpushed commit `37a7d29a182f049054483915f4ceee5bc7fdd1d4` contains this recovery
implementation and passed the same 380/380 suite.
