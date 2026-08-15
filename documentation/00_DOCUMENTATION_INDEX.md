# 00 - Documentation Index

Last updated: 2026-08-13

Revision note (2026-08-13, next bounded recovery preparation): Document 151bk freezes the exact
vngrs response-header correction after 151bh reached completed-package validation. HTTP request
`Range` retains `bytes=...`, while HTTP response `Content-Range` is corrected to the standards
grammar `bytes START-END/TOTAL`. Its SHA-256 is
`18f9a3c65d7e006a29645bfcef2a26a3d48eb1224291bfe2ca122fafbfc6e4f8`.
Document 165 freezes an outcome-blind relocation of only missing Falcon checkpoint
`126/210/252` evaluations to local `gpu/gruenau8/gpu:rtxa6000:1`, with exact RTX A6000/CC 8.6,
40 GiB free-VRAM, `sbatch --test-only`, sequential `2,4,5%1` and dependency-closed summary gates.
Its SHA-256 is `e8e1d772ed7726e959f5ec5e24d81f1a4a3aeed2973f6aa3bbe5c22b078e9fda`.
Both implementations are prepared locally in commit `68e5be9`; the complete compatible suite
passed 382/382. Neither contract is executed or published; exact SHA-bound authorization is
required before push, HU synchronization, source requests or Slurm work.

Revision note (2026-08-12, authorized vngrs HTTP-307 retry result): Documents 151bi/151bj record
the single Document 151bh invocation. The same-origin immutable README HTTP-307 repair progressed
beyond the prior license-route blocker, but the completed-package validator rejected unreconciled
trailer/footer `Content-Range` evidence. The invocation is consumed, the execution root remains
absent, and no accepted metadata/footer package exists. Document SHA-256 values are
`0060ef1002438488a184b9951ef12ce42e34c5eb755f6fda15a81c44bdc1d8fa` and
`3e9fc4a9b9dee26515fbed5d536e75895d9217c2ceb3e71dd14ab875bb793cb8`.
Global `blocked_by_measurement_design` and corpus-materialization blockers remain unchanged.

Revision note (2026-08-12, Falcon recovery scheduler-access block): Documents 163/164 record the
authorized Document 162 wave. Both 15/18 preflights passed, but no Slurm job ID was created. The
original `gpu` partition did not contain frozen node `guppi5`; the contract-compatible partition
binding correction to `wbimlgpu` passed 100/100 local and HU focused tests, then scheduler access
failed with `User's group not permitted to use this partition`. Missing Falcon
`126/210/252` roots and the family summary remain absent; family status is still 15/18 and this is
an operational NOT-RUN, not a Falcon scientific result. Document SHA-256 values are
`55c8a8c2c9565793e2656e1a8f94a195ee6956f119df919878b10a014f6bec4d` and
`b73f13c7beca9a967488d5af2702f2ff64806924a7bdc9739f6614ef4c9876d3`.

Revision note (2026-08-11, OLMo queue relocation amendment): Document 159 execution started, but
OLMo V100 job `453301` remained `PENDING(Resources)` with a scheduler estimate near 41 hours
because every V10032GB was allocated. Document 159a freezes an outcome-blind RTX3090 FP16
relocation with memory-safe `microbatch=4`, `gradient_accumulation=125`, unchanged effective batch
500, LR, seed, update/checkpoint grid and scientific gates. It permits only state-checked
cancellation of the never-started OLMo jobs/stale summary and requires exact authorization bound
to SHA-256 `e13c2a08c482e027ab04c364306b6b62ec73897d9caca7b111a188796235b0cb`.

Revision note (2026-08-11, three-model dose/Pareto remediation plan): Document 159 is the current
frozen, unexecuted remediation contract. It preserves all three negative v3 results and unchanged
gates, and proposes one seed-42 run per model with checkpoints `42/84/126/168/210/252`. Every
checkpoint receives exact/PPL/generic evaluation; only exact+PPL passing checkpoints enter the
expensive hard-suite. No LR change, threshold relaxation, seed43, corpus or cleanup is authorized.
Execution requires exact authorization bound to Document 159's final SHA-256; Documents 160/161
are reserved for result/gate.

Revision note (2026-08-11, completed three-model 500-fact screen): Documents 157/158 record the
completed Pythia official-tokenizer/BF16 repair result and combined OLMo/Falcon/Pythia gate.
Pythia jobs `453163`--`453166` completed on `guppi5`: exact-prefix 100%, hard-suite 98.175%,
profession form-C minimum 65%, and WikiText-2 PPL ratio 16.1487x. Pythia is a valid negative
result. OLMo, Falcon and Pythia all learned the 500 facts exactly but all failed at least the
frozen profession-form robustness and retention gates; therefore the three-model screen has three
results but no selected primary model. Document 158 §2.1 binds the terminal OLMo/Falcon jobs,
absolute training/evaluation artifact paths, compact SHA-256 ledger, 51G retained shared root and
no-cleanup closure; this supersedes the progress-only OLMo/Falcon wording in Document 155.

Revision note (2026-08-11, Pythia RTX3090 BF16 preparation): Document 156b relocation reached
`guppi5` immediately. Training preflight, exact RTX3090 runtime and tokenization passed, but job
`453127` failed in optimizer smoke before training because GradScaler rejects direct FP16 parameter
gradients. No scientific result or training/evaluation namespace exists; dead downstream jobs were
cancelled. Document 156c freezes the narrow BF16/no-GradScaler compatibility repair and remains
unexecuted pending exact authorization.

Revision note (2026-08-11, Pythia RTX3090 relocation preparation): The Document 156a acquisition,
official-tokenizer and training-preflight stages passed as jobs `452895`--`452897`. Training
`452898` did not start because all three V100s were occupied; its Slurm start estimate was
13 August. `guppi5/6/7` simultaneously exposed nine idle RTX3090 cards. Document 156b freezes a
scientifically identical, runtime-fail-closed RTX3090 relocation using the already verified
tokenizer/composite manifest. It is unexecuted and requires separate exact authorization.

Revision note (2026-08-11, Pythia PAD-default retry): The exact Document 156 wave ran once.
Acquisition preflight `452542` passed and job `452543` obtained the exact official tokenizer byte,
but Transformers 5.13 inserted its `<|padding|>`/ID-1 class default and the explicit PAD assertion
failed closed before composite manifest, GPU, smoke, training or evaluation. Pending job `452544`
was cancelled. Document 156a freezes the narrow `pad_token=None` + HU `v10032gb` selector fix and
fresh retry root; its SHA-256 is
`13f2e281b13a699149a2d0cb51ee62c9395180655534e6b2c8c224fab5284429`. It is unexecuted and needs
separate exact authorization.

Revision note (2026-08-11, Pythia official-tokenizer repair): Document 156 is the frozen,
unexecuted repair contract for the Pythia candidate that previously terminated as
`NOT_RUN_MASKING_COMPATIBILITY_GATE`. It preserves the exact weight revision and all historical
v3 evidence, pins EleutherAI/Pythia's official GPT-NeoX-20B tokenizer source by immutable commit,
exact byte count and SHA-256, and proposes a fresh-root V100 FP16 tokenizer audit → smoke →
500-fact training → base/endpoint evaluation chain. Its SHA-256 is
`0e48ec4882768d92d2a88e75e8d54a7d505d95a1605b015692e31b3b9e5c8985`. Local preparation does
not authorize push, HU/SSH, tokenizer retrieval or execution; a new exact authorization is
required. Documents 157/158 are reserved for result/gate.

Revision note (2026-08-11, authorized v3 launch): Document 155 records the exact 152b-authorized
wave. Commit `f0caa05` was pushed/fast-forwarded, HU targeted tests passed 98/98 and shared
acquisition preflight passed. OLMo/Falcon passed meaningful model-native acquisition and training
preflight and are in the A100 queue. Pythia's pinned snapshot yielded a two-token tokenizer with
empty probe encodings; its pending train/eval chain was cancelled before GPU work and is
`NOT_RUN_MASKING_COMPATIBILITY_GATE`. No silent revision/tokenizer fallback is allowed.

Append-only GPU reroute note: the user cancelled the long-wait A100 DAG and requested live
free-GPU restart. Falcon is running as job `452163` on clean `guppi7` after a passing RTX3090
smoke. OLMo failed optimizer smoke twice on clean `guppi5` before training; 24 GiB is insufficient
under the frozen 10×50 decomposition. `guppi6` was excluded due foreign GPU processes. The user
then approved an isolated OLMo 5×100 retry preserving effective batch 500, BF16 and all other
scientific settings. Commit `f7b2b6d` was pushed/fast-forwarded, HU targeted tests passed 60/60,
and preflight `452173` passed. Training job `452174` nevertheless failed before scientific
training at the first AdamW multi-tensor optimizer step, approximately 69 MiB short; downstream
jobs `452175`/`452176` were cancelled. This is an operational `NOT_RUN`, not a scientific result.
The subsequently authorized `foreach=False` retry was implemented in commit `5407161`, passed
61/61 HU tests and preflight `452177`, but job `452178` showed the single-tensor Adam path still
allocating the same 784 MiB `sqrt()` temporary and failed before training; `452179`/`452180` were
cancelled. No OLMo scientific result exists at this cutoff.
The user then selected the idle V100 route. The existing Torch 2.7 wheel lacked V100 `sm_70`, so
job `452182` failed compatibility before training. A scratch-only Torch 2.6.0/CUDA 12.4 env was
installed; allocated-V100 validation `452190`, preflight `452191`, and the full FP16 optimizer
smoke passed. OLMo job `452192` is now in real 252-update training on `gruenau1` with peak smoke
allocation 29,973,358,592 bytes; downstream evaluation jobs are `452193`/`452194`. No completed
OLMo scientific result is claimed yet.

Revision note (2026-08-11, v3 storage-preflight correction): At the user's request, one bounded
read-only exact HU-home measurement completed at `14,689,423,360` bytes (approximately 13.68 GiB)
in 96.99 seconds, below the 30 GiB limit. Document 152b freezes this evidence and locally prepares
a v3-only no-home-write/scratch-routing correction that removes repeated recursive home `du` and
large-file scans from the submission/per-stage blocker path. Its SHA-256 is
`1b55a03484682e065c9eaec106f8803b9ffdecba9301e3a0261df9e6ecd154fa`. Document 152b is
unexecuted; prepared local commit `f0caa05` remains unpushed and requires a new exact authorization
for push/HU/model/Slurm/training/evaluation.

Revision note (2026-08-11, three-model v3 execution): The user explicitly authorized the exact
Document 152a wave. Implementation commit `a0eeed33c7c894b9ae05c369869d114419603e66` was pushed
ordinary non-force and preservation-checked fast-forwarded on HU. Document 153 records that the
wave then failed closed on the mandatory 120-second exact-byte HU-home `du` preflight before model
access, scratch-root creation, HU pytest and Slurm submission. The v3 root remained absent and
matching jobs were zero. Document 154 sets `blocked_by_operational_preflight`; no OLMo, Pythia or
Falcon scientific result exists and no automatic retry is authorized.

Revision note (2026-08-11, three-model 500-fact screen repair plan): Document 152 is now indexed
as the preserved historical `NATIVE ASSET GATE` block; it produced no model training/evaluation
result. Document 152a is the current `READY_FOR_EXACT_USER_AUTHORIZATION — UNEXECUTED`
model-native repair and execution plan for OLMo-2-0425-1B, Pythia-1.4B and Falcon-RW-1B. Its
SHA-256 is `411b32bedebc8f710b0d533ba7d17884d854bafe892496068ef20517d90a950a`.
It proposes independent candidate DAGs and the fresh root
`/vol/tmp2/yesildau/m1_provenance_screen_v3`; its single authorized wave is now closed by
Documents 153/154 as a pre-submission operational block.

Revision note (2026-08-09, literature/roadmap alignment): the restored
`THESIS_RELEVANT_PAPERS_MASTER_MAP_TR.md`, historical Document 60, active scientific Document 145
and bounded vngrs Document 151at have been reconciled in Document 151aw. OLMo/Pythia/Falcon remain
non-selected English-centric screening candidates and Qwen remains the multilingual positive
control. vngrs is conditional, trwiki is control-only, CulturaX is access-blocked, and the other
listed Turkish corpora remain literature/provenance candidates. The global gate remains
`blocked_by_measurement_design`; this alignment does not authorize execution or training.

Revision note (2026-08-07): external validation updated the status summary for Documents 148,
150 and 151; historical results and the uncreated state of Documents 152--154 are preserved.

Revision note (2026-08-07, bounded-audit continuation): Documents 151a--151c record the first
bounded-audit attempt and its approval-layer block; they do not contain scientific sample results.
The user later explicitly authorized only the 151a bounded HU read-only continuation. The resumed
sample result and post-resumed decision gate are recorded in Documents 151d and 151e. This does
not authorize training or create Documents 152--154.

Revision note (2026-08-07, evidence-integrity correction and externally prompted validation):
Document 151f is the current evidence-integrity correction and externally prompted validation
authority for the HU evidence timing, full SHA recomputation, sample-manifest noncompliance,
vngrs incompleteness, trwiki LID interpretation, near-dedup cap deviation, and synthetic
inventory grain. It was internally executed by the same LUNA-Worker 2 that produced 151d/151e
after an external Codex evidence review prompted the correction; it is not a genuinely independent
external review. Codex later spot-checked the core SHA values, file count, total bytes, sample
completeness, and gate interpretation. Documents 151d/151e remain historical
preliminary/provisional evidence. Document 151g is the frozen repair contract; Documents 151h and
151i are its append-only execution result and post-repair gate. The required vngrs operational
gate is closed for that repair wave, while the secondary gate remains
`blocked_by_measurement_design`; CulturaX remains `excluded_access_blocked`. No training or
Documents 152--154 are authorized.

Revision note (2026-08-07, post-repair): Document 151h records the completed vngrs-only repair
wave and Document 151i records the resulting gate. The operational closure is scope-limited; it
does not close measurement design, create a frozen global quality pass, or authorize training.

Revision note (2026-08-07, Phase-1 execution): Document 151j remains a
`SUPERSEDED_UNEXECUTED_REQUIREMENTS_DRAFT` and was not executed. The frozen 151m contract was
executed once under explicit authorization; Document 151n records the execution and Document
151o records the post-execution gate. Operational bounds and immutable-root checks PASS, but the
measurement evidence remains blocked. Documents 151n/151o are preserved historical
preliminary/provisional records. Document 151p is the current local validation and blocker
correction authority: synthetic-inventory provenance and the exact 65,717 inventory component are
closed; benchmark and source-model registries are incomplete collection/extraction from the
executed bounded wave, not public-source absence. Future alias/template/overlap definitions and
capability measurement remain unresolved. The global gate remains `blocked_by_measurement_design`;
no training or Documents 152--154 are authorized.

Revision note (2026-08-07, Document 151p correction): Document 151p is a local deterministic
validation pass by LUNA-Worker 2, not an agent-level independent external review. It preserves
151n/151o, verifies the frozen source/derived Relation V2 chain (829 versus 713 exact surface
unions) and reproduces the exact 65,717 contamination inventory. Its final SHA-256 is recorded
below. No HU, SSH, network, API, download, inference, scoring, corpus scan, GPU, Slurm or training
action occurred.

Revision note (2026-08-07, Document 151q execution-location clarification; pre-execution state,
superseded by the execution note below): Document 151q remained
**UNEXECUTED — EXECUTION_READY** and now includes a third append-only operational correction. Its
original SHA-256 is preserved as `b55499242100263e0d9adbe946679b6175268012d1c3e897298413a2af1ef60c`;
the first corrected SHA-256 is `0acf5251bea811e07b6442681ec02c7bc4fa2ea584a55e8b48cbcb704d4209e3`;
the second corrected SHA-256 is `c217f4d8395a8e3b657f96fd46f3e6443a11fcde6bbfbd6f7a8414933ccf89ee`;
the final third-correction SHA-256 is recorded below. The third correction scopes earlier no-HU/SSH
statements to the preparation/correction passes and permits only a future separately authorized
151q wave to use the documented HU route, mandatory preflight and the frozen new scratch root.
HU home, prior roots, scoring, inference, weights, corpus, Slurm/GPU and training remain forbidden.
At that pre-execution point, Documents 151r/151s remained reserved and uncreated. The global gate remains
`blocked_by_measurement_design`; no current execution or Documents 152--154 are authorized.

Revision note (2026-08-07, Document 151q bounded execution): The single explicitly authorized 151q
wave ran once and is recorded in Documents 151r and 151s. The wave failed closed on the frozen
32 MiB single-response bound for the EXAMS `with_paragraphs/test_with_para.jsonl.tar.gz` route.
The effective operational gate is therefore `blocked_by_operational_access`; the global gate
remains `blocked_by_measurement_design`. The initial report is preserved, and its stale operational
gate field is corrected only by the append-only storage-audit correction artifact under the new
scratch root. No scoring, inference, weights/tokenizer access, corpus materialization, GPU/Slurm,
training, cleanup, prior-root or home write occurred.

Revision note (2026-08-07, minimal 151q retry preparation): Document 151t is the current frozen,
unexecuted minimal registry-completion retry contract. It preserves Documents 151q/151r/151s and
the first execution root
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1` as immutable/read-only;
the new retry root
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1` was not created.
The retry is limited to the missing EXAMS `test_with_para` artifact and the three skipped public
model-card metadata responses, with a 48 MiB single-response allowance and separately frozen
request, retry, response, retained-byte, file, storage and wall-clock bounds. Documents 151u/151v
are reserved but uncreated. No retry execution, HU/SSH, network, scoring, inference, weights,
tokenizers, corpus, GPU/Slurm, training, cleanup or prior-root write occurred. The effective
operational gate remains `blocked_by_operational_access`; the global gate remains
`blocked_by_measurement_design`; `ready_to_train` remains false.

Revision note (2026-08-07, 151t Hugging Face route correction): Document 151t remains unexecuted.
Its pre-correction SHA-256 is preserved as
`eef968538b2022250803504ba1f206860c053663bb9ce74f761c3ae25c4c11cc`; the append-only correction
overrides only the three model-card `/blob/` URLs with immutable revision-pinned `/resolve/` URLs.
The later retry must retain/hash raw README bytes, record the final response URL, ordered redirect
chain and content type, and fail closed on HTML presentation/login/error pages, partial bodies or
revision/path mismatch. EXAMS scope, request order, all bounds, retry root, reconciliation rules,
prohibitions and reserved 151u/151v outputs are unchanged. Final corrected SHA-256 is recorded
below; no HU/SSH, network, retry or result/gate document creation occurred.

Revision note (2026-08-07, bounded 151t retry execution): Under one explicit authorization,
Document 151t was executed once with the required HU preflight, frozen public routes, new retry
root only, first-root read-only reconciliation and post-run storage audit. Document 151u records
the PASS result and Document 151v records the post-retry gate. The EXAMS artifact and all three
raw model-card rows completed within the revised bounds; the first root remained unchanged. The
narrow registry-completion operational blocker is closed, while the global gate remains
`blocked_by_measurement_design`; `ready_to_train` remains false. No scoring, inference,
weights/tokenizers, corpus materialization, GPU/Slurm, training, cleanup, Documents 151k/151l or
152--154 action occurred.

Revision note (2026-08-07, 151u/151v coverage correction): Document 151w is the current
coverage-matrix validation authority. Its bounded HU inspection was read-only and found that the
retry matrix contains six entity-summary rows rather than one row per required entity-field;
the first-wave matrix lacks `evidence_sha256s`, `source_revisions` and `last_checked_utc` on all
132 rows; and retry benchmark/model registries do not satisfy the frozen 27/23-field schemas.
The three raw model-card rows remain successful metadata artifacts, but are not complete model
provenance rows. Documents 151u/151v remain historical, unchanged records: their successful
EXAMS/raw-README/hash/storage facts are preserved, while their scoped coverage PASS is
`PROVISIONAL / UNSUPPORTED BY THE FROZEN COVERAGE RULE`. The narrow coverage gate is now
`BLOCKED` by `blocked_by_coverage_schema`, with contributing `blocked_by_benchmark_registry`;
the global gate remains `blocked_by_measurement_design` and `ready_to_train` remains false.
Document 151w SHA-256 is
`2b19bfbea496bb76efc4e06d24d815d2b83b06090e6ebdee6526773c5fb96de3`.
Document 151x was the frozen minimal repair contract and was executed exactly once. Its
pre-correction SHA-256 is
`a19ed3b7e15540fa2810d5f483b2015cc5badd2bd41949d8678f945d3a6fb32e`; its final protocol-correction SHA-256 is
`9c66cb95ee264d8411750d8e79aff258eaaeb4d1789ffc77bc8e162ffc93555b`. The append-only correction names `output_artifact_manifest.jsonl`, excludes
self-reference and the later final audit from that manifest, freezes the one-way final-audit
chain, requires exactly 150 required field-level coverage rows and freezes mandatory HU
storage/path/inode preflight. Its new repair root is
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1`. Documents 151y/151z
are the current execution result and post-repair gate. The single execution is `BLOCKED` by
`blocked_by_benchmark_registry` and `blocked_by_source_model_provenance`; the global gate remains
`blocked_by_measurement_design` and `ready_to_train` remains false. The repair root contains 9
files / 203,993 bytes with inventory SHA-256
`7bce6b0d70c8069595d9c8ca96801b2eca1faf5a31973b8741e176926ef26e82`; the prior roots remain
unchanged and read-only. No 151t/u/v modification, public HTTP, scoring, inference,
weights/tokenizers, corpus, GPU/Slurm, training, cleanup or Documents 152--154 action is
authorized, and no further 151x execution is authorized.

Revision note (2026-08-08, 151x execution): Under one explicit authorization, corrected frozen
151x was executed exactly once with mandatory HU preflight, immutable-input read-only access and
new-repair-root-only writes. Document 151y records the `BLOCKED` execution result and Document
151z records the post-repair gate. The 150-row schema and nine-output final-audit chain completed,
but required benchmark evidence and source-model provenance remained incomplete; no evidence was
fabricated.

Revision note (2026-08-08, 151aa gap audit): Document 151aa is the current read-only evidence-gap
authority. HU inspection of only the six existing repair-root files verified their hashes/bytes/
rows, confirmed `output_artifact_manifest.jsonl` has 7 rows, corrected 151y’s “previous eight”
narrative append-only, and enumerated all 54 non-verified fields. 151aa SHA-256 is
`0a063d7d7465eb8bffdfa47a55fa95adc8420cef0a641e9d967c19ef6cdb69ae`.

Document 151ab remains the current frozen measurement-design authority/minimal baseline contract,
now executed once for its bounded inventory-only scope. Its original pre-correction SHA-256 is
`500b24f6945272cbf7ddb0f26e95449434857bcac89ed5fb5d593e3fd189b4dd`; its first corrected final
SHA-256, preserved as the pre-operational-correction hash, is
`3320516e674c12288d70396e31b33c059550c15365caabe9453e932e3858e2dc`; its final operational
correction SHA-256 is
`3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c`. The first correction
freezes BPB, the primary in-domain Turkish held-out split, `trwiki-20260601` as cross-domain
control, the WikiText-2 token-stream hash distinction, exact M0/M1 states, both thesis estimands
and the review ledger. The second correction resolves the HU/SSH versus `/vol/tmp2` contradiction:
future inventory may use the documented HU/SSH route only after separate authorization, mandatory
storage/path/inode preflight, a closed exact read-only source allowlist and the single new scratch
root `/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1`; HU home and prior roots
remain read-only. Public HTTP/download and recursive corpus reads are zero, large weights are
path/stat-only, and compact metadata/output bounds are frozen. The wave may inventory candidate
corpus evidence but may not select/materialize the primary in-domain split; absence remains
`blocked_by_corpus_selection_or_materialization`, while `trwiki-20260601` is control-only.
151ac/151ad remain reserved and unused. The one authorized inventory execution wrote exactly eight
compact outputs under `/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1`; existing
sources, HU home and prior evidence roots remained read-only. Document 151ae is the execution
result (SHA-256 `b6a90ce5573de1c29828186dbc278c7c92c87dc1e435ef44965d0eff6f8e1601`) and Document
151af is the post-execution gate (SHA-256
`1e96a4b8d29edc50a8f151a34990c93edf3b5115dfb76416500261f8f8d817d1`). The operational inventory
passed, but 151af keeps the scientific gate `blocked_by_measurement_design` with contributing
blocker `blocked_by_corpus_selection_or_materialization`; `ready_to_measure` and `ready_to_train`
remain false. No selected adaptation corpus or primary in-domain split was fabricated, and the
inventory did not authorize training or baseline scoring.

Revision note (2026-08-08, 151ag/151ah corpus decision): Document 151ag is the current exact C1
reconciliation and corpus-selection authority. It read only the six named inventory files on HU:
60 source-allowlist rows, 5 model/tokenizer rows, 6 evaluation-input rows and 17 C1 rows. The C1
status counts are 12 `observed_existing_compact_evidence`, 2
`verified_existing_selected_manifest`, 1 `blocked`, 1 `existing_control_identity_stat_only` and
1 `existing_input_identity_stat_only`; natural identity keys have no duplicates. vngrs is only a
conditional primary materialization candidate, trwiki-20260601 is cross-domain control-only and
CulturaX is `excluded_access_blocked`. 151ag SHA-256 is
`54c9e1f8c626fb0f67a2d1f5396277304c30714074683b386ac39da3a8f22497`.

Document 151ah is the current frozen, unexecuted vngrs acquisition/materialization contract with
append-only metadata/structural and systematic-selection corrections. Its pre-correction SHA-256
was `a8c1d1d2082ec3ae5b31ace5dc0a9506ace90f82d0f7bd1a2c1a528069ef2269`; its immediately prior
SHA-256 was `9151da7112b6d1ab9bbb3b483b202dec23449624beeddb53c23682569a0f598b`; its current
SHA-256 is `18bf6d59b0552b044bec70f2f41852912c493ec098917dbd1ed87f5078eda1e8`. The bounded official
metadata pass verified immutable revision `ee5c6201ee84457a18182bfc483a7d8a7f3655ba`, 50,336,214
train rows, schema `text/corpus/original_id`, the 284-shard tree and CC BY-NC-SA 4.0 metadata.
The exact systematic midpoint path set is ordinals
`00004,00013,00022,00031,00039,00048,00057,00066,00075,00084,00093,00102,00110,00119,00128,00137,00146,00155,00164,00173,00181,00190,00199,00208,00217,00226,00235,00244,00252,00261,00270,00279`;
its selection payload SHA-256 is
`dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686`. Exact per-shard
LFS/SHA/footer/byte metadata, execution-time license byte hashes and sample-based tokenizer-yield
evidence remain unresolved; 151ah therefore remains `PREPARATION_BLOCKED`, and the path set is not
yet an executable download allowlist. The proposed root was not created. The primary gate remains
`blocked_by_measurement_design`, with contributing `blocked_by_corpus_selection_or_materialization`;
`ready_to_measure` and `ready_to_train` remain false. Documents 151ai/151aj are reserved only.
No 151ah execution, sample calibration, full-shard or corpus-row download, corpus materialization,
scoring, inference, evaluation, GPU/Slurm, training, cleanup or Documents 152--154 action is
authorized.

Document 151ak is the current frozen, unexecuted model-neutral bounded sample-calibration contract.
Its pre-correction SHA-256 was `97a2d8a53cc8ff8390f71ddb833e9582d8b46fb9793deeb6673483a1384df012`;
its immediately prior SHA-256 was `8fc6d3dbc89f9b71e7b9e1f6ca787fce81bbcde2cf715abfa2fec54eb0b07bd5`;
its previous current SHA-256 was `eb520ece20b157ec342cd6511589907b561dd7cea5e4d68cb1cd84327c92bd8e`.
The prior final correction SHA-256 is `16f2978b10fc2b71490917ffe9ed549b574d2b364865675f0f1d900fb4320d68`;
the prior append-only final evidence-graph correction SHA-256 is
`1920f1c58d8ada250af50d1f088f5ad2fc3a15e8221f84d92f5458dab415154b`; the current append-only
evidence-binding/sampling-schedule correction SHA-256 is
`9e35ba69fcd4885c339101e59f1d719681942571770a41023f20f6472782ea94`.
The effective contract freezes a 34-field raw record manifest, named source/footer/license/route
and response evidence artifacts with direct byte rehashing, the exact row-count-weighted midpoint
schedule, request-ledger aggregate reconciliation (`128` attempts, `100` successful-row maximum,
`28` retries, `64 MiB` total, `4 MiB` per response), contract-level final-decision validation and
the self-reference-free `output_artifact_manifest.jsonl`/`calibration_audit.json` chain. The local
fixture is `STRUCTURAL_SYNTHETIC_CONTROL`, not source or route evidence. Its exact schedule needs
373 contiguous windows, so it fails the frozen 100-request envelope; arbitrary windows,
out-of-bounds/overlapping windows, unbound hashes or unbound near-dedup count/rate are `BLOCKED`.
Model-neutral calibration does not require tokenizer fertility; tokenizer yield/dose adequacy belongs
to later 151ah/materialization or model-specific planning. 151ak remains
`FROZEN — PREPARATION_BLOCKED — UNEXECUTED`; local verification is `30 passed, 1 skipped` and
`260 passed, 8 skipped` after the same three collection exclusions. These checks do not authorize
route resolution or execution.

Document 151an is the current frozen, unexecuted **execution-ready metadata/footer feasibility
only** contract. Its pre-correction SHA-256 is
`435e0c25cedd7fd8fcb70862c637040300c2d5b201bfb5fa25c2b20232e71096`; its prior corrected SHA-256
is `572a14636dfc44f23cdff5ac536838ea671a488ddcd24968097bc4942bb0d4e4`; its strict-parser
correction SHA-256 is
`e23ae18d35791e91d05f094fe7c675871214df6a9fe9714a660ae703fe84a0ac`; and its current retry/bound
correction SHA-256 is
`937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79`. It freezes the exact
32-path immutable source identity, one `parquet_footer_range` route-kind vocabulary, immutable
direct `/resolve/` routes, exclusion of Dataset Viewer `/rows`, the new scratch root
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1`, seven exact top-level outputs,
separate LFS/full-object identity versus compact metadata-artifact hashes, a pure-Python
compact-Thrift parser for complete footer framing, two-stage trailer/exact-footer ranges, shared
HEAD role binding, explicit 429/503 and no-response retry semantics, actual response-byte binding
and `evidence/retry/` artifacts. The effective retry ceiling is `24`; nominal 32-shard accounting
is 97 base artifacts plus 24 retry artifacts plus seven top-level files = 128 files/inodes within
the frozen ceilings. Local verification is `40 passed, 2 skipped` focused and `270 passed, 9
skipped` compatible with the same three exclusions plus the explicit independent-writer
compatibility skip. This execution-ready status was exercised once under explicit authorization
and is recorded as `BLOCKED` before source access: the HU checkout was dirty at old base `9f17552`,
the reviewed three-commit chain was published ordinary non-force to `c1a3127`, and the byte-form
home `du` preflight was unparseable. The frozen root was not created; executor invocations,
HTTP attempts, retries, response bytes and artifacts are zero. 151ao SHA-256 is
`5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46`; 151ap SHA-256 is
`aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468`. This does not establish
route unavailability; another execution requires a new explicit authorization after safe HU
reconciliation and successful preflight.

Original pre-addendum SHA-256 of `151j_MEASUREMENT_DESIGN_CORRECTION_CONTRACT_TR.md`:
`15d43a2bd2c87802c0d1f9c20d20ac59c370af5135751ff02709b938be5e1259`

Post-addendum SHA-256 of superseded `151j_MEASUREMENT_DESIGN_CORRECTION_CONTRACT_TR.md`:
`d4253e5e1688064cde4650eddf1d5e2c86134bdad33ca0e33a4d3d444033b856`

Current local SHA-256 of frozen `151m_PHASE1_MEASUREMENT_EVIDENCE_RESOLUTION_CONTRACT_TR.md`:
`371c9c4fd2838626a731f802eec5e23666d265e4918d14a5cdf51e2c9ea881c0`

Current local SHA-256 of `151n_PHASE1_MEASUREMENT_EVIDENCE_RESOLUTION_EXECUTION_RESULT_TR.md`:
`998c4bc7bab9c275b558624a040106c31bd93ea7210f618b835aa8f91258973e`

Current local SHA-256 of `151o_PHASE1_POST_EXECUTION_DECISION_GATE_TR.md`:
`beae3c1aa20ac47994cd740f652af9c99e4d504224a1a00152c54543159682f4`

Current local SHA-256 of `151p_PHASE1_INDEPENDENT_LOCAL_VALIDATION_AND_BLOCKER_CORRECTION_TR.md`:
`9dfe3ce759aa6d257d39f5f1dc6b1b8a2ff3e5ad8d70c0667aa1c70344b6eb5c`

Current local SHA-256 of `151q_BENCHMARK_AND_SOURCE_MODEL_METADATA_REGISTRY_COMPLETION_CONTRACT_TR.md`:
pre-correction `b55499242100263e0d9adbe946679b6175268012d1c3e897298413a2af1ef60c`

Corrected append-only SHA-256:
`0acf5251bea811e07b6442681ec02c7bc4fa2ea584a55e8b48cbcb704d4209e3`

Final second-correction append-only SHA-256:
`c217f4d8395a8e3b657f96fd46f3e6443a11fcde6bbfbd6f7a8414933ccf89ee`

Final third-correction append-only SHA-256:
`f1cdfe082a78fce612d7bc53766e88dae3182ffcf52a225f2aa81e24c2491561`

Current local SHA-256 of `151g_BOUNDED_AUDIT_REPAIR_CONTRACT_TR.md`:
`eb9992af3bb4bb4fca18e0198ce772051d67e861b8b41d8298071434c5bf3b92`

Current local SHA-256 of `151r_BENCHMARK_AND_SOURCE_MODEL_METADATA_REGISTRY_EXECUTION_RESULT_TR.md`:
`09ffb44bea8711e7c9e37dd7a4c5cea93d9c277f552bdc50bc556fdf55facfe8`

Current local SHA-256 of `151s_POST_BENCHMARK_SOURCE_MODEL_METADATA_REGISTRY_DECISION_GATE_TR.md`:
`cec364cf21716a186311d243094f669b998bd2cf558a02bd21fcb3438be61950`

Pre-correction SHA-256 of `151t_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_CONTRACT_TR.md`:
`eef968538b2022250803504ba1f206860c053663bb9ce74f761c3ae25c4c11cc`

Final route-correction SHA-256 of `151t_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_CONTRACT_TR.md`:
`63951ba5543c2c803e8466d0c43e0aace9637ca1239164dc1d9f5e49ea75f46b`

Current local SHA-256 of `151u_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_EXECUTION_RESULT_TR.md`:
`579be50a33a8bc26c71b7f47969bfca4a9e30fde06172e3cbe21dfa772976909`

Current local SHA-256 of `151v_POST_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_DECISION_GATE_TR.md`:
`5f822449cd5295cee26b9f550c5883d4c897276fb0ee754b20a8540393edb871`

Current local SHA-256 of `151w_151U_151V_COVERAGE_MATRIX_VALIDATION_AND_CORRECTION_REPORT_TR.md`:
`2b19bfbea496bb76efc4e06d24d815d2b83b06090e6ebdee6526773c5fb96de3`

Current local SHA-256 of `151x_MINIMAL_COVERAGE_MATRIX_REPAIR_CONTRACT_TR.md`:
pre-correction `a19ed3b7e15540fa2810d5f483b2015cc5badd2bd41949d8678f945d3a6fb32e`; final protocol-correction
`9c66cb95ee264d8411750d8e79aff258eaaeb4d1789ffc77bc8e162ffc93555b`

Current local SHA-256 of `151y_MINIMAL_COVERAGE_MATRIX_REPAIR_EXECUTION_RESULT_TR.md`:
`1309af278901009c22d2ee5b2438fdec886abe27cdaa60c4555dcd3af42ae6ba`

Current local SHA-256 of `151z_POST_MINIMAL_COVERAGE_MATRIX_REPAIR_DECISION_GATE_TR.md`:
`51e3cdda3db8a636f1308a42910c2dd76bfdca5ef0906a3a316dc639c4b984db`

Current local SHA-256 of `151aa_FINAL_EVIDENCE_GAP_AUDIT_AND_MANIFEST_CORRECTION_TR.md`:
`0a063d7d7465eb8bffdfa47a55fa95adc8420cef0a641e9d967c19ef6cdb69ae`

Current local SHA-256 of `151ab_MEASUREMENT_DESIGN_AUTHORITY_AND_MINIMAL_BASELINE_CONTRACT_TR.md`:
original pre-correction `500b24f6945272cbf7ddb0f26e95449434857bcac89ed5fb5d593e3fd189b4dd`;
first corrected final / pre-operational-correction
`3320516e674c12288d70396e31b33c059550c15365caabe9453e932e3858e2dc`; final operational
correction `3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c`

Current local SHA-256 of `151ae_BOUNDED_HU_EVIDENCE_INPUT_INVENTORY_EXECUTION_RESULT_TR.md`:
`b6a90ce5573de1c29828186dbc278c7c92c87dc1e435ef44965d0eff6f8e1601`

Current local SHA-256 of `151af_BOUNDED_HU_EVIDENCE_INPUT_INVENTORY_POST_EXECUTION_GATE_TR.md`:
`1e96a4b8d29edc50a8f151a34990c93edf3b5115dfb76416500261f8f8d817d1`

Current local SHA-256 of `151ag_CORPUS_SELECTION_DECISION_AND_C1_RECONCILIATION_TR.md`:
`54c9e1f8c626fb0f67a2d1f5396277304c30714074683b386ac39da3a8f22497`

Pre-correction SHA-256 of `151ah_BOUNDED_VNGRS_CORPUS_ACQUISITION_MATERIALIZATION_CONTRACT_TR.md`:
`a8c1d1d2082ec3ae5b31ace5dc0a9506ace90f82d0f7bd1a2c1a528069ef2269`

Current local SHA-256 of corrected `151ah_BOUNDED_VNGRS_CORPUS_ACQUISITION_MATERIALIZATION_CONTRACT_TR.md`:
`9151da7112b6d1ab9bbb3b483b202dec23449624beeddb53c23682569a0f598b`

This folder is the ordered documentation home for the thesis implementation project.
Use the numeric prefix as the reading order. Use the date inside each document for recency.

**Current source order:** Read `100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md` after `AGENTS.md`
for the historical master synthesis and its dated corrections. For the now-completed 2,500-fact
M2/M3 family, Document 133 section 14 and Document 136 sections 21--24 supersede the earlier HOLD
statements. Documents 138 and 139 are the current post-M2/M3 milestone synthesis and independent
next-action plan. Document 140a is the completed independent, read-only verification of the raw HU
evidence and frozen gate. Earlier numbered reports remain the scientific evidence record.

Following the 6 August 2026 supervisor discussion, read
`144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md` for the corrected Exposé interpretation,
the preserved status of the completed Wikipedia-only Qwen pilot, and the shift from score-driven
overengineering to literature-motivated experimental design. Then read
`145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md` for the current model-provenance,
Turkish-corpus, capability-evaluation, and phased M2-A/M2-B research route. Documents 144--145 do
not authorize a new training family; they define the audits and frozen contracts required before
one can be opened.

For the comprehensive literature synthesis use `THESIS_RELEVANT_PAPERS_MASTER_MAP_TR.md`; it is a
living thesis-writing/research map, not an execution contract. Read Document 60 only as the
historical July roadmap plus its 9 August pointer. Document 151aw is the current reconciliation of
those two files with Document 145 and the bounded 151at route state.

For the detailed, directly executable read-only handoff for the next AI worker, read
`146_LUNA_WORKER_2_DETAILED_RESEARCH_AND_AUDIT_HANDOFF_TR.md`. It expands Documents 144--145 into
WP0--WP5, gives the exact historical reading chain, reserves Documents 147--151 as research/audit
deliverables, and explicitly prohibits HU access, training, large downloads, and artifact
mutation. It does not expand the scientific authorization boundary.

Documents 147--151 are the LUNA-Worker 2 read-only evidence package dated 7 August 2026. The
original 147--151 research package remains historical context, while the bounded-audit continuation
authority is now the append-only chain 151d--151x. Documents 151d and 151e are historical
preliminary/provisional evidence. Document 151f is the evidence-integrity correction and
externally prompted validation authority; Document 151g is the frozen repair contract; Documents
151h and 151i are the completed vngrs repair result and post-repair gate. Document 151j is a
superseded unexecuted requirements draft; Document 151m is the frozen contract executed once,
while Documents 151n/151o are historical preliminary/provisional Phase-1 result and gate records
and 151p is the current local correction authority. Document 151q is the frozen
benchmark/source-model metadata registry contract with three append-only corrections and was
executed once under explicit authorization. Documents 151r/151s preserve that execution result
and post-execution gate; the fixed EXAMS response bound failure remains their historical result.
Document 151t was then executed once under a separately authorized revised-bound retry. Documents
151u/151v preserve its execution result and post-retry gate. Document 151w subsequently found
that their six-row coverage PASS is unsupported by the frozen per-entity-field rule; Document
151x was then executed exactly once and Documents 151y/151z now preserve its execution result and
post-repair gate. The narrow repair gate is `BLOCKED` by `blocked_by_benchmark_registry` and
`blocked_by_source_model_provenance`; the global gate remains `blocked_by_measurement_design`. The
historical vngrs 10,000-record sample-access subgate is closed; the later immutable
route/footer/byte subgate is separate and remains operationally blocked after the 302 result.
Synthetic provenance and the exact 65,717 inventory-reproduction
component are closed by 151p. Benchmark scoring is unconditionally forbidden. Future
alias/template/overlap definitions and capability measurement remain unresolved. CulturaX remains
`excluded_access_blocked`. HU home and prior roots remain read-only. No training, inference,
weights, corpus, GPU/Slurm, cleanup, Documents 151k/151l or 152--154 action is authorized.

For the bounded-audit continuation state, read the following append-only records after the
initial 147--151 package described above:

- `151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md` — frozen bounded
  model-metadata and corpus-sample audit contract;
- `151b_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_RESULT_TR.md` — first execution attempt,
  stopped in the approval layer before the HU command ran;
- `151c_POST_AUDIT_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md` — decision gate for that
  operationally blocked attempt;
- `151d_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_RESUMED_RESULT_TR.md` — later
  user-authorized bounded continuation with actual sample metrics;
- `151e_POST_RESUMED_AUDIT_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md` — post-resumed model,
  corpus, and measurement gate.
- `151f_BOUNDED_AUDIT_INDEPENDENT_VALIDATION_AND_CORRECTION_REPORT_TR.md` — evidence-integrity
  correction and externally prompted validation of the provisional resumed result/gate; the
  filename is retained for link stability, but the report is not agent-level independent review;
- `151g_BOUNDED_AUDIT_REPAIR_CONTRACT_TR.md` — frozen minimal repair contract; its execution
  result is recorded separately and the contract itself remains unchanged;
- `151h_BOUNDED_AUDIT_REPAIR_WAVE_EXECUTION_RESULT_TR.md` — completed vngrs-only repair-wave
  execution result;
- `151i_BOUNDED_AUDIT_POST_REPAIR_DECISION_GATE_TR.md` — post-repair decision gate; operational
  vngrs access is closed, measurement design remains blocked;
- `151j_MEASUREMENT_DESIGN_CORRECTION_CONTRACT_TR.md` — superseded unexecuted measurement-design
  requirements draft preserved by append-only note; original and post-addendum SHA-256 values are
  recorded above. It does not authorize execution.
- `151m_PHASE1_MEASUREMENT_EVIDENCE_RESOLUTION_CONTRACT_TR.md` — frozen bounded Phase-1 contract;
  its SHA-256 is recorded above and it was executed once.
- `151n_PHASE1_MEASUREMENT_EVIDENCE_RESOLUTION_EXECUTION_RESULT_TR.md` — execution result,
  request/storage ledgers, corrected synthetic grain and preserved limitations.
- `151o_PHASE1_POST_EXECUTION_DECISION_GATE_TR.md` — post-execution gate; operational checks PASS,
  measurement evidence remains blocked.
- `151p_PHASE1_INDEPENDENT_LOCAL_VALIDATION_AND_BLOCKER_CORRECTION_TR.md` — current local
  correction authority; closes the synthetic provenance and exact 65,717 inventory components,
  while preserving the remaining measurement-design blockers.
- `151q_BENCHMARK_AND_SOURCE_MODEL_METADATA_REGISTRY_COMPLETION_CONTRACT_TR.md` — frozen
  metadata-registry contract with three append-only corrections; original, first, second and final
  SHA-256 values are recorded above. It was executed once; its result and gate are Documents 151r
  and 151s. Benchmark scoring remains forbidden.
- `151r_BENCHMARK_AND_SOURCE_MODEL_METADATA_REGISTRY_EXECUTION_RESULT_TR.md` — bounded 151q
  execution result; fail-closed on the EXAMS single-response bound with immutable-root and
  post-run storage evidence.
- `151s_POST_BENCHMARK_SOURCE_MODEL_METADATA_REGISTRY_DECISION_GATE_TR.md` — post-execution gate;
  operational access remains blocked and the global measurement-design gate remains open.
- `151t_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_CONTRACT_TR.md` — frozen minimal retry contract;
  executed once under explicit authorization, with its `/resolve/` route correction,
  pre-correction hash and final SHA-256 recorded above.
- `151u_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_EXECUTION_RESULT_TR.md` — bounded 151t execution
  result; PASS for the exact EXAMS/model-card registry scope with request/file/hash manifests and
  post-run storage audit.
- `151v_POST_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_DECISION_GATE_TR.md` — post-retry decision
  gate; preserved historical result whose six-row coverage PASS is superseded by 151w's
  frozen-schema correction.
- `151w_151U_151V_COVERAGE_MATRIX_VALIDATION_AND_CORRECTION_REPORT_TR.md` — current bounded
  read-only coverage validation authority; 151u/151v coverage PASS is provisional/unsupported
  by the frozen per-entity-field rule.
- `151x_MINIMAL_COVERAGE_MATRIX_REPAIR_CONTRACT_TR.md` — frozen minimal coverage repair contract,
  executed exactly once; its final SHA-256 is recorded above.
- `151y_MINIMAL_COVERAGE_MATRIX_REPAIR_EXECUTION_RESULT_TR.md` — current 151x execution result;
  schema-complete but evidence-incomplete, therefore `BLOCKED`.
- `151z_POST_MINIMAL_COVERAGE_MATRIX_REPAIR_DECISION_GATE_TR.md` — current post-repair decision
  gate; preserves `blocked_by_benchmark_registry`, `blocked_by_source_model_provenance` and the
  global `blocked_by_measurement_design` gate.
- `151aa_FINAL_EVIDENCE_GAP_AUDIT_AND_MANIFEST_CORRECTION_TR.md` — current six-file read-only
  evidence-gap authority; corrects the seven-row manifest narrative and classifies all 54
  non-verified fields.
- `151ab_MEASUREMENT_DESIGN_AUTHORITY_AND_MINIMAL_BASELINE_CONTRACT_TR.md` — current frozen,
  executed-once inventory authority with append-only BPB/held-out/state/estimand/review-ledger and
  operational HU/SSH/allowlist/corpus-gate corrections. Its eight-output inventory result is
  recorded in 151ae; the post-execution scientific gate is recorded in 151af.
- `151ae_BOUNDED_HU_EVIDENCE_INPUT_INVENTORY_EXECUTION_RESULT_TR.md` — one authorized bounded HU
  inventory result; operational inventory PASS, scientific status BLOCKED.
- `151af_BOUNDED_HU_EVIDENCE_INPUT_INVENTORY_POST_EXECUTION_GATE_TR.md` — post-inventory gate;
  primary `blocked_by_measurement_design`, contributing `blocked_by_corpus_selection_or_materialization`.
- `151ag_CORPUS_SELECTION_DECISION_AND_C1_RECONCILIATION_TR.md` — current exact six-file C1
  reconciliation and conditional corpus-selection decision; vngrs candidate, trwiki control,
  CulturaX access-blocked.
- `151ah_BOUNDED_VNGRS_CORPUS_ACQUISITION_MATERIALIZATION_CONTRACT_TR.md` — current frozen,
  append-only corrected, unexecuted and `PREPARATION_BLOCKED` vngrs contract; its candidate
  domain is bounded to at most 32 whole shards, while 151ai/151aj remain reserved and uncreated.
- `151ak_BOUNDED_VNGRS_SAMPLE_CALIBRATION_CONTRACT_TR.md` — current frozen, append-only corrected,
  unexecuted and `PREPARATION_BLOCKED` model-neutral sample-calibration contract; current SHA-256
  `9e35ba69fcd4885c339101e59f1d719681942571770a41023f20f6472782ea94`; prior evidence-graph
  SHA-256 `1920f1c58d8ada250af50d1f088f5ad2fc3a15e8221f84d92f5458dab415154b`; 151al/151am remain
  reserved and uncreated.
- `151an_BOUNDED_VNGRS_ROUTE_FOOTER_BYTE_AND_SAMPLING_SCHEDULE_EVIDENCE_RESOLUTION_CONTRACT_TR.md`
  — current frozen, unexecuted and **execution-ready only for bounded metadata/footer feasibility**;
  pre-correction SHA-256 `435e0c25cedd7fd8fcb70862c637040300c2d5b201bfb5fa25c2b20232e71096`, prior
  corrected SHA-256 `572a14636dfc44f23cdff5ac536838ea671a488ddcd24968097bc4942bb0d4e4`, strict-parser
  correction SHA-256 `e23ae18d35791e91d05f094fe7c675871214df6a9fe9714a660ae703fe84a0ac`, current
  retry/bound correction SHA-256
  `937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79`; exact root, direct
  routes, one route-kind vocabulary, complete-footer parser, two-stage ranges, shared HEAD,
  429/503/no-response retry semantics, 24-retry bound, response-byte bindings, canonical
  manifest and final audit are frozen; the single authorized wave is recorded in
  `151ao_BOUNDED_VNGRS_METADATA_FOOTER_EXECUTION_RESULT_TR.md` (SHA-256
  `5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46`) and
  `151ap_POST_BOUNDED_VNGRS_METADATA_FOOTER_EXECUTION_GATE_TR.md` (SHA-256
  `aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468`).
- `151ao_BOUNDED_VNGRS_METADATA_FOOTER_EXECUTION_RESULT_TR.md` — one authorized 151an wave;
  `BLOCKED` before source access because HU synchronization and byte-parsable preflight failed.
- `151ap_POST_BOUNDED_VNGRS_METADATA_FOOTER_EXECUTION_GATE_TR.md` — post-wave gate;
  operational `blocked_by_operational_access`, global `blocked_by_measurement_design`.
- `151aq_BOUNDED_HU_GIT_STATUS_AND_DU_PREFLIGHT_DIAGNOSTIC_TR.md` — current bounded HU
  source-read-only operational diagnostic (SHA-256
  `5a48d297ef5475550df41fd7e2baace4278acf54bbfb32bbfe455909dde7dbea`); exactly 42 HU status
  entries (`39 .D` tracked deletions plus `3 ?` untracked top-level entries), zero overlap with
  the published 13-path `9f17552..c1a3127` change set, successful 30-second human-size and
  byte-form `du` evidence (`14G` and `14687617024` bytes), and absent 151an root. The dirty HU
  checkout still leaves 151an `blocked_by_operational_access`; no new execution is authorized.
- `151ar_BOUNDED_VNGRS_METADATA_FOOTER_RETRY_EXECUTION_RESULT_TR.md` — one authorized
  preservation-checked 151an execution after exactly one fetch and one `merge --ff-only`; preflight
  and independent PyArrow self-check passed, but the first frozen direct route returned HTTP 302.
  Result `BLOCKED`, no redirect/retry/response artifact, root absent. SHA-256
  `e531443254133a3ade95fcdf004420cc8726d28f337c7171c730937de3019967`.
- `151as_POST_BOUNDED_VNGRS_METADATA_FOOTER_RETRY_GATE_TR.md` — post-execution gate;
  route-integrity/operational `BLOCKED`, global `blocked_by_measurement_design`. SHA-256
  `03c603265836320b173489a6659f91916c97db7ec78ebdd7b8faf0c1122a0ceb`.
- `151at_BOUNDED_HUGGINGFACE_CDN_REDIRECT_SEMANTICS_CORRECTION_CONTRACT_TR.md` — current
  frozen, unexecuted local/public-metadata-only route correction. It preserves 151an’s exact
  immutable revision and 32 paths; permits zero or one validated HTTPS 302 hop only to the
  official `xethub.hf.co`/`cdn.hf.co` suffixes; redacts signed Location values; separates 121
  logical request attempts from at most 242 physical HTTP hops; and keeps the existing 64 MiB,
  4 MiB, 128-file/inode and 7,200-second bounds. Local implementation/test follow-up commit is
  `de4a14e3370326173bdf04ce33356aae7826ddda` (published by ordinary non-force push). Document 151at SHA-256:
  `d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa`.
- `151au_BOUNDED_VNGRS_METADATA_FOOTER_REDIRECT_EXECUTION_RESULT_TR.md` — one authorized
  publication/synchronization attempt for 151an/151at. HU fast-forwarded to `de4a14e...` with
  the 42-entry status digest unchanged, but the mandatory 30-second home-usage `du` timed out
  before PyArrow/source access; result `BLOCKED`. SHA-256:
  `a83d832efa7478e86fa6bfa555cfe70d900f5284bf1bc862a8e5ca696d43fd8e`.
- `151av_POST_BOUNDED_VNGRS_METADATA_FOOTER_REDIRECT_EXECUTION_GATE_TR.md` — post-wave gate;
  primary `blocked_by_operational_access` due mandatory preflight timeout, global
  `blocked_by_measurement_design`. SHA-256:
  `d25789ddece62628a9cd6913eb1cbb94306816413a5b0b7768fec85a2709944a`.
- `151aw_LITERATURE_MODEL_CORPUS_AND_M2A_M2B_ROADMAP_ALIGNMENT_TR.md` — current documentation-only
  authority reconciliation. It separates completed Qwen evidence, model screening roles, corpus
  evidence levels, the active M2-A/M2-B sequence and 151at's narrow operational role. It also
  records that any future corrected route wave must explicitly include ordinary publication and
  preservation-checked HU synchronization before execution. No HU/network/training authority.
  SHA-256: `d28cf560dc8ee3eba0ca435d81df2651f88d30ef6f412f1b83e8c4bd0b6255a8`.
- `151ax_HU_STORAGE_PREFLIGHT_RESILIENCE_CORRECTION_CONTRACT_TR.md` — current frozen, unexecuted
  local storage-preflight correction. It makes exact-byte `du -x -B1 -s` with a 120-second bound
  primary, keeps `du -xsh` as a non-blocking diagnostic when exact-byte usage is below 30 GiB,
  requires bounded capacity/inode/path/root and HU-write-prohibition checks, and freezes a
  manifest-hashed bounded `>500 MiB` home-file audit with PASS/BLOCKED/INCOMPLETE and pre/post
  reconciliation. Its pre-clarification SHA-256 is
  `15bdc5a7ae0e0356254c5d5ffd5ad47b091f459a52689ce4c0cb1ecc9699ed22`; current final SHA-256 is
  `b32550966e29f3398239e7be778cb20e3344e427bbec6f664fdda062c0e9eaff`. Top-level PASS is now
  bound to source-stage PASS and post-run-audit PASS, with source evidence preserved on audit
  BLOCKED/INCOMPLETE. Local implementation/test follow-up commit (unpushed):
  `92460a00ec136dd885b4940184bee9d954da9106` (after predecessor
  `6ff9ceb13bbf2b9a4de19ba1db7788f11d239570`).
  It does not authorize HU/network, source/footer access, 151an/151at execution, corpus,
  calibration, materialization, scoring, evaluation, GPU/Slurm, training or Documents 152--154.
- `151ay_BOUNDED_VNGRS_METADATA_FOOTER_REDIRECT_EXECUTION_RESULT_TR.md` — latest authorized
  execution result, `BLOCKED` before publication because live `origin/corpus-update` was
  `2ff1cacdffd55820fdf9a8f633c2bc20bffac807` instead of expected base
  `de4a14e3370326173bdf04ce33356aae7826ddda`; no HU/source execution occurred. SHA-256:
  `a98ba8b8ddcd95742e7956c76c3ffc7364ade716ed4d0a45c8a6ca8fe352b23b`.
- `151az_POST_BOUNDED_VNGRS_METADATA_FOOTER_REDIRECT_EXECUTION_GATE_TR.md` — post-wave gate;
  publication and operational gates blocked, global gate remains `blocked_by_measurement_design`.
  SHA-256: `c161a0eac7fe2c619511a30419d1ae6168c76ea83d25e4922e18cec2d968ede5`.

- `151ba_BOUNDED_VNGRS_METADATA_FOOTER_REDIRECT_REVISED_BASE_EXECUTION_RESULT_TR.md` — revised-base
  execution result. Remote base/ancestry, ordinary non-force publication, preservation-checked
  HU fast-forward and zero-overlap guards passed. The corrected 151ax exact-byte preflight
  timed out at 120 seconds (diagnostic `du -xsh` also timed out at 30 seconds), so PyArrow and
  the executor were not invoked; post-run audit PASSed with an absent 0-file/0-byte root.
  Result is `BLOCKED`. An append-only post-wave note records a later read-only observation that
  local/remote had moved to `210e47256a499d098da9879d7ade990527cdbe35`; no additional push or
  execution was performed. Current SHA-256:
  `d14c3b31b4d35517fbbcfaac2706b20f4108241c25f21b51c0e3157f0373ae26`.
- `151bb_POST_BOUNDED_VNGRS_METADATA_FOOTER_REDIRECT_REVISED_BASE_EXECUTION_GATE_TR.md` —
  post-execution decision gate for the revised-base wave. Operational gate remains
  `blocked_by_operational_access`; global gate remains `blocked_by_measurement_design`;
  `ready_to_measure` and `ready_to_train` remain false. The same post-wave movement is recorded
  without changing the gate. Current SHA-256:
  `2ffaf1eed56a8c895dbb48715b4bab07d9e3d368363ee3a81dc7bdff2c34c606`.

- `151bc_BOUNDED_VNGRS_METADATA_FOOTER_PREWARMED_HU_ONLY_EXECUTION_RETRY_RESULT_TR.md` —
  HU-only retry result. No push/fetch/merge or HU movement occurred. Bounded SSH read-only
  connectivity timed out before live HEAD/status/root/manifest/exact-byte evidence could be
  returned; internal preflight, PyArrow and executor were not run. Post-run audit connection was
  also incomplete. Result is `BLOCKED`; SHA-256:
  `376c5e380ba1fa22262626b66b531d19f9333e168a2ffe3c86017b1218726edc`.
- `151bd_POST_BOUNDED_VNGRS_METADATA_FOOTER_PREWARMED_HU_ONLY_EXECUTION_RETRY_GATE_TR.md` —
  post-retry gate. Operational gate remains `blocked_by_operational_access`; global gate remains
  `blocked_by_measurement_design`; `ready_to_measure` and `ready_to_train` remain false. SHA-256:
  `c9544bbe410c2d4353ef6b1f1c4c72debd269bb3122d0c0de559b46680d61683`.

The 151a--151c records alone are not a scientific sample-result package. The resumed package in
151d--151e remains historical preliminary/provisional evidence. The historical vngrs sample-access
subgate is closed by 151h/151i; this does not close the later 151an/151at immutable
route/footer/byte subgate. Document 151j is superseded and unexecuted; 151m is frozen and
executed once; 151n/151o remain preserved preliminary/provisional result and gate records; and
151p is the current local correction authority. Document 151q is the frozen contract executed once;
151r/151s are the preserved result and gate records; 151t is the frozen retry contract executed
once; 151u/151v are its result and post-retry gate; 151w/151x/151y/151z/151aa/151ab remain
chronological coverage and measurement-design authorities; and 151at is the current local
Hugging Face redirect correction authority. The narrow retry operational gate is PASS, but the
later 151an route execution remains `blocked_by_operational_access` after the observed direct-route
302; the global gate remains `blocked_by_measurement_design` because overlap/alias definitions,
capability measurement and other scientific blockers remain incomplete. Documents 151au/151av,
151ai/151aj, 151k/151l and 152--154 remain uncreated and unauthorized; no scoring, inference,
training or readiness is authorized.

For a Turkish, supervisor-facing synthesis of the complete project history and current
scientific interpretation, read `78_SUPERVISOR_BRIEFING_TR.md` after the chronological reports.

For the current executable handoff that converts Max's post-meeting questions into controlled
experiments required before M2, read `93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md`.

For the completed Phase 0 plus first frozen-checkpoint WP1A/WP2/WP4 wave, read
`94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md`.

For the completed WP1B subject-form counterbalance and swap replication, including the failed
crossed-form robustness gate, read `95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md`.

For the completed WP3 four-relation joint-capture control, including its exhaustive fixture audit,
frozen Stage A contract, HU preflight, results, and job ledger, read
`96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md`.

For the completed WP5 controlled learning-rate sweep, replicated EOS-supervision ablation, and
selected Pareto recipe, read
`97_PRE_M2_DRIFT_ABLATION_REPORT.md`.

For the completed Max-question audit, reconciliation of the pilot and canonical 5,000-subject
design, final HOLD decision, and ordered work required before M2, read
`98_PRE_M2_FINAL_DECISION.md`.

Document 99 is intentionally unused. Document 100 is the active master handoff; its 28 July
operational correction directs the Qwen-scale/SmolLM workstream to Documents 122--125.

For a Turkish, agent-oriented audit that compares the plans in Documents 98 and 100 with all
recorded work through Document 120, read
`121_PLAN_EXECUTION_AUDIT_98_TO_120_TR.md`. It is a synthesis; Document 100 remains the current
operational authority.

For the active Qwen confirmation and SmolLM `lambda=0` matched-control plan, read
`125_QWEN_CONFIRMATION_AND_SMOLLM_MATCHED_CONTROL_EXECUTION_PLAN.md` together with Documents
123 and 124.

For the 2,500-fact Qwen M2/M3 execution handoff and its append-only execution closure, read
`133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md`. For the latest GPU execution blocker,
failed smoke-attempt ledger, loader corrections, and offline baseline-wave preparation, read
`134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md`. Document 133 records the frozen
scientific plan and §14 closes the completed family; Document 136 is the latest operational and
result authority.

For the frozen M2/M3 contract, materialization, smoke, and completed four-run principal training
ledger, read `135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md`. For the complete 96/96
endpoint evaluation, retry ledger, aggregate metrics, frozen gate, and pre-M2/M3 closure audit,
read `136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md`.

For the current post-M2/M3 milestone synthesis and the precise scientific interpretation of the
completed negative/inconclusive primary result, read
`138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md`. For the ordered work that
may proceed independently of future supervisor feedback, read
`139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md`. Document 139 authorizes evidence review,
exploratory analysis, documentation alignment, and artifact closure only; it does not authorize a
new training family. The completed, independent read-only review and its issue ledger are recorded
in `140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md`; its `PASS WITH CONCERNS` verdict confirms the
frozen conclusion while retaining two minor artifact-closure concerns. Document 143 records the
completed model-only endpoint retention freeze, source/retained hashes, and post-freeze storage
audit.

For the detailed completion ledger of the Qwen seed-43 and SmolLM treatment/control training wave,
read `126_QWEN_SEED43_AND_SMOLLM_TRAINING_COMPLETION_REPORT.md`.

For the replicated Qwen scale result and current SmolLM lambda-0.25 status, read
`127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md`.

For the user-authorized, bounded SmolLM 100-subject/500-fact prompt-consistency remediation that
follows the completed contrastive branch, read
`128_SMOLLM_500_FACT_PROMPT_CONSISTENCY_REMEDIATION_PLAN.md`.

For the current, detailed external-collaborator handoff through the completed Qwen replication and
SmolLM remediation, read
`129_EXTERNAL_COLLABORATOR_HANDOFF_QWEN_SMOLLM_AND_TURKISH_STAGE_TR.md`. It distinguishes the
replicated intermediate-scale English M1 result from the still-unopened Turkish M2/M3 causal
stages and lists the precise decisions still required.

For the comprehensive milestone synthesis of the complete project history, attempted methods,
positive and negative results, methodological differences, current evidence, and provisional
supervisor-facing forward plan, read
`130_COMPLETE_PROJECT_HISTORY_METHODS_RESULTS_AND_FORWARD_PLAN_EN.md`. This is the English master
version. Its Turkish companion is
`130_COMPLETE_PROJECT_HISTORY_METHODS_RESULTS_AND_FORWARD_PLAN_TR.md`. These are synthesis and
briefing documents; they do not authorize a new experiment or supersede Document 100.

For the completed first form-generalization remediation, its failed seed-42 result, and the current
canonical-plus-form-diversity follow-up contract, read Documents 101, 102, and 103 respectively.

For a collaborator-friendly narrative of the complete project, the M1--M3 causal design, major
failures and corrections, Documents 101--108, PPL-threshold rationale, current HOLD, and next work,
read `PROJECT_HANDOFF_AND_COMPLETE_PROGRESS_OVERVIEW.md` after Document 100.

## Reading Order

1. `00_DOCUMENTATION_INDEX.md`
   - Start here.
   - Explains document order, ownership, and how new documentation should be added.

2. `01_PROJECT_STATUS_AND_NEXT_STEPS.md`
   - Historical consolidated project state through its recorded update date.
   - Consolidates the early handoff, Notion export, expose, commit history, artifact manifests,
     readiness audit, and then-current next steps; Document 100 now supersedes its status claims.

3. `02_AGENT_ROSTER.md`
   - Defines the standing agent roles.
   - Explains each agent's ownership boundary and expected deliverables.

4. `03_INITIAL_AGENT_REPORTS.md`
   - First coordination pass from the spawned agents.
   - Captures each agent's readiness findings, risks, and documentation ownership.

5. `04_M0_BASELINE_RUN_REPORT.md`
   - Direct-prompt M0 baseline run report.
   - Records Slurm job, run directory, metrics, and interpretation.

6. `05_M0_QA_MATCHED_BASELINE_REPORT.md`
   - QA-matched M0 baseline run report.
   - Confirms that the QA scaffold does not make base GPT-2 retrieve synthetic facts.

7. `06_M1_FACT_ACQUISITION_RESEARCH_NOTES.md`
   - Paper and web-source review for M1 English fact acquisition.
   - Extracts GPT-2/continued-pretraining hyperparameter evidence and first M1 recommendations.

8. `07_M1_FACT_ACQUISITION_PLAN.md`
   - Executable M1 pilot plan.
   - Lists training configs, Slurm command, job protocol, outputs, and checkpoint selection rule.

9. `08_M1_PILOT_LR5E-5_EP1_RUN_REPORT.md`
   - First M1 pilot run report.
   - Tracks Slurm job 378783, run directory, queue/log checks, and final metrics when complete.

10. `09_M1_CHECKPOINT_EVALUATION_REPORT.md`
   - English direct and QA-matched checkpoint evaluation for the first M1 pilot.
   - Records checkpoint metrics and learned-fact gate interpretation.

11. `10_M1_PILOT_LR1E-4_EP1_RUN_REPORT.md`
   - Second M1 pilot run report.
   - Tracks LR 1e-4 / 1 epoch training, checkpoint evaluation, and interpretation.

12. `11_M1_PILOT_LR5E-5_EP3_RUN_REPORT.md`
   - Third M1 pilot run report.
   - Tracks LR 5e-5 / 3 epoch training, submitted checkpoint evaluation jobs, and final outcome.

13. `12_M1_SMOLLM2_360M_PILOT_RUN_REPORT.md`
   - First non-GPT-2 M1 pilot run report.
   - Tracks SmolLM2-360M 1-epoch training and checkpoint evaluation against the same English gate.

14. `13_M1_R1_STRONGER_REPETITION_PLAN.md`
   - First recipe-change plan after the GPT-2 and SmolLM pilots.
   - Defines the QA-mixed and repetition-boosted English training dataset and launch config.

15. `14_M1_R1_RUN_REPORT.md`
   - Execution report for the first recipe-change run on GPT-2.
   - Records the corrected checkpoint-evaluation retry, final English-only metrics, and outcome.

16. `15_M1_R2_BIGGER_MODEL_QAMIX_PLAN.md`
   - Next M1 escalation plan after R1 failed.
   - Keeps the stronger QA-mixed recipe and moves to SmolLM2-360M.

17. `16_M1_R2_SMOLLM2_QAMIX_RUN_REPORT.md`
   - Execution report for the first combined bigger-model plus QA-mixed recipe run.
   - Records SmolLM2-360M R2 training, checkpoint evaluation, and learned-fact gate outcome.

18. `17_M1_R3_SMOLLM2_QAMIX_EP3_RUN_REPORT.md`
   - Execution report for the first higher-exposure continuation of the SmolLM2 QA-mixed branch.
   - Records 3-epoch training, checkpoint evaluation, and the conclusion that more exposure alone did not solve M1.

19. `18_M1_R4_SMOLLM2_1_7B_QAMIX_RUN_REPORT.md`
   - Execution report for the first larger-model follow-up after R3.
   - Records the SmolLM2-1.7B QA-mixed pilot, evaluation retries, and final outcome.

20. `19_M1_BIO_QA_REDESIGN_PLAN.md`
   - Redesign plan after the QA-mixed CLM branch failed to produce a valid M1 checkpoint.
   - Defines the next direction: richer English synthetic biographies plus QA-mixed pretraining data.

21. `20_M1_BIO_QA_FIRST_RUN_PLAN.md`
   - First executable run plan for the BIO-QA redesign branch.
   - Records branch, commit, dataset sync target, first training config, and comparison target.

22. `21_M1_BIO_QA_FIRST_RUN_REPORT.md`
   - Execution report for the first BIO-QA training run.
   - Tracks dataset sync, pushed commits, Slurm job launch, and comparison target against R2.

23. `22_M1_BIO_QA_EVALUATION_REPORT.md`
   - English direct and QA-matched checkpoint evaluation for the first BIO-QA run.
   - Records the final comparison against R2 and the decision not to promote the branch as M1.

24. `23_M1_TWO_STAGE_ACQUIRE_EXTRACT_PLAN.md`
   - Next M1 branch plan after the BIO-QA single-stage recipe failed.
   - Separates acquisition and extraction into two explicit English-only stages.

25. `24_M1_TWO_STAGE_STAGE_A_RUN_REPORT.md`
   - First run report for the two-stage branch.
   - Records the Stage A biography-only Slurm launch and verification.

26. `25_M1_TWO_STAGE_STAGE_A_EVALUATION_REPORT.md`
   - English checkpoint evaluation for Stage A of the two-stage branch.
   - Confirms that Stage A alone should not be promoted and motivates Stage B1.

27. `26_M1_TWO_STAGE_STAGE_B1_RUN_REPORT.md`
   - First run report for Stage B1 of the two-stage branch.
   - Records the QA-only continuation launch from the Stage A final model.

28. `27_M1_TWO_STAGE_STAGE_B1_EVALUATION_REPORT.md`
   - English checkpoint evaluation for Stage B1 of the two-stage branch.
   - Confirms partial QA recovery but no valid M1 promotion.

29. `28_M1_TWO_STAGE_STAGE_B2_PLAN.md`
   - Next escalation plan inside the two-stage branch.
   - Defines answer-only loss for the English QA continuation stage.

30. `29_M1_TWO_STAGE_STAGE_B2_RUN_REPORT.md`
   - First run report for Stage B2 of the two-stage branch.
   - Records the answer-only continuation launch and final training outcome.

31. `30_M1_TWO_STAGE_STAGE_B2_EVAL_RETRY_NOTE.md`
   - Retry note for Stage B2 checkpoint evaluation.
   - Records the first eval failure, tokenizer-fallback fix, and pending clean resubmission.

32. `31_M1_TWO_STAGE_STAGE_B2_EVALUATION_REPORT.md`
   - English checkpoint evaluation for Stage B2 of the two-stage branch.
   - Confirms that answer-only continuation improved loss but not the English learned-fact gate.

33. `32_M1_RETURN_TO_BASELINE_HIGH_EXPOSURE_PLAN.md`
   - Controlled return to the original plain M1 recipe family.
   - Keeps the small model and original English facts dataset, but lowers LR and increases exposure.

34. `33_M1_RETURN_TO_BASELINE_HIGH_EXPOSURE_RUN_REPORT.md`
   - Execution report for the high-exposure return-to-baseline branch.
   - Records training outcome and the launched checkpoint-evaluation wave.

35. `34_M1_RETURN_TO_BASELINE_HIGH_EXPOSURE_EVALUATION_REPORT.md`
   - English checkpoint evaluation for the high-exposure return-to-baseline branch.
   - Confirms that lower LR plus more exposure did not beat the original plain SmolLM2 baseline.

36. `35_M1_RANKING_OBJECTIVE_PLAN.md`
   - First plan for an eval-aligned M1 ranking objective branch.
   - Keeps the small model but changes supervision from plain CLM to candidate discrimination.

37. `36_M1_RANKING_OBJECTIVE_RUN_REPORT.md`
   - First execution report for the ranking-objective M1 branch.
   - Records the implemented trainer, HU validation, and first pilot launch.

38. `37_M1_RANKING_OBJECTIVE_EVALUATION_REPORT.md`
   - English checkpoint evaluation for the first ranking-objective M1 pilot.
   - Shows the first meaningful robust-overlap recovery on the new objective family.

39. `38_M1_RANKING_OBJECTIVE_FOLLOWUP_PLAN.md`
   - Follow-up plan for the ranking-objective M1 branch after the first positive pilot.
   - Lowers the learning rate and uses a medium-length run to preserve QA gains while
     trying to move direct top1 above the plain baseline.

40. `39_M1_RANKING_OBJECTIVE_FOLLOWUP_RUN_REPORT.md`
   - Execution report for the second ranking-objective M1 run.
   - Records the launch commit, validation, Slurm job, queue state, and expected timing.

41. `40_M1_RANKING_OBJECTIVE_FOLLOWUP_EVALUATION_REPORT.md`
   - English checkpoint evaluation for the second ranking-objective M1 run.
   - Confirms that the lower-LR, longer follow-up regressed relative to the first ranking
     pilot.

42. `41_M1_SYNTHETIC_DATA_REDESIGN_DECISION.md`
   - Records the deep-research diagnosis and the selected new synthetic-data direction.
   - Documents the first implementation pass inside `syntheticFacts`.

43. `42_M1_BINDING_MIX_FIRST_RUN_PLAN.md`
   - First executable run plan for the new binding-focused M1 data family.
   - Defines the synced dataset version, first config, and launch sequence.

44. `43_M1_BINDING_MIX_FIRST_RUN_REPORT.md`
   - Execution report for the first binding-focused M1 run.
   - Records sync state, validation, upload, HU launch, and job metadata.

45. `44_M1_BINDING_MIX_MEMORY_SAFE_RELAUNCH_REPORT.md`
   - Recovery report for the first memory-safe binding-mix relaunch.
   - Records the recipe correction after the first OOM failure and the next Slurm launch.

46. `45_M1_BINDING_MIX_CLEAN_NODE_RETRY_REPORT.md`
   - Scheduler-side retry report after discovering node-level GPU contamination.
   - Records the clean-node pending job and projected overnight start window.

47. `46_M1_BINDING_MIX_CLEAN_NODE_RELAUNCH_REPORT.md`
   - Cancellation and relaunch report after investigating the misleading 41-hour estimate.
   - Records A100 availability, clean-node verification, and active job `389939`.

48. `47_M1_BINDING_MIX_EVALUATION_REPORT.md`
   - English direct and QA-matched evaluation for all four binding-mix checkpoints.
   - Records jobs `389946` through `389953` and the final learned-fact gate result.

49. `48_M1_ACQUISITION_LADDER_PLAN.md`
   - Restores the originally planned small English acquisition feasibility experiment.
   - Defines nested 10/100/500-subject training subsets, answer-only supervision,
     diagnostic views, and precommitted progression gates.

50. `49_M1_ACQUISITION_LADDER_10_SUBJECT_REPORT.md`
   - Records training job `390992`, evaluation jobs, all checkpoint metrics, and the failed
     10-subject progression gate.
   - Documents the evaluation-helper retry and the `gruenau9`/`gruenau10` scheduling policy.

51. `50_M1_SINGLE_FACT_DIAGNOSTIC_PLAN.md`
   - Decomposes the failed 50-fact rung into one fact, one relation, and all relations.
   - Precommits the single-fact training recipe, three-view gate, and stopping rule.

52. `51_M1_SINGLE_FACT_DIAGNOSTIC_REPORT.md`
   - Records training job `391013`, evaluator retry jobs, and all checkpoint ranks/margins.
   - Demonstrates exact/QA storage while localizing the remaining failure to direct-format
     extraction.

53. `52_M1_SINGLE_FACT_DIRECT_SUPERVISION_PLAN.md`
   - Adds two scaffold-free direct training forms for the same single fact.
   - Matches the previous optimizer-step budget and preserves a held-out direct paraphrase.

54. `53_M1_SINGLE_FACT_DIRECT_SUPERVISION_REPORT.md`
   - Records training job `391034` and evaluation jobs `391035` through `391045`.
   - Shows that two direct supervision forms move the held-out direct probe from rank 7 to
     rank 1 while preserving exact and QA retrieval.

55. `54_M1_BORN_IN_10_DIRECT_SUPERVISION_PLAN.md`
   - Scales the successful direct-aware format mix from one to ten `born_in` bindings.
   - Matches update/exposure budget and precommits the four-part progression gate.

56. `55_M1_BORN_IN_10_DIRECT_SUPERVISION_REPORT.md`
   - Records training job `391048` and evaluation jobs `391049` through `391059`.
   - Shows perfect 10/10 exact, direct, QA, and overlap retrieval from checkpoint 50.

57. `56_M1_ALL_RELATIONS_50_DIRECT_SUPERVISION_PLAN.md`
   - Expands the successful direct-aware recipe to five relations and 50 facts.
   - Matches exposure/update budget and precommits global plus relation-level evaluation.

58. `57_M1_ALL_RELATIONS_50_DIRECT_SUPERVISION_REPORT.md`
   - Records training job `391060` and evaluation jobs `391061` through `391071`.
   - Shows a passing 50-fact gate and near-perfect five-relation retrieval at checkpoint 75.

59. `58_M1_500_FACT_DIRECT_SUPERVISION_PLAN.md`
   - Scales the direct-aware recipe to 100 subjects and 500 facts.
   - Uses micro-batch 50 plus gradient accumulation 10 and limits initial evaluation to
     checkpoints 25/50/75.

60. `59_M1_500_FACT_DIRECT_SUPERVISION_INTERIM_REPORT.md`
   - Records training job `391072`, completed checkpoint 25/50/75 results, and the running
     checkpoint 100/125/150 wave.
   - Marks the new no-sleep monitoring protocol.

61. `60_M1_TO_M3_EXECUTION_ROADMAP.md`
   - Defines the active gated path from the 500-fact wave through 2,500 facts, full M1,
     artifact freezing, M2, and M3.
   - Records job timing, no-sleep operations, checkpoint selection, and triple-robust subset
     rules.

62. `61_M1_CHECKPOINT_250_TRIPLE_ROBUST_AUDIT.md`
   - Freezes the 265/500 three-view learned-fact subset from checkpoint 250.
   - Audits relation, branch, frequency, name, leakage, city binding, and candidate collapse.

63. `62_M1_CHECKPOINT_250_RANKING_CONTINUATION_PLAN.md`
   - Defines the controlled extraction remediation from checkpoint 250.
   - Uses balanced same-relation negatives without held-out prompt leakage.

64. `63_M1_CHECKPOINT_250_RANKING_CONTINUATION_RUN_REPORT.md`
   - Records implementation commit, preflight, Slurm job 391085, and expected timing.
   - Tracks the no-sleep training run before checkpoint evaluation.

65. `64_M1_CHECKPOINT_250_RANKING_CONTINUATION_EVALUATION_REPORT.md`
   - Tracks the checkpoint 35/70/105 external evaluation wave.
   - Applies the unchanged exact/direct/QA/overlap gate and triple-robust comparison.

66. `65_M1_RELATION_REPLACEMENT_DECISION_AND_DATA_PLAN.md`
   - Replaces proper-name education/employer relations with field and industry categories.
   - Freezes candidate sourcing, independent assignment, dependence audit, and gating rules.

67. `66_M1_RELATION_V2_CANDIDATE_AUDIT_RUN_REPORT.md`
   - Records V1 through V7 candidate audits, frozen artifacts, unchanged thresholds, and
     Slurm jobs 391097 through 391104.
   - Freezes the accepted 100/100 V7 inventory and opens independent balanced assignment.

68. `67_M1_RELATION_V2_ASSIGNMENT_AND_DEPENDENCE_AUDIT.md`
   - Records the deterministic 5,000-subject assignment implementation and rejected iterations.
   - Freezes exact balance, dependence/slice metrics, raw tables, hashes, and the passed gate.

69. `68_M1_RELATION_V2_DATASET_RELEASE_AND_10_SUBJECT_GATE.md`
   - Freezes the V2 dataset release, HU regeneration, compact gate package, and first M1 contract.

70. `69_M1_RELATION_V2_10_SUBJECT_EVALUATION_REPORT.md`
   - Reports the eleven-checkpoint exact/direct/QA evaluation and stable 45/50 triple result.
   - Accepts both replacement relations and isolates the remaining city-relation binding failure.

71. `70_M1_RELATION_V2_CITY_BINDING_CONTROL_PLAN.md`
   - Keeps the deliberately confusable city relation pair and freezes a symmetric contrast control.
   - Preserves the training budget and precommits relation-level success criteria before launch.

72. `71_M1_RELATION_V2_CITY_BINDING_CONTROL_EVALUATION_REPORT.md`
   - Reports the failed paired-city control and the unchanged 5/10 robust `lives_in` result.
   - Preserves the hard relation pair and rejects mixed-city CLM as the remediation method.

73. `72_M1_RELATION_V2_CITY_HARD_NEGATIVE_PLAN.md`
   - Freezes the city pair as permanent and defines a narrow same-subject hard-negative stage.
   - Precommits how its outcome selects the subsequent 500-fact scaling path.

74. `73_M1_RELATION_V2_CITY_HARD_NEGATIVE_EVALUATION_REPORT.md`
   - Reports the metric-neutral hard-negative continuation and preserves the clean V2 checkpoint.

75. `74_M1_RELATION_V2_500_FACT_SCALE_PLAN.md`
   - Freezes the nested 100-subject / 500-fact dataset and matched 252-update training contract.

76. `75_M1_RELATION_V2_500_FACT_EVALUATION_REPORT.md`
   - Reports perfect 500/500 storage, the 329-fact robust plateau, and the strict gate decision.
   - Quantifies the controlled improvement over historical V1 and freezes checkpoint 250.

77. `76_M1_RELATION_V2_2500_FACT_EXPLORATORY_SCALE_PLAN.md`
   - Records the explicit exploratory override without rewriting the failed 500-fact gate.
   - Freezes the nested 2,500-fact release, matched budget, and proportional evaluation gate.

78. `77_M1_RELATION_V2_2500_FACT_EXPLORATORY_EVALUATION_REPORT.md`
   - Reports near-perfect storage, the 958-fact overlap plateau, and scale interference.
   - Freezes checkpoint 252 and blocks full 25,000-fact scaling under the current recipe.

79. `78_SUPERVISOR_BRIEFING_TR.md`
   - Synthesizes the full project history in Turkish for a supervisor discussion.
   - Separates the thesis question, experimental design, negative branches, diagnostic turning
     point, Relation V2 scale results, limitations, and proposed next decisions.

80. `79_M1_RELATION_V2_RELATION_CONDITIONED_RETRIEVAL_PLAN.md`
   - Freezes the next 500-fact retrieval intervention before execution.
   - Defines prompt augmentation, hard negatives, leakage controls, and the unchanged gate.

81. `80_M1_RELATION_V2_RELATION_CONDITIONED_EVALUATION_REPORT.md`
   - Reports the small `+2` robust improvement and unchanged strict gate failure.
   - Selects checkpoint 120 and freezes one lower-learning-rate control.

82. `81_M1_RELATION_V2_PROMPT_CONSISTENCY_OBJECTIVE_PLAN.md`
   - Freezes a grouped prompt-consistency objective at the canonical 500-fact scale.
   - Aligns six training-view candidate distributions without held-out prompt leakage.

83. `82_M1_RELATION_V2_PROMPT_CONSISTENCY_EVALUATION_REPORT.md`
   - Reports the best 332/500 robust continuation result and unchanged gate failure.
   - Closes objective tuning and recommends freezing an audited M1 subset for M2/M3.

84. `83_M1_RELATION_V2_1_7B_CAPACITY_CONTROL_PLAN.md`
   - Freezes the first 1.7B capacity control using the corrected direct-aware Relation V2 recipe.
   - Keeps data, objective, exposure, effective batch, updates, evaluator, and gate unchanged.

85. `Expose.pdf`
   - Thesis expose.
   - Use as scientific framing, not as the latest operational state.

86. `NotionExport/`
   - Historical design notes and earlier planning.
   - Useful context, but not automatically current.

## Source-Of-Truth Rule

When documents conflict, prefer sources in this order:

1. latest explicit user instruction,
2. latest handoff/current status documentation,
3. repository state and artifact manifests,
4. expose/scientific framing,
5. older Notion export notes.

Older Notion notes should be cited as history unless they are confirmed by the handoff or
current repository state.

## Naming Convention

Use this pattern for curated docs:

```text
NN_SHORT_TITLE.md
```

Examples:

```text
03_M0_BASELINE_RUN_REPORT.md
04_M1_TRAINING_PLAN.md
05_CORPUS_PHASE1_RUNBOOK.md
```

For dated run reports, include the date in the title or body:

```text
03_2026-07-05_M0_BASELINE_RUN_REPORT.md
```

Use numeric order for reading flow. Use dates for milestone chronology.

## Documentation Update Policy

After every major milestone, the Documentation Agent should add or update a concise report
with:

- what was run or changed,
- exact commands,
- important outputs and run IDs,
- interpretation,
- blockers or risks,
- next recommended action.

Do not rewrite old reports to hide history. If a decision changes, add a new dated note or
clearly mark the old section as superseded.

## Current Active Docs

- `01_PROJECT_STATUS_AND_NEXT_STEPS.md`
- `02_AGENT_ROSTER.md`
- `03_INITIAL_AGENT_REPORTS.md`
- `04_M0_BASELINE_RUN_REPORT.md`
- `05_M0_QA_MATCHED_BASELINE_REPORT.md`
- `06_M1_FACT_ACQUISITION_RESEARCH_NOTES.md`
- `07_M1_FACT_ACQUISITION_PLAN.md`
- `08_M1_PILOT_LR5E-5_EP1_RUN_REPORT.md`
- `09_M1_CHECKPOINT_EVALUATION_REPORT.md`
- `10_M1_PILOT_LR1E-4_EP1_RUN_REPORT.md`
- `11_M1_PILOT_LR5E-5_EP3_RUN_REPORT.md`
- `12_M1_SMOLLM2_360M_PILOT_RUN_REPORT.md`
- `13_M1_R1_STRONGER_REPETITION_PLAN.md`
- `14_M1_R1_RUN_REPORT.md`
- `15_M1_R2_BIGGER_MODEL_QAMIX_PLAN.md`
- `16_M1_R2_SMOLLM2_QAMIX_RUN_REPORT.md`
- `17_M1_R3_SMOLLM2_QAMIX_EP3_RUN_REPORT.md`
- `18_M1_R4_SMOLLM2_1_7B_QAMIX_RUN_REPORT.md`
- `19_M1_BIO_QA_REDESIGN_PLAN.md`
- `20_M1_BIO_QA_FIRST_RUN_PLAN.md`
- `21_M1_BIO_QA_FIRST_RUN_REPORT.md`
- `22_M1_BIO_QA_EVALUATION_REPORT.md`
- `23_M1_TWO_STAGE_ACQUIRE_EXTRACT_PLAN.md`
- `24_M1_TWO_STAGE_STAGE_A_RUN_REPORT.md`
- `25_M1_TWO_STAGE_STAGE_A_EVALUATION_REPORT.md`
- `26_M1_TWO_STAGE_STAGE_B1_RUN_REPORT.md`
- `27_M1_TWO_STAGE_STAGE_B1_EVALUATION_REPORT.md`
- `28_M1_TWO_STAGE_STAGE_B2_PLAN.md`
- `29_M1_TWO_STAGE_STAGE_B2_RUN_REPORT.md`
- `30_M1_TWO_STAGE_STAGE_B2_EVAL_RETRY_NOTE.md`
- `31_M1_TWO_STAGE_STAGE_B2_EVALUATION_REPORT.md`
- `32_M1_RETURN_TO_BASELINE_HIGH_EXPOSURE_PLAN.md`
- `33_M1_RETURN_TO_BASELINE_HIGH_EXPOSURE_RUN_REPORT.md`
- `34_M1_RETURN_TO_BASELINE_HIGH_EXPOSURE_EVALUATION_REPORT.md`
- `35_M1_RANKING_OBJECTIVE_PLAN.md`
- `36_M1_RANKING_OBJECTIVE_RUN_REPORT.md`
- `37_M1_RANKING_OBJECTIVE_EVALUATION_REPORT.md`
- `59_M1_500_FACT_DIRECT_SUPERVISION_INTERIM_REPORT.md`
- `60_M1_TO_M3_EXECUTION_ROADMAP.md`
- `61_M1_CHECKPOINT_250_TRIPLE_ROBUST_AUDIT.md`
- `62_M1_CHECKPOINT_250_RANKING_CONTINUATION_PLAN.md`
- `63_M1_CHECKPOINT_250_RANKING_CONTINUATION_RUN_REPORT.md`
- `64_M1_CHECKPOINT_250_RANKING_CONTINUATION_EVALUATION_REPORT.md`
- `65_M1_RELATION_REPLACEMENT_DECISION_AND_DATA_PLAN.md`
- `66_M1_RELATION_V2_CANDIDATE_AUDIT_RUN_REPORT.md`
- `67_M1_RELATION_V2_ASSIGNMENT_AND_DEPENDENCE_AUDIT.md`
- `68_M1_RELATION_V2_DATASET_RELEASE_AND_10_SUBJECT_GATE.md`
- `69_M1_RELATION_V2_10_SUBJECT_EVALUATION_REPORT.md`
- `70_M1_RELATION_V2_CITY_BINDING_CONTROL_PLAN.md`
- `71_M1_RELATION_V2_CITY_BINDING_CONTROL_EVALUATION_REPORT.md`
- `72_M1_RELATION_V2_CITY_HARD_NEGATIVE_PLAN.md`
- `73_M1_RELATION_V2_CITY_HARD_NEGATIVE_EVALUATION_REPORT.md`
- `74_M1_RELATION_V2_500_FACT_SCALE_PLAN.md`
- `75_M1_RELATION_V2_500_FACT_EVALUATION_REPORT.md`
- `76_M1_RELATION_V2_2500_FACT_EXPLORATORY_SCALE_PLAN.md`
- `77_M1_RELATION_V2_2500_FACT_EXPLORATORY_EVALUATION_REPORT.md`
- `78_SUPERVISOR_BRIEFING_TR.md`
- `79_M1_RELATION_V2_RELATION_CONDITIONED_RETRIEVAL_PLAN.md`
- `80_M1_RELATION_V2_RELATION_CONDITIONED_EVALUATION_REPORT.md`
- `81_M1_RELATION_V2_PROMPT_CONSISTENCY_OBJECTIVE_PLAN.md`
- `82_M1_RELATION_V2_PROMPT_CONSISTENCY_EVALUATION_REPORT.md`
- `83_M1_RELATION_V2_1_7B_CAPACITY_CONTROL_PLAN.md`
- `84_HU_HOME_STORAGE_INCIDENT_AND_ARTIFACT_LIFECYCLE.md`
- `85_M1_RELATION_V2_1_7B_CAPACITY_CONTROL_EVALUATION_REPORT.md`
- `86_M1_RELATION_V2_1_7B_SEED43_REPLICATION_PLAN.md`
- `87_M1_RELATION_V2_1_7B_SEED43_REPLICATION_EVALUATION_REPORT.md`
- `89_MAX_MEETING_TECHNICAL_EVIDENCE_BRIEF_TR.md`
- `90_M1_GENERAL_CAPABILITY_DEGENERATION_PLAN.md`
- `91_M1_GENERAL_CAPABILITY_DEGENERATION_EVALUATION_REPORT.md`
- `92_MAX_PRESENTATION_GAMMA_PROMPT_EN.md`
- `93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md`
- `94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md`
- `95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md`
- `96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md`
- `97_PRE_M2_DRIFT_ABLATION_REPORT.md`
- `98_PRE_M2_FINAL_DECISION.md`
- `100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md`
- `101_M1_FORM_GENERALIZATION_REMEDIATION_PLAN.md`
- `102_M1_FORM_GENERALIZATION_REMEDIATION_RESULT.md`
- `103_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_PLAN.md`
- `104_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_RESULT.md`
- `105_M1_CROSS_FAMILY_MODEL_SCREENING_PLAN.md`
- `106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md`
- `107_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_PLAN.md`
- `108_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_RESULT.md`
- `109_TURKISH_BRIDGE_RETENTION_AND_SCALE_DECISION_PLAN.md`
- `110_TURKISH_BRIDGE_CORPUS_RESULT_AND_FREEZE.md`
- `111_TURKISH_BRIDGE_CONTRACT_V2_AND_EXECUTION_GATE.md`
- `112_TURKISH_BRIDGE_CONTRACT_V2_RESULT_AND_TRAINING_DECISION.md`
- `113_TURKISH_BRIDGE_PARALLEL_TRAINING_PLAN_AND_LAUNCH.md`
- `114_QWEN_TURKISH_BRIDGE_CLEAN_GPU_RECOVERY_PLAN.md`
- `115_TURKISH_BRIDGE_FROZEN_EVALUATION_PLAN.md`
- `116_QWEN_BRIDGE_TOKENIZER_RECOVERY_PLAN.md`
- `117_M1_RETENTION_REMEDIATION_AND_500_SUBJECT_SCALE_GATE.md`
- `118_M1_RETENTION_EVALUATION_RESULT_AND_INTEGRITY_ADJUDICATION.md`
- `119_M1_QWEN_RETENTION_SEED43_REPLICATION_PLAN.md`
- `120_M1_QWEN_RETENTION_SEED43_REPLICATION_RESULT.md`
- `121_PLAN_EXECUTION_AUDIT_98_TO_120_TR.md`
- `122_QWEN_SCALE_AND_SMOLLM_CONTRASTIVE_FEASIBILITY_PLAN.md`
- `123_QWEN_SCALE_PROBE_RESULT_AND_SMOLLM_PILOT_STATUS.md`
- `124_EXTERNAL_AI_HANDOFF_QWEN_SMOLLM_TR.md`
- `125_QWEN_CONFIRMATION_AND_SMOLLM_MATCHED_CONTROL_EXECUTION_PLAN.md`
- `126_QWEN_SEED43_AND_SMOLLM_TRAINING_COMPLETION_REPORT.md`
- `127_QWEN_SCALE_REPLICATION_RESULT_AND_SMOLLM_LAMBDA025_STATUS.md`
- `128_SMOLLM_500_FACT_PROMPT_CONSISTENCY_REMEDIATION_PLAN.md`
- `129_EXTERNAL_COLLABORATOR_HANDOFF_QWEN_SMOLLM_AND_TURKISH_STAGE_TR.md`
- `130_COMPLETE_PROJECT_HISTORY_METHODS_RESULTS_AND_FORWARD_PLAN_EN.md`
- `130_COMPLETE_PROJECT_HISTORY_METHODS_RESULTS_AND_FORWARD_PLAN_TR.md`
- `131_QWEN_25000_FACT_WEEKEND_SCALE_PLAN.md`
- `132_PRE_M2_QWEN_READINESS_AND_BASELINE_PLAN.md`
- `133_QWEN_2500_FACT_M2_M3_EXECUTION_HANDOFF_PLAN.md`
- `134_QWEN_PRE_M2_GPU_BLOCKER_AND_OFFLINE_PREPARATION_STATUS.md`
- `135_QWEN_M2_M3_CONTRACT_AND_MATERIALIZATION_STATUS.md`
- `136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md`
- `137_QWEN_M2_M3_EXTERNAL_REVIEW_HANDOFF_PROMPT_EN.md`
- `140_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_TEMPLATE_EN.md`
- `140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md`
- `143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md`
- `141_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_PLAN_EN.md`
- `142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md`
- `138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md`
- `139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md`
- `144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md`
- `145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md`
- `146_LUNA_WORKER_2_DETAILED_RESEARCH_AND_AUDIT_HANDOFF_TR.md`
- `147_LUNA_MODEL_PROVENANCE_AND_M1_SHORTLIST_AUDIT_TR.md`
- `148_CROSS_LINGUAL_LANGUAGE_ADAPTATION_LITERATURE_MATRIX_TR.md`
- `149_TURKISH_CORPUS_PROVENANCE_QUALITY_AND_CONTAMINATION_AUDIT_PLAN_TR.md`
- `150_TURKISH_CAPABILITY_AND_ADAPTATION_MANIPULATION_CHECK_PLAN_TR.md`
- `151_PRETRAINING_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md`
- `151a_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_CONTRACT_TR.md`
- `151b_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_RESULT_TR.md`
- `151c_POST_AUDIT_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md`
- `151d_BOUNDED_MODEL_AND_CORPUS_PROVENANCE_SAMPLE_AUDIT_RESUMED_RESULT_TR.md`
- `151e_POST_RESUMED_AUDIT_MODEL_CORPUS_AND_MEASUREMENT_DECISION_GATE_TR.md`
- `151f_BOUNDED_AUDIT_INDEPENDENT_VALIDATION_AND_CORRECTION_REPORT_TR.md`
- `151g_BOUNDED_AUDIT_REPAIR_CONTRACT_TR.md`
- `151h_BOUNDED_AUDIT_REPAIR_WAVE_EXECUTION_RESULT_TR.md`
- `151i_BOUNDED_AUDIT_POST_REPAIR_DECISION_GATE_TR.md`
- `151j_MEASUREMENT_DESIGN_CORRECTION_CONTRACT_TR.md`
- `151m_PHASE1_MEASUREMENT_EVIDENCE_RESOLUTION_CONTRACT_TR.md`
- `151n_PHASE1_MEASUREMENT_EVIDENCE_RESOLUTION_EXECUTION_RESULT_TR.md`
- `151o_PHASE1_POST_EXECUTION_DECISION_GATE_TR.md`
- `151p_PHASE1_INDEPENDENT_LOCAL_VALIDATION_AND_BLOCKER_CORRECTION_TR.md`
- `151q_BENCHMARK_AND_SOURCE_MODEL_METADATA_REGISTRY_COMPLETION_CONTRACT_TR.md`
- `151r_BENCHMARK_AND_SOURCE_MODEL_METADATA_REGISTRY_EXECUTION_RESULT_TR.md`
- `151s_POST_BENCHMARK_SOURCE_MODEL_METADATA_REGISTRY_DECISION_GATE_TR.md`
- `151t_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_CONTRACT_TR.md`
- `151u_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_EXECUTION_RESULT_TR.md`
- `151v_POST_MINIMAL_151Q_REGISTRY_COMPLETION_RETRY_DECISION_GATE_TR.md`
- `151w_151U_151V_COVERAGE_MATRIX_VALIDATION_AND_CORRECTION_REPORT_TR.md`
- `151x_MINIMAL_COVERAGE_MATRIX_REPAIR_CONTRACT_TR.md`
- `151y_MINIMAL_COVERAGE_MATRIX_REPAIR_EXECUTION_RESULT_TR.md`
- `151z_POST_MINIMAL_COVERAGE_MATRIX_REPAIR_DECISION_GATE_TR.md`
- `152_BOUNDED_M1_PROVENANCE_SCREEN_EXECUTION_CONTRACT_TR.md`
- `152a_M1_PROVENANCE_SCREEN_MODEL_NATIVE_REPAIR_AND_EXECUTION_PLAN_TR.md`
- `152b_M1_PROVENANCE_SCREEN_V3_FROZEN_HOME_REFERENCE_AND_NO_WRITE_PREFLIGHT_CORRECTION_TR.md`
- `153_M1_PROVENANCE_SCREEN_V3_EXECUTION_RESULT_TR.md`
- `154_M1_PROVENANCE_SCREEN_V3_POST_EXECUTION_GATE_TR.md`
- `155_M1_PROVENANCE_SCREEN_V3_AUTHORIZED_EXECUTION_LAUNCH_AND_INTERIM_STATUS_TR.md`
- `156_PYTHIA_OFFICIAL_TOKENIZER_REPAIR_AND_SINGLE_EXECUTION_CONTRACT_TR.md`
- `156a_PYTHIA_TOKENIZER_PAD_DEFAULT_RETRY_CONTRACT_TR.md`
- `156b_PYTHIA_V100_QUEUE_TO_RTX3090_RELOCATION_CONTRACT_TR.md`
- `156c_PYTHIA_RTX3090_BF16_MASTER_PRECISION_REPAIR_CONTRACT_TR.md`
- `157_PYTHIA_OFFICIAL_TOKENIZER_REPAIR_EXECUTION_RESULT_TR.md`
- `158_PYTHIA_REPAIR_POST_EXECUTION_AND_THREE_MODEL_GATE_TR.md`
- `159_THREE_MODEL_M1_DOSE_PARETO_REMEDIATION_CONTRACT_TR.md`
- `159a_OLMO_V100_QUEUE_TO_RTX3090_MEMORY_SAFE_RELOCATION_CONTRACT_TR.md`
- `159b_OLMO_RTX3090_EXPLICIT_BF16_PARAMETER_STATE_REPAIR_CONTRACT_TR.md`
- `160_M1_DOSE_PARETO_OLMO_BF16_EXECUTION_AND_FAMILY_STATUS_TR.md`
- `161_M1_DOSE_PARETO_POST_EXECUTION_GATE_TR.md`
- `162_M1_DOSE_PARETO_FALCON_MISSING_EVALUATION_RECOVERY_CONTRACT_TR.md`
- `163_M1_DOSE_PARETO_FALCON_MISSING_EVALUATION_RECOVERY_EXECUTION_RESULT_TR.md`
- `164_M1_DOSE_PARETO_POST_FALCON_RECOVERY_GATE_TR.md`
- `165_M1_DOSE_PARETO_FALCON_RTXA6000_EVALUATION_RELOCATION_CONTRACT_TR.md`
- `166_M1_DOSE_PARETO_FALCON_RTXA6000_RELOCATION_EXECUTION_RESULT_TR.md`
- `167_M1_DOSE_PARETO_POST_FALCON_RTXA6000_RELOCATION_GATE_TR.md`
- `151bk_VNGRS_CONTENT_RANGE_RECONCILIATION_SINGLE_RETRY_CONTRACT_TR.md`
- `151bl_VNGRS_CONTENT_RANGE_RECONCILIATION_RETRY_EXECUTION_RESULT_TR.md`
- `151bm_POST_VNGRS_CONTENT_RANGE_RECONCILIATION_GATE_TR.md`
- `151bn_VNGRS_SAMPLE_TRANSPORT_FEASIBILITY_PROJECTION_CONTRACT_TR.md`
- `168_M1_DOSE_PARETO_FALCON_RTXA6000_EXCLUSIVE_CLEAN_RECOVERY_CONTRACT_TR.md`
- `151bo_VNGRS_SAMPLE_TRANSPORT_FEASIBILITY_PROJECTION_EXECUTION_RESULT_TR.md`
- `151bp_POST_VNGRS_SAMPLE_TRANSPORT_FEASIBILITY_GATE_TR.md`
- `169_M1_DOSE_PARETO_FALCON_EXCLUSIVE_RECOVERY_EXECUTION_RESULT_TR.md`
- `170_M1_DOSE_PARETO_POST_FALCON_EXCLUSIVE_RECOVERY_GATE_TR.md`
- `151bq_VNGRS_CLUSTERED_WINDOW_SAMPLE_DESIGN_AND_EXECUTION_CONTRACT_TR.md`
- `171_M1_DOSE_PARETO_FALCON_DETERMINISTIC_CLEAN_UUID_RECOVERY_CONTRACT_TR.md`
- `172_M1_DOSE_PARETO_FALCON_CLEAN_UUID_RECOVERY_EXECUTION_RESULT_TR.md`
- `173_M1_DOSE_PARETO_POST_FALCON_CLEAN_UUID_RECOVERY_GATE_TR.md`
- `174_M1_DOSE_PARETO_FALCON_AUDIT_PERSISTENT_SINGLE_ALLOCATION_RECOVERY_CONTRACT_TR.md`
- `175_M1_DOSE_PARETO_FALCON_AUDIT_PERSISTENT_RECOVERY_EXECUTION_RESULT_TR.md`
- `176_M1_DOSE_PARETO_POST_FALCON_AUDIT_PERSISTENT_RECOVERY_GATE_TR.md`
- `177_SUPERVISOR_FEEDBACK_EVALUATION_FIRST_OLMO_AND_M2_PRIORITY_REALIGNMENT_TR.md`

## Planned Future Docs

- No additional result report is required for the completed M2-clean/M3-fact family. Documents
  147--151 now record the research/audit outputs reserved by Document 146, with 151h/151i recording
  the authorized vngrs repair result and gate, 151j preserved as a superseded requirements draft,
  151m--151p recording the Phase-1 contract, its execution result/gate and local blocker
  correction, and 151q--151s recording the frozen metadata-registry contract, its single bounded
  execution result and post-execution gate. Document 151t is the frozen minimal retry contract;
  Documents 151u/151v preserve its single authorized retry result and gate. Document 151w is the
  current coverage validation authority; Documents 151x--151z record the frozen repair contract,
  its single execution result and post-repair gate; 151aa is the current gap authority and 151ab
  is the current frozen measurement-design/inventory authority with the operational HU/SSH,
  allowlist and corpus-gate correction (SHA-256
  `3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c`); its single bounded
  inventory result and post-execution gate are recorded in Documents 151ae/151af. Documents 151k and 151l remain reserved from the
  superseded 151j path. The historical restrictions in Documents 151--151bd remain scoped to
  those audit waves. Document 152 is the preserved blocked M1-screen record and Document 152a is
  the current unexecuted repair plan; neither authorizes execution without its separate exact
  authorization. Documents 153/154 remain reserved and uncreated. The 151u/151v operational facts are preserved, but their coverage PASS is
  provisional/unsupported by the frozen schema; Documents 144--151 do not by themselves
  authorize training. Documents 153/154 now record the single authorized 152a wave's fail-closed
  pre-submission result and gate; they do not authorize a retry. Document 156 is the frozen
  Pythia tokenizer-repair contract; Documents 157/158 now record its completed execution result,
  artifact/storage closure and the combined three-model post-execution gate.
