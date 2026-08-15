# Project Agent Instructions

These instructions apply to every agent working anywhere under this workspace. Read them before
editing code, preparing data, connecting to HU, or submitting a Slurm job.

## Project Context

This repository implements the thesis project **Transfer vs. Relearning in Cross-Lingual Factual
Adaptation**. Experimental decisions, run outcomes, failures, and corrections must remain
reproducible and documented. The chronological reports under `documentation/` are part of the
scientific record, not disposable notes.

For the project history and master synthesis, read the master handoff before acting:

- `documentation/100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md`

For the completed post-M2/M3 state, also read the latest numbered documents before acting:

- `documentation/136_QWEN_M2_M3_ENDPOINT_EVALUATION_GPU_ALLOCATION_STATUS.md`
- `documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md`
- `documentation/141_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_PLAN_EN.md`
- `documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md`
- `documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md`
- `documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md`
- `documentation/139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md`
- `documentation/144_SUPERVISOR_FEEDBACK_AND_SCIENTIFIC_REALIGNMENT_TR.md`
- `documentation/145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md`
- `documentation/146_LUNA_WORKER_2_DETAILED_RESEARCH_AND_AUDIT_HANDOFF_TR.md`

Then consult the relevant evidence reports. In particular:

- `documentation/84_HU_HOME_STORAGE_INCIDENT_AND_ARTIFACT_LIFECYCLE.md`
- `documentation/94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md`
- `documentation/95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md`
- `documentation/96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md`
- `documentation/97_PRE_M2_DRIFT_ABLATION_REPORT.md`
- `documentation/98_PRE_M2_FINAL_DECISION.md`
- `documentation/102_M1_FORM_GENERALIZATION_REMEDIATION_RESULT.md`
- `documentation/103_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_PLAN.md`
- `documentation/104_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_RESULT.md`
- `documentation/105_M1_CROSS_FAMILY_MODEL_SCREENING_PLAN.md`
- `documentation/137_QWEN_M2_M3_EXTERNAL_REVIEW_HANDOFF_PROMPT_EN.md`
- `documentation/138_QWEN_M2_M3_COMPLETED_MILESTONE_AND_SCIENTIFIC_INTERPRETATION_EN.md`
- `documentation/139_POST_M2_M3_INDEPENDENT_NEXT_ACTION_PLAN_EN.md`
- `documentation/140_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_TEMPLATE_EN.md`
- `documentation/140a_QWEN_M2_M3_INDEPENDENT_REVIEW_RESULT_EN.md`
- `documentation/141_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_PLAN_EN.md`
- `documentation/142_QWEN_M2_M3_EXPLORATORY_MECHANISM_ANALYSIS_RESULT_EN.md`
- `documentation/143_QWEN_M2_M3_ARTIFACT_RETENTION_FREEZE_AND_STORAGE_AUDIT_EN.md`

Document 100 remains the historical/master synthesis and must be preserved. Document 136 is the
current operational/result authority for the completed Qwen M2/M3 family; Document 138 is the
current scientific milestone interpretation; Document 139 authorizes only read-only review,
exploratory analysis, documentation alignment, and later artifact closure; Document 142 records
the completed exploratory result without changing the primary gate; Document 143 records the
completed model-only retention freeze and storage audit. Earlier chronological
reports remain the scientific evidence record and must not be rewritten to hide failures or
superseded decisions. Do not infer the post-M2/M3 state from stale pre-M2 HOLD passages in
Document 100.

Documents 144 and 145 record the 6 August 2026 supervisor-driven scientific realignment. New work
must distinguish the completed Qwen Wikipedia-only pilot from the next literature-first design,
treat the new core conditions as parallel sibling arms `M2-A` (general Turkish corpus) and `M2-B`
(the same adaptation with controlled Turkish factual re-exposure), and audit both source-model
Turkish provenance and genuine Turkish-capability improvement before opening a new factual
training family. These documents authorize read-only literature/model/corpus audits and local
planning only; a separately frozen execution contract is still required before training.

Document 146 is the detailed handoff for the next read-only research worker. It defines WP0--WP5
and reserves Documents 147--151 for model-provenance, literature, corpus, measurement, and decision
audits. It does not authorize HU access, Slurm work, training/evaluation runs, large model or corpus
downloads, corpus materialization, or artifact mutation. Do not create the later execution
contracts or claim readiness to train until the Document 146 evidence package is complete and the
user explicitly authorizes the next stage.

### Current three-model M1 screening authority (2026-08-11)

Document 152 exists and is preserved as the historical `NATIVE ASSET GATE` block for the bounded
OLMo-2-0425-1B, Pythia-1.4B and Falcon-RW-1B 500-fact screen. It produced no training or
evaluation metrics. Document 152a is the current model-native repair and execution-plan authority;
its SHA-256 is `411b32bedebc8f710b0d533ba7d17884d854bafe892496068ef20517d90a950a`.
It replaces the universal tokenizer-filename gate with an offline model-native tokenizer
save/reload/offset/embedding compatibility gate, makes the three candidate DAGs independent, and
uses a fresh proposed root `/vol/tmp2/yesildau/m1_provenance_screen_v3`. The user authorized its
single wave. Document 153 records the fail-closed result and Document 154 is the current
post-execution gate. Commit `a0eeed33c7c894b9ae05c369869d114419603e66` was ordinary non-force
pushed and preservation-checked fast-forwarded on HU, but the mandatory exact-byte HU-home `du`
did not complete within 120 seconds. The v3 scratch root remained absent, matching Slurm jobs were
zero, and model access, training and evaluation were all zero. The effective narrow gate is
`blocked_by_operational_preflight`; there is no automatic retry or scientific candidate result.
The user has fixed the work order as the
three-model 500-fact screen first, followed only later by a separately contracted vngrs corpus
audit with trwiki as control; Document 152a does not authorize that corpus stage.

Document 152b is the current frozen, locally prepared storage-preflight correction; its SHA-256
is `1b55a03484682e065c9eaec106f8803b9ffdecba9301e3a0261df9e6ecd154fa`. At the user's request,
one bounded read-only exact measurement completed on 2026-08-11 with `14,689,423,360` bytes
(approximately 13.68 GiB) in 96.99 seconds, below the 30 GiB limit. For v3 only, 152b replaces
repeated per-stage recursive home `du`/large-file scans with this frozen reference plus mandatory
no-home-write policy, scratch-only output/cache/tmp path resolution, `df`/inode/capacity, root
absence, dataset, commit, dirty-overlap and duplicate-job gates. It does not authorize push,
HU fast-forward, model access, Slurm/GPU, training, evaluation or an automatic retry. A new exact
user authorization bound to Document 152b is required.
The previously prepared local correction is now covered by the user's exact 152b execution
authorization and Document 155. Commit `f0caa05b7ac487b376ed7f2e070a5dd5c8d9415e` was pushed and preservation-checked
fast-forwarded on HU; the targeted HU suite passed 98/98 and shared acquisition preflight passed.
OLMo/Falcon acquisition and training preflight passed and their training jobs `452145`/`452155`
are queued. Pythia's pinned snapshot produced an invalid two-token tokenizer with empty probe
encodings; its train/eval jobs were cancelled before GPU work and its current class is
`NOT_RUN_MASKING_COMPATIBILITY_GATE`. Document 155 is the current interim operational authority.
Do not retry Pythia, substitute a tokenizer/revision, cancel the valid OLMo/Falcon chains, or open
corpus/seed-43/M2-M3/cleanup work without separate authority.

The user subsequently explicitly cancelled the long-wait A100 DAG and requested live free-GPU
rerouting. Document 155's append-only GPU update is current: Falcon job `452163` is running on a
clean `guppi7` RTX3090 after a valid smoke (peak 13.26 GB); OLMo failed optimizer smoke twice on a
clean `guppi5` RTX3090 before training, including one allocator-only retry. `guppi6` is excluded
because foreign processes occupy about 21.4 GiB despite Slurm idle state. Immediate OLMo execution
was subsequently approved as the isolated `10×50 -> 5×100` microbatch/accumulation decomposition
while preserving effective batch 500. Narrow commit
`f7b2b6d527b84328792c773e84b34c46e6cbaeae` was ordinary non-force pushed and
preservation-checked fast-forwarded on HU; the HU targeted suite passed 60/60 and OLMo-only
preflight job `452173` passed. OLMo training job `452174` then failed during its pre-training
AdamW optimizer smoke: `5×100` remained approximately 69 MiB short at the multi-tensor optimizer
peak, and no scientific training began. Dead downstream jobs `452175`/`452176` were cancelled.
This is `NOT_RUN` operational evidence, not a candidate score. Do not submit another OLMo retry,
change optimizer implementation/precision, or alter the recipe without explicit authority. The
user then authorized a single `optimizer_foreach: false` attempt: commit
`5407161a0b3a978fafef9d1ac4d7eb736552d910` was pushed/fast-forwarded, HU tests passed 61/61 and
preflight `452177` passed. Job `452178` verified `_single_tensor_adam` but failed at the same
pre-training 784 MiB `sqrt()` temporary with only 715.38 MiB free; downstream `452179`/`452180`
were cancelled. Thus foreach was not the root cause. No further OLMo retry is authorized by that
attempt. The user then explicitly selected V100. The existing Torch 2.7/CUDA 12.8 env failed
compatibility job `452182` because it lacked `sm_70`; this was not a model failure. A scratch-only
Torch 2.6.0/CUDA 12.4 environment was installed and actual V100 validation job `452190` passed
finite FP16 forward/backward. Fresh preflight `452191` and the full OLMo optimizer smoke passed;
job `452192` is now in real 252-update FP16 training on `gruenau1` with peak smoke allocation
29,973,358,592 bytes. Downstream evaluation jobs are `452193`/`452194`. Falcon `452163` remains
independent. Do not duplicate or alter either active chain, and do not claim OLMo completion before
training/evaluation artifacts are verified.

Document 156 is the current frozen, unexecuted Pythia official-tokenizer repair contract; its
SHA-256 is `0e48ec4882768d92d2a88e75e8d54a7d505d95a1605b015692e31b3b9e5c8985`.
It preserves the exact Pythia-1.4B weight revision
`0da31d8fb309463877ed8c40e54a8f911dced3ec` and all historical v3 evidence, and permits a future
separately authorized wave to bind those weights to EleutherAI/Pythia's official
`utils/20B_tokenizer.json` at immutable upstream commit
`1e2365516a3284f18a68c13dbd4ca19fcae59a4b` (2,467,981 bytes; SHA-256
`56ac4821e129d2c520fdaba60abd920fa852ada51b45c0dd52bbb6bd8c985ade`) under the fresh root
`/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_v1`. The local implementation rejects
empty probe encodings and two-token vocabularies, supports a separate tokenizer source in
tokenization audit/smoke/evaluation, and freezes one V100 FP16/GradScaler 500-fact chain. Document
156 preparation does not authorize push, HU/SSH, tokenizer retrieval, Slurm/GPU, training or
evaluation. Exact user authorization bound to Document 156's SHA-256 is required. Documents
157/158 are reserved for the execution result and post-execution gate.

The exact Document 156 wave was executed once and failed closed before composite-manifest creation
because Transformers 5.13's `GPTNeoXTokenizerFast` constructor supplied its own
`<|padding|>`/ID-1 default. Acquisition preflight job `452542` passed; job `452543` downloaded the
exact 2,467,981-byte official source but stopped at the explicit PAD assertion; pending training
preflight `452544` was cancelled, and no GPU/smoke/training/evaluation occurred. The first repair
root remains preserved and must not be reused or cleaned. Document 156a is the current frozen,
unexecuted single-retry contract; its SHA-256 is
`13f2e281b13a699149a2d0cb51ee62c9395180655534e6b2c8c224fab5284429`. It changes only explicit
`pad_token=None`, HU's verified `gpu:v10032gb:1` selector and fresh-root launcher routing. Its
proposed root is `/vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_retry_v1`. No retry,
push, HU fast-forward or new Slurm/GPU chain is authorized without exact user authorization bound
to Document 156a.

The exact Document 156a wave has now passed acquisition preflight `452895`, official-tokenizer
job `452896` and training preflight `452897`. The composite manifest records vocabulary `50,277`,
PAD `null` and the frozen source identity. V100 training `452898` has not started and remains
`PENDING(Resources)` behind three foreign V100 jobs; `452899`/`452900` are dependency-pending.
Document 156b is the current frozen, unexecuted operational-relocation contract. It preserves the
completed tokenizer/preflight evidence and every scientific recipe field, but permits a separately
authorized cancellation of only the three not-started downstream jobs and one fail-closed RTX3090
training/evaluation continuation. No relocation, cancellation, push, HU fast-forward or RTX3090
Slurm action is authorized without exact user authorization bound to Document 156b.

The exact Document 156b relocation was executed. RTX3090 training preflight `453126` passed and
job `453127` immediately ran on `guppi5`, where exact runtime and tokenization gates passed. The
optimizer smoke then failed before scientific training with PyTorch's explicit `Attempting to
unscale FP16 gradients` guard because native FP16 parameters cannot be GradScaler-unscaled without
FP32 master parameters. No optimizer update, checkpoint, training run or evaluation namespace was
created; dependency-dead `453128/453129` were cancelled and artifacts remain preserved. Document
156c is the current frozen, unexecuted BF16 parameter/optimizer-state compatibility contract. It changes
only the RTX3090 precision binding to explicit BF16 model load/training with no GradScaler while
preserving the complete scientific recipe. No 156c push, HU fast-forward or Slurm execution is
authorized without exact user authorization bound to its SHA-256.

Document 156c was subsequently authorized and completed. BF16 preflight `453163`, training
`453164`, evaluation preflight `453165` and evaluation `453166` all completed on clean `guppi5`;
runtime, tokenizer, BF16 parameter/gradient/AdamW-state and preserved smoke-checkpoint gates passed.
Documents 157 and 158 are the current result and post-execution gate authorities. Pythia achieved
100% exact-prefix and 98.175% aggregate hard-suite accuracy, but profession form-C bottomed at 65%
against the 70% robust gate and WikiText-2 PPL rose from 22.5740 to 364.5404 (16.1487x) against the
1.25x retention gate. It is a valid scientific negative result, not an infrastructure failure.
Together with completed OLMo and Falcon, the requested three-model 500-fact screen now contains
three valid negative results and no automatic primary-model selection. No cleanup/deletion,
outcome-aware rerun, seed-43, corpus, dose ladder or M2-A/M2-B execution is authorized by this
closure.

Document 158 §2.1 is the durable terminal ledger for the previously progress-only OLMo/Falcon
record. Falcon training/evaluation are `452163_2`/`452167_2`; OLMo training/evaluation are
`452192_0`/`452194_0`, with pre-evaluation jobs `452165` and `452193`. Their training manifests,
hard/exact/general summary paths and SHA-256 values are frozen there. The shared root
`/vol/tmp2/yesildau/m1_provenance_screen_v3` retains 54,089,916,824 bytes (51G); no cleanup was
performed. Frozen per-subject eight-prompt robust intersections reproduce OLMo profession 59/100
and Falcon profession 37/100. HU `sacct` was unavailable during the final documentation check due
Munge/SlurmDBD authentication failure; this is missing accounting metadata, not a run failure.

Document 159 is the frozen three-model dose/Pareto remediation contract. It
preserves the v3 negative results, exact model/data/runtime identities and every existing gate. It
proposes exactly one seed-42 run per OLMo/Falcon/Pythia with precommitted checkpoints
`42/84/126/168/210/252`, cheap exact/PPL/generic evaluation at every checkpoint and hard-suite
only after exact+PPL PASS. It does not authorize LR changes, threshold relaxation, seed43,
prompt/replay intervention, corpus, M2/M3, deletion or cleanup. A final Document 159 SHA-bound
authorization was required before implementation publication, HU/SSH, Slurm, training or
evaluation; that authorization was later supplied. Documents 160/161 are reserved for its result
and gate.

Document 159 was subsequently authorized and its three-model DAG was submitted. Falcon and
Pythia entered RTX3090 training; Falcon's first job `453295` failed before scientific training at
the BF16 model-load smoke gate, the append-only implementation repair passed 70 HU tests, and
replacement job `453300` passed smoke without changing the registry or scientific recipe. OLMo
job `453301` never received a GPU and remained `PENDING(Resources)` with a scheduler estimate near
41 hours because all three V10032GB cards were allocated. OLMo v4 training/evaluation namespaces
remain absent.

Document 159a is the current frozen, unexecuted OLMo-only queue-relocation amendment. Its SHA-256
is `e13c2a08c482e027ab04c364306b6b62ec73897d9caca7b111a188796235b0cb`. It preserves FP16,
effective batch 500, LR, seed, 252 updates, six checkpoints, evaluation cascade and every gate,
while moving only OLMo to RTX3090 with memory-safe `microbatch=4` and
`gradient_accumulation=125`. It does not authorize any Falcon/Pythia/foreign-job cancellation,
second scientific OLMo run, threshold/LR change, deletion or cleanup. Exact SHA-bound user
authorization is required before implementation publication, HU synchronization, pending-job
cancellation or relocation execution.

Document 159a was subsequently executed through its precommitted RTX3090 memory fallbacks, but
all three attempts stopped before scientific training: jobs `453386` and `453479` failed at FP16
AdamW optimizer-state smoke, and `453513` failed in the single-tensor AdamW `sqrt` temporary with
only 553 MiB free. No OLMo v4 training/evaluation namespace or scientific checkpoint exists.
Document 159b's exact SHA-bound OLMo BF16 wave was subsequently authorized and completed. Document
160 is the execution/family-status authority; its SHA-256 is
`9e995bc9cdff6ffa1da0e17194e050b590c2f7cbf8e2af0345672e6a425044de`. BF16 runtime, optimizer
smoke, 252-update training and all six cheap checkpoint gates passed integrity. OLMo reached 100%
exact acquisition at every checkpoint, but its PPL ratios were 1.385--1.429 against the frozen
1.25 maximum, so no hard suite opened and OLMo is a valid scientific negative. Document 161 is the
current post-execution gate; its SHA-256 is
`eea7227ef433506755da53699af9adf30e36aa574caec22fce48f9db30224579`. Pythia has 6/6 cheap gates,
but Falcon has only 3/6: checkpoints 126, 210 and 252 stopped before scientific evaluation at the
free-VRAM runtime guard. The family therefore has 15/18 required rows, no summary and no selected
primary model. No Falcon recovery, seed-43, Turkish dose ladder, M2-A/M2-B, cleanup or deletion is
authorized by this result.

Document 162 is the current frozen, unexecuted Falcon-only missing-evaluation recovery contract;
its SHA-256 is `4ada146f01c777a2995d6bc4901e1cbaf9bae574b9d93263440fdfe9cca355fd`.
It preserves Falcon's completed seed-42 training and all 15 existing family cheap gates, permits
only array indices `2,4,5` for checkpoints `126,210,252` on one sequential clean `guppi5`
RTX3090 route with a 20 GiB free-VRAM guard, and opens the existing family summary only through an
`afterok` dependency after 18/18 rows exist. It forbids every training rerun, completed-evaluation
rerun, threshold/recipe/seed change, second recovery array, cleanup and automatic primary
promotion. The local implementation is frozen in commit
`37a7d29a182f049054483915f4ceee5bc7fdd1d4` and the compatible suite passed 380/380. No
publication, HU synchronization, preflight, Slurm/GPU evaluation or summary is authorized without separate
exact SHA-bound user approval. Documents 163/164 are reserved for its result/gate.

Documents 162, 165, 168 and 171 were each executed once and remain preserved operational
NOT-RUN evidence. The Falcon family still has 15/18 cheap rows, missing checkpoints
`126/210/252`, no family summary and no selected primary model. Document 171's clean-UUID selector
correctly stopped all three tasks before model load when no A6000 met the frozen zero-process,
40 GiB free and 512 MiB used bounds, but failed to persist the required four-GPU failure ledger.
Documents 172/173 are the current result/gate authorities for that wave; summary job `456502` is
dependency-dead and must not be cancelled without separate authority.

Document 174 is the preserved Falcon-only audit-persistent single-allocation recovery contract;
its SHA-256 is
`75964edfdd4e3d792ac355ce9e966db9918e88b9aed59953daa2bf071fce0a3a`. It writes the full
four-GPU UUID/memory/process ledger atomically on both PASS and no-clean-candidate paths, binds the
lexicographically smallest clean UUID once, and proposes one non-array exclusive job evaluating
only missing checkpoints `126 -> 210 -> 252` sequentially, followed by one 18/18-closed `afterok`
summary. The local implementation is commit `9314a02b7a6986d760602002648372d266d04227`;
focused tests passed 16/16 and the compatible suite passed 382/382. Its preparation alone did not
authorize execution; the exact SHA-bound authorization and single execution are recorded below.

Document 174 was subsequently authorized and executed once. HU focused tests and fresh preflight
passed; old dead summary `456502` was cancelled, test-only was `456593`, evaluation job was
`456594` and its `afterok` summary was `456595`. The repaired failure audit passed and preserved a
2,522-byte manifest with SHA-256
`68751ff26908b1555370e93806003b6c4a79cf857e64a38cb6aa35faf26487b3`.
All four gruenau8 A6000s were occupied by foreign `VLLM::Worker_TP0--TP3` processes, each with only
3,423,600,640 free bytes and 47,474,278,400 used bytes. No UUID was selected; no runtime validator,
model load or scientific evaluation ran. Documents 175/176 are the current result/gate
authorities. The family remains 15/18 and summary `456595` is dependency-dead. Do not blindly
retry the same route, cancel `456595`, intervene in foreign processes, reroute, alter thresholds or
open later scientific work without a new exact contract and user authorization.

### Current bounded-audit authority (2026-08-07)

Documents 151d and 151e are preserved as historical preliminary/provisional evidence. Document
151f is the current **evidence-integrity correction and externally prompted validation** authority;
it is not a genuinely independent external review. Document 151g remains the frozen repair
contract, and Documents 151h and 151i are the append-only execution result and post-repair gate.
Document 151j is preserved as a `SUPERSEDED_UNEXECUTED_REQUIREMENTS_DRAFT`; its broad execution
request is withdrawn, it produced no scientific results, and it must not be executed. Document
151m is the frozen bounded Phase-1 evidence-resolution contract and was executed once. Documents
151n and 151o remain historical preliminary/provisional execution and gate records. Document
151p is the current **Phase-1 local validation and blocker correction** authority. Its local
validation closes the synthetic-inventory provenance blocker and the exact 65,717 inventory
reproduction component. Document 151q is the frozen bounded benchmark/source-model metadata
registry contract with three append-only corrections; it was executed once under the user's
explicit Single Next Authorization Request. Its original
SHA-256 is `b55499242100263e0d9adbe946679b6175268012d1c3e897298413a2af1ef60c`; the first corrected
SHA-256 is `0acf5251bea811e07b6442681ec02c7bc4fa2ea584a55e8b48cbcb704d4209e3`; the second corrected
SHA-256 is `c217f4d8395a8e3b657f96fd46f3e6443a11fcde6bbfbd6f7a8414933ccf89ee`; and the final
third-correction SHA-256 is `f1cdfe082a78fce612d7bc53766e88dae3182ffcf52a225f2aa81e24c2491561`. The third correction limits the
earlier no-HU/SSH language to the preparation/correction passes and makes a future separately
authorized wave explicitly eligible to use the documented `ssh-client` route, mandatory
storage/path/inode preflight, public HTTP retrieval within 151q's bounds and writes only under
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1`. HU home and prior
evidence roots remain read-only. The execution result is Document 151r and the post-execution gate
is Document 151s; both are current chronological authorities. The effective operational gate is
`blocked_by_operational_access` because the fixed EXAMS `test_with_para` response exceeded the
32 MiB single-response bound and the wave failed closed. The global gate remains
`blocked_by_measurement_design`. Future alias/template/overlap definitions and capability
measurement remain unresolved. Documents 151k/151l remain reserved from the superseded 151j path.
CulturaX remains `excluded_access_blocked`, so CulturaX--vngrs comparative selection is
unavailable. Benchmark scoring is unconditionally forbidden. No further 151q execution is
authorized by this result; any new attempt would require a separately revised contract and explicit
authorization. HU home, all prior evidence roots, model/tokenizer weights, corpus, Slurm/GPU,
training, cleanup, Documents 151k/151l and 152--154 remain outside scope.

Current local SHA-256 of Document 151r is
`09ffb44bea8711e7c9e37dd7a4c5cea93d9c277f552bdc50bc556fdf55facfe8`; current local SHA-256 of
Document 151s is `cec364cf21716a186311d243094f669b998bd2cf558a02bd21fcb3438be61950`.

Document 151t was the frozen minimal 151q registry-completion retry contract. Its pre-correction
SHA-256 is `eef968538b2022250803504ba1f206860c053663bb9ce74f761c3ae25c4c11cc`; the final
route-correction SHA-256 is
`63951ba5543c2c803e8466d0c43e0aace9637ca1239164dc1d9f5e49ea75f46b`. It preserved 151q/151r/151s
and kept the first execution root
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1` immutable/read-only.
Under one explicit authorization, it was executed once using the new retry root
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1`; Documents 151u
and 151v record the execution result and post-retry gate. The retry PASS is scoped to the exact
EXAMS artifact and three raw model-card metadata rows. The prior `blocked_by_operational_access`
state from 151s is closed for this narrow registry-completion component; the global
measurement-design gate remains `blocked_by_measurement_design`, training remains `BLOCKED`, and
`ready_to_train` remains false. Scoring, inference, weights, tokenizers, corpus materialization,
GPU/Slurm, training, cleanup, deletion and prior-root writes remain forbidden. Documents 151k/151l
and 152--154 remain uncreated and unauthorized. The route correction's raw-byte, redirect-chain,
content-type and fail-closed requirements were evidenced in 151u.

Current local SHA-256 of Document 151u is
`579be50a33a8bc26c71b7f47969bfca4a9e30fde06172e3cbe21dfa772976909`; current local SHA-256 of
Document 151v is `5f822449cd5295cee26b9f550c5883d4c897276fb0ee754b20a8540393edb871`.

### Coverage and 151x protocol correction authority (2026-08-08)

Document 151w is now the current validation authority for the 151u/151v coverage-matrix PASS.
Its SHA-256 is `2b19bfbea496bb76efc4e06d24d815d2b83b06090e6ebdee6526773c5fb96de3`. The HU
inspection was source-read-only: the first-wave root had 91 files / 13,063,617 bytes and the
retry root had 16 files / 38,315,850 bytes; no HU file or root was changed. The retry coverage
file contains six entity-summary rows rather than one row for every required entity-field, the
first-wave matrix lacks three mandatory coverage metadata fields on all 132 rows, and the retry
benchmark/model registries do not satisfy their frozen 27/23-field schemas. The three raw
model-card rows are retained evidence, not complete provenance rows.

Documents 151u and 151v remain historical execution/gate records and are not rewritten. Their
successful EXAMS/raw-README/hash/storage facts are preserved, but their scoped coverage PASS is
now classified `PROVISIONAL / UNSUPPORTED BY THE FROZEN COVERAGE RULE`. The current narrow
coverage gate is `BLOCKED`, with primary blocker `blocked_by_coverage_schema` and contributing
`blocked_by_benchmark_registry`; the global gate remains `blocked_by_measurement_design`.
Document 151x was the current frozen minimal repair contract and was executed exactly once under
explicit authorization. Its pre-correction SHA-256 is `a19ed3b7e15540fa2810d5f483b2015cc5badd2bd41949d8678f945d3a6fb32e`; its final protocol-correction SHA-256 is
`9c66cb95ee264d8411750d8e79aff258eaaeb4d1789ffc77bc8e162ffc93555b`. The append-only correction names
`output_artifact_manifest.jsonl`, excludes self-reference and the later final audit from that
manifest, freezes the one-way final-audit chain, requires exactly 150 required field-level
coverage rows, and freezes mandatory HU storage/path/inode preflight. Its proposed new root is
`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1`; it now contains
the nine contract outputs. Documents 151u/151v remain historical execution/gate records and
151x remains frozen and unchanged. Documents 151y and 151z are the current execution result and
post-repair gate. 151x execution is `BLOCKED` by `blocked_by_benchmark_registry` and
`blocked_by_source_model_provenance`; the global gate remains `blocked_by_measurement_design`.
The repair root has 9 files / 203,993 bytes with inventory SHA-256
`7bce6b0d70c8069595d9c8ca96801b2eca1faf5a31973b8741e176926ef26e82`; both pre-existing HU roots
remain unchanged and read-only. No network, scoring, inference, weights/tokenizers, corpus,
GPU/Slurm, training, cleanup, or Documents 152--154 action is authorized; `ready_to_train` is
false and no further 151x execution is authorized. Current local hashes are 151y =
`1309af278901009c22d2ee5b2438fdec886abe27cdaa60c4555dcd3af42ae6ba` and 151z =
`51e3cdda3db8a636f1308a42910c2dd76bfdca5ef0906a3a316dc639c4b984db`.

### Final evidence-gap and measurement-design authority (2026-08-08)

Document 151aa is the current read-only evidence-gap authority. It verified the six existing
repair-root files without HU writes, corrected the 151y narrative from eight to the actual seven
manifest rows, and enumerated all 54 non-verified coverage fields. Its SHA-256 is
`0a063d7d7465eb8bffdfa47a55fa95adc8420cef0a641e9d967c19ef6cdb69ae`.

Document 151ab remains the current frozen measurement-design authority/minimal baseline contract,
now executed once for its bounded inventory-only scope. Its original pre-correction SHA-256 is
`500b24f6945272cbf7ddb0f26e95449434857bcac89ed5fb5d593e3fd189b4dd`; its first corrected final
SHA-256, preserved as the pre-operational-correction hash, is
`3320516e674c12288d70396e31b33c059550c15365caabe9453e932e3858e2dc`; its final
operationally corrected SHA-256 is
`3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c`. The first correction
freezes BPB, the primary in-domain Turkish held-out role, `trwiki-20260601` as cross-domain
control, the WikiText-2 token-stream hash distinction, exact M0/M1 states, both thesis estimands
and the expanded review ledger. The second correction resolves the operational contradiction:
any future inventory wave must use the documented HU/SSH route, mandatory storage/path/inode
preflight and one new scratch root, while all existing sources and prior roots remain
read-only. It freezes a closed exact source allowlist, zero public HTTP/download limits, bounded
metadata/path-stat output limits, and no recursive corpus read. It may inventory candidate corpus
evidence but may not select/materialize the primary in-domain split; absence remains
`blocked_by_corpus_selection_or_materialization`, with `trwiki-20260601` control-only. Documents
151ac/151ad remain reserved and unused. The one authorized inventory execution wrote exactly eight
compact outputs under `/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1`; the
existing sources, HU home and prior evidence roots remained read-only. Document 151ae records the
execution result and Document 151af records the post-execution gate. Their local SHA-256 values are
`b6a90ce5573de1c29828186dbc278c7c92c87dc1e435ef44965d0eff6f8e1601` and
`1e96a4b8d29edc50a8f151a34990c93edf3b5115dfb76416500261f8f8d817d1`, respectively.

The operational inventory passed, but the scientific gate remains
`blocked_by_measurement_design` with contributing blocker
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure` and `ready_to_train` are
false. No selected adaptation corpus or primary in-domain split was fabricated. The inventory did
not authorize baseline scoring, corpus construction, model/tokenizer acquisition, inference,
evaluation, GPU/Slurm, training, cleanup or Documents 152--154. Later corpus selection, scoring or
measurement requires separate contracts and explicit authorization; successful inventory does not
authorize dose-ladder training or M2-A/M2-B.

Before connecting to HU, running an `ssh-client/scripts/*.sh` file, or submitting Slurm work, read
`ssh-client/README.md`. Existing shell scripts are historical experiment-specific launchers and
must not be treated as generic current entrypoints.

The workspace root is not a Git repository. `transfer-vs-relearning/` and `syntheticFacts/` are
separate Git repositories with separate branches and dirty generated outputs. Run Git commands in
the intended repository, inspect status first, and preserve all unrelated tracked and untracked
user files.

### Corpus selection and materialization authority (2026-08-08)

Document 151ag is the current exact C1 reconciliation and corpus-selection decision. Its HU
inspection was limited to the six named inventory files and was read-only. It classifies
`vngrs-ai/vngrs-web-corpus` only as a **conditional primary materialization candidate**,
`trwiki-20260601` as a frozen cross-domain control, and `uonlp/CulturaX` as
`excluded_access_blocked`. vngrs is not `quality_pass`, selected, frozen for training or
`ready_to_train`. The six-file reconciliation is operationally complete: 60 source-allowlist
rows, 5 model/tokenizer rows, 6 evaluation-input rows and 17 C1 rows; C1 statuses are 12
`observed_existing_compact_evidence`, 2 `verified_existing_selected_manifest`, 1 `blocked`, 1
`existing_control_identity_stat_only` and 1 `existing_input_identity_stat_only`.

Document 151ah is the current frozen, **unexecuted** vngrs acquisition/materialization contract,
with append-only metadata/structural and systematic-selection corrections. Its pre-correction
SHA-256 was `a8c1d1d2082ec3ae5b31ace5dc0a9506ace90f82d0f7bd1a2c1a528069ef2269`; its immediately
prior SHA-256 was `9151da7112b6d1ab9bbb3b483b202dec23449624beeddb53c23682569a0f598b`; its current
SHA-256 is `18bf6d59b0552b044bec70f2f41852912c493ec098917dbd1ed87f5078eda1e8`. The bounded official
metadata pass verified immutable revision `ee5c6201ee84457a18182bfc483a7d8a7f3655ba`, 50,336,214
train rows, schema `text/corpus/original_id`, the 284-shard tree and CC BY-NC-SA 4.0 metadata.
The exact 32-path systematic midpoint set is frozen as ordinals
`00004,00013,00022,00031,00039,00048,00057,00066,00075,00084,00093,00102,00110,00119,00128,00137,00146,00155,00164,00173,00181,00190,00199,00208,00217,00226,00235,00244,00252,00261,00270,00279`;
selection payload SHA-256 is
`dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686`. Exact per-shard
LFS/SHA/footer/byte metadata, execution-time license byte hashes and sample-based tokenizer-yield
evidence remain unresolved, so 151ah remains `PREPARATION_BLOCKED`; the path set is exact but not
yet an executable download allowlist. Its proposed root
`/vol/tmp2/yesildau/luna_vngrs_corpus_acquisition_materialization_v1` was not created.

Document 151ak is the current frozen, **unexecuted** model-neutral bounded sample-calibration
contract. Its pre-correction SHA-256 was
`97a2d8a53cc8ff8390f71ddb833e9582d8b46fb9793deeb6673483a1384df012`; its immediately prior
SHA-256 was `8fc6d3dbc89f9b71e7b9e1f6ca787fce81bbcde2cf715abfa2fec54eb0b07bd5`; its previous current
SHA-256 was `eb520ece20b157ec342cd6511589907b561dd7cea5e4d68cb1cd84327c92bd8e`. The prior final
correction SHA-256 is `16f2978b10fc2b71490917ffe9ed549b574d2b364865675f0f1d900fb4320d68`; the prior
append-only final evidence-graph correction SHA-256 is
`1920f1c58d8ada250af50d1f088f5ad2fc3a15e8221f84d92f5458dab415154b`; and the current append-only
evidence-binding/sampling-schedule correction SHA-256 is
`9e35ba69fcd4885c339101e59f1d719681942571770a41023f20f6472782ea94`. The effective contract
freezes a 34-field raw record manifest with explicit `(immutable_revision, corpus, original_id)`
identity, raw decoded versus normalized character counts, complete raw LID evaluator identity,
request-ledger aggregate reconciliation (`128` attempts, `100` successful-row maximum, `28`
retries, `64 MiB` total, `4 MiB` per response), named byte-bound source/footer/license/route and
response evidence artifacts, an exact row-count-weighted midpoint sampling schedule, contract-level
final-decision validation and the self-reference-free `output_artifact_manifest.jsonl`/
`calibration_audit.json` chain. The local structural fixture is explicitly
`STRUCTURAL_SYNTHETIC_CONTROL` and cannot establish source provenance or route feasibility. The
current schedule validator records a minimum of 373 contiguous windows for that fixture, exceeding
the frozen 100 successful-row-request envelope; it fails closed without changing the estimand.
Near-dedup count/rate must reconcile canonical affected IDs/pairs or a hash-bound execution
artifact. Missing bindings, arbitrary windows, overlaps, out-of-bounds offsets, manifest/metric or
audit evidence are `BLOCKED`. Model-neutral calibration does not require tokenizer fertility;
tokenizer yield/dose adequacy belongs to later 151ah/materialization or model-specific planning.
151ak remains `FROZEN — PREPARATION_BLOCKED — UNEXECUTED`; its proposed root was not created. The
focused suite is `30 passed, 1 skipped` and the compatible suite is `260 passed, 8 skipped` after
the same three documented collection exclusions. These are local checks only; route/source and
scientific gates remain blocked.

Document 151an is the current frozen, unexecuted **execution-ready metadata/footer feasibility
only** contract. Its pre-correction SHA-256 is
`435e0c25cedd7fd8fcb70862c637040300c2d5b201bfb5fa25c2b20232e71096`; its prior corrected SHA-256
is `572a14636dfc44f23cdff5ac536838ea671a488ddcd24968097bc4942bb0d4e4`; its strict-parser
correction SHA-256 is
`e23ae18d35791e91d05f094fe7c675871214df6a9fe9714a660ae703fe84a0ac`; and its current retry/bound
correction SHA-256 is
`937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79`. It freezes the exact
32-path immutable source identity, the single `parquet_footer_range` route-kind vocabulary,
direct immutable `/resolve/` routes, the exclusion of Dataset Viewer `/rows`, the new scratch root
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1`, exact seven top-level outputs,
separate LFS/full-object identity versus compact metadata-artifact hashes, a pure-Python
compact-Thrift parser for complete Parquet footer framing, two-stage trailer/exact-footer ranges,
shared HEAD role binding, explicit 429/503 and no-response retry semantics, actual response-byte
binding and `evidence/retry/` artifacts. The effective retry ceiling is `24`; nominal 32-shard
accounting is 97 base artifacts plus 24 retry artifacts plus seven top-level files = 128 files and
inodes, within the 128-attempt, 64 MiB-total, 4 MiB-single-response and 7,200-second ceilings.
Local validation is `40 passed, 2 skipped` focused and `270 passed, 9 skipped` compatible with the
same three exclusions plus the explicit independent-writer compatibility skip. The single
authorized 151an wave is recorded in Documents 151ao/151ap and is `BLOCKED` before source access:
HU `corpus-update` remained dirty at old base `9f17552`, and the byte-form home-usage `du`
preflight returned no parseable value. The reviewed three-commit chain was pushed ordinary
non-force to `c1a3127`, but HU synchronization was not attempted so unrelated HU work could not
be overwritten. The frozen root was not created; executor invocations, HTTP attempts, retries,
response bytes and artifacts are all zero. 151ao SHA-256 is
`5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46`; 151ap SHA-256 is
`aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468`. This does not establish
route unavailability or close the measurement-design gate. No new 151an execution is authorized
until the HU checkout is safely reconciled and preflight succeeds. The result does not authorize
source access, row sampling, corpus materialization, scoring, evaluation, training or readiness
to measure/train.

The primary gate remains `blocked_by_measurement_design`, with contributing
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure` and `ready_to_train` remain
false. Documents 151ai/151aj are reserved but uncreated. No 151ah execution, sample calibration,
full-shard or corpus-row download, corpus materialization, scoring, inference, evaluation,
GPU/Slurm, training, cleanup or Documents 152--154 action is authorized by these documents.

Document 151aq is the current bounded HU read-only operational diagnostic authority. It verified
the live/local `corpus-update` publication at `c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23`, the HU
checkout at old base `9f1755219ba003d4aaf962558b3c0512fc74f99a`, and exactly 42 status entries:
39 tracked `.D` worktree deletions plus three untracked top-level entries. The exact intersection
with the 13 paths in the published `9f17552..c1a3127` change set is zero. Its mandatory 30-second
`du -xsh` check returned exit 0, 32 stdout bytes, 0 stderr bytes and `14G`; the 30-second GNU
byte-form returned exit 0, 40 stdout bytes, 0 stderr bytes and exact `14687617024` bytes. The
capacity/inode/path checks passed read-only and the frozen 151an root remained absent. 151aq SHA-256
is `5a48d297ef5475550df41fd7e2baace4278acf54bbfb32bbfe455909dde7dbea`. The dirty HU checkout
still keeps 151an blocked by operational access; owner-controlled reversible reconciliation is
only a separately authorized next step. Documents 151an/151ao/151ap remain unchanged, and no
source/footer access, PyArrow, executor, retry, corpus, scoring, evaluation, GPU/Slurm, training,
cleanup or Documents 152--154 action is authorized.

Documents 151ar and 151as are now the current result and post-execution gate for the one
preservation-checked 151an wave. The HU checkout was safely fast-forwarded once from
`9f1755219ba003d4aaf962558b3c0512fc74f99a` to
`c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23` after the exact 42-entry status blob remained
unchanged (6,989 bytes, SHA-256
`71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9`, zero overlap). Mandatory
preflight and the independent PyArrow writer/parser check passed. The single 151an execution then
failed closed on the first frozen direct-route request returning non-retryable HTTP 302; no
redirect was followed, retries and response bytes were zero, and the scratch root remained absent.
151ar SHA-256 is `e531443254133a3ade95fcdf004420cc8726d28f337c7171c730937de3019967`; 151as SHA-256 is
`03c603265836320b173489a6659f91916c97db7ec78ebdd7b8faf0c1122a0ceb`. The narrow operational
gate remains `blocked_by_operational_access` due route integrity; the global gate remains
`blocked_by_measurement_design`; no retry, corpus, scoring, evaluation, GPU/Slurm, training or
Documents 152--154 action is authorized.

Document 151at is now the current frozen, unexecuted local/public-metadata-only correction
contract for the observed Hugging Face 302 route behavior. Its SHA-256 is
`d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa`. It preserves 151an’s exact immutable revision and 32 paths, permits zero or exactly one
validated absolute HTTPS 302 hop only to the official `xethub.hf.co`/`cdn.hf.co` suffixes, keeps
signed Location values secret-safe, strips Authorization/Cookie on cross-host requests, separates
121 logical request attempts from at most 242 physical HTTP hops, and retains the 64 MiB, 4 MiB,
128-file/inode and 7,200-second ceilings. The local executor/validators/tests implement this
protocol and repair the nested HTTPError response-read exception shadowing. Local follow-up commit
`de4a14e3370326173bdf04ce33356aae7826ddda` was published by ordinary non-force push. Document
151at was not executed. The one authorized 151an wave fast-forwarded HU while preserving the
42-entry dirty state, but failed closed on the mandatory 30-second home-usage `du` timeout before
PyArrow or source access. Document 151au is the append-only execution result (SHA-256
`a83d832efa7478e86fa6bfa555cfe70d900f5284bf1bc862a8e5ca696d43fd8e`) and 151av is the post-wave
gate (SHA-256 `d25789ddece62628a9cd6913eb1cbb94306816413a5b0b7768fec85a2709944a`). The operational
gate remains `blocked_by_operational_access`; the global gate remains
`blocked_by_measurement_design`; no route, corpus, scoring, evaluation, training or readiness
claim follows.

Document 151aw is the current documentation-only roadmap alignment authority. It reconciles the
restored `THESIS_RELEVANT_PAPERS_MASTER_MAP_TR.md`, historical Document 60, active scientific
Document 145 and bounded Document 151at without changing frozen results. OLMo/Pythia/Falcon remain
non-selected English-centric screening candidates; Qwen is the multilingual positive control.
vngrs remains only a conditional materialization candidate, trwiki is cross-domain control-only,
CulturaX is `excluded_access_blocked`, and OSCAR/mC4/HPLT/FineWeb2/Bella Turca remain
literature/provenance candidates pending exact evidence. The reviewed commit is now published, and
the authorized wave performed the preservation-checked HU fast-forward but stopped on the mandatory
home-usage preflight timeout before source access. No automatic retry is authorized; any future
wave requires a new explicit authorization after a successful bounded preflight. This does not
authorize training.
Document 151aw SHA-256 is
`d28cf560dc8ee3eba0ca435d81df2651f88d30ef6f412f1b83e8c4bd0b6255a8`.

Document 151ax is the current frozen, unexecuted local HU storage-preflight resilience
correction contract. Its pre-clarification SHA-256 is
`15bdc5a7ae0e0356254c5d5ffd5ad47b091f459a52689ce4c0cb1ecc9699ed22`; its current final
SHA-256 after the append-only post-run audit binding clarification is
`b32550966e29f3398239e7be778cb20e3344e427bbec6f664fdda062c0e9eaff`.
It makes `du -x -B1 -s /vol/fob-vol6/mi25/yesildau` the live exact-byte primary check with a
120-second bound; `du -xsh` remains a 30-second diagnostic and cannot alone block when the
exact-byte check passes below 30 GiB. It freezes mandatory `df -h`, `df -i`, resolved-root,
root-absence and HU-home-write-prohibition checks, plus a bounded 120-second `>500 MiB` regular
file manifest with explicit PASS/BLOCKED/INCOMPLETE and pre/post reconciliation semantics.
The final correction binds top-level PASS to both source-stage PASS and post-run-audit PASS;
source evidence remains preserved when the audit is BLOCKED or INCOMPLETE, and definitive audit
violations are distinguished from incomplete timeout/parse/reconciliation evidence. The local
implementation/test correction is unpushed and is recorded in narrow follow-up commit
`92460a00ec136dd885b4940184bee9d954da9106`, after predecessor `6ff9ceb13bbf2b9a4de19ba1db7788f11d239570`.
151ax does not authorize HU/network access, source/footer access,
151an/151at execution, corpus rows/full shards, sample calibration, materialization, scoring,
evaluation, GPU/Slurm, training or Documents 151ay/151az/152--154. The operational gate remains
`blocked_by_operational_access`; the global gate remains `blocked_by_measurement_design` and
`ready_to_measure`/`ready_to_train` remain false. The next separately authorized wave must cover
ordinary non-force push, preservation-checked HU fast-forward, corrected preflight and exactly one
bounded 151an/151at execution.

Documents 151ay and 151az record the latest explicitly authorized execution wave. It stopped
fail-closed before publication because live `origin/corpus-update` was
`2ff1cacdffd55820fdf9a8f633c2bc20bffac807`, not the required expected base
`de4a14e3370326173bdf04ce33356aae7826ddda`. No push, HU/SSH, fetch, merge, preflight, PyArrow,
source/footer HTTP or executor invocation occurred. 151ay SHA-256 is
`a98ba8b8ddcd95742e7956c76c3ffc7364ade716ed4d0a45c8a6ca8fe352b23b`; 151az SHA-256 is
`c161a0eac7fe2c619511a30419d1ae6168c76ea83d25e4922e18cec2d968ede5`. The operational gate is
`blocked_by_operational_access`; the global gate remains `blocked_by_measurement_design`, and a
new wave requires explicit resolution/approval of the remote-base contradiction.

Documents 151ba and 151bb record the next revised-base wave. The live remote base was verified as
`2ff1cacdffd55820fdf9a8f633c2bc20bffac807`; merge-base was identical, local ahead was 2 and
remote ahead was 0. Only the reviewed `6ff9ceb13bbf2b9a4de19ba1db7788f11d239570` to
`92460a00ec136dd885b4940184bee9d954da9106` chain was published by ordinary non-force push.
HU was preservation-checked and fast-forwarded exactly once from `2ff1cac...` to
`92460a0...`; the 42-entry status, 39 tracked `.D`, 3 untracked entries and status SHA-256
`71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9` remained unchanged, with
zero overlap against the two incoming paths. Corrected 151ax preflight then failed closed before
PyArrow/source access because exact-byte `du -x -B1 -s` timed out at 120 seconds (the diagnostic
`du -xsh` also timed out at 30 seconds); home usage was not accepted from the later post-run
measurement. The post-run audit completed PASS with an absent root and zero files/bytes, but it
does not reverse the preflight BLOCKED result. No executor invocation, request, hop, retry or
response byte occurred. An append-only post-wave read-only check later observed local and
`origin/corpus-update` at `210e47256a499d098da9879d7ade990527cdbe35`; this commit was not part of
the authorized push and was not pushed by LUNA-Worker 2. No additional push, fetch, merge, HU
operation or execution followed. The pre-observation hashes were preserved in 151ba/151bb;
their current SHA-256 values are 151ba
`d14c3b31b4d35517fbbcfaac2706b20f4108241c25f21b51c0e3157f0373ae26` and 151bb
`2ffaf1eed56a8c895dbb48715b4bab07d9e3d368363ee3a81dc7bdff2c34c606`. The operational gate
remains `blocked_by_operational_access`; the global gate remains `blocked_by_measurement_design`;
`ready_to_measure` and `ready_to_train` remain false. Documents 151ay/151az are unchanged.

Documents 151bc and 151bd record the subsequent HU-only prewarmed retry. No push, fetch, merge
or HU checkout movement was performed; `210e47256a499d098da9879d7ade990527cdbe35` remained
outside scope. The bounded HU helper did not return a remote result: a 30.004-second
read-only probe timed out with return code `null`, 226 stdout bytes containing only the SSH spawn
line and 0 stderr bytes. Therefore the retry did not freshly verify the expected HU HEAD
`92460a00ec136dd885b4940184bee9d954da9106`, the 42-entry dirty-state/status SHA, the frozen-root
absence, the large-file manifest or exact-byte home usage. Internal preflight, PyArrow and the
executor were not invoked; a bounded post-run audit probe also timed out at 30.005 seconds before
returning a remote result. 151bc SHA-256 is
`376c5e380ba1fa22262626b66b531d19f9333e168a2ffe3c86017b1218726edc`; 151bd SHA-256 is
`c9544bbe410c2d4353ef6b1f1c4c72debd269bb3122d0c0de559b46680d61683`. The operational gate
remains `blocked_by_operational_access`; the global gate remains `blocked_by_measurement_design`;
`ready_to_measure` and `ready_to_train` remain false. Documents 151ba/151bb are unchanged.

Document 151be's exact SHA-bound HU-only wave was subsequently authorized and executed exactly
once. Document 151bf records the result; its SHA-256 is
`e9a086f3be624ded0ac1271326ff57beefbd01b4a98dc936cb3ff6c135e1c9c5`. Connectivity, live
preservation, exact-byte home/cache prewarm, internal storage preflight, PyArrow independent
writer/parser and all 96 shard HEAD/trailer/footer requests passed. The terminal immutable
README/license request returned HTTP 307, while frozen 151at accepted only validated 302 CDN hops;
the executor therefore stopped fail-closed after logical attempt 97, HTTP hop 193, with zero retry
and no accepted output root. The single invocation is consumed. Document 151bg is the current
post-retry gate; its SHA-256 is
`80ed93e937f9fc1eda74f9ae90df76823d957688e803f92bfd9df4c17aa86d75`. A future retry requires a
new append-only license/README 307 semantics contract and exact authorization. Corpus rows/full
shards, 151ak sample calibration, 151ah materialization, scoring, model/tokenizer, GPU/Slurm,
training, cleanup/deletion and a second executor invocation remain unauthorized; the global gate
remains `blocked_by_measurement_design`.

Document 151bh is the current frozen, unexecuted license HTTP-307 resolve-cache repair and
single-retry contract; its SHA-256 is
`57d8dbd0b84f5914e9b249b12d888cb1aa7c2ea6b6733197aaf117dbcb801853`. It changes only the exact
immutable `license_attribution` README route: one HTTP 307 may resolve to the exact same-origin
`huggingface.co/api/resolve-cache/datasets/vngrs-ai/vngrs-web-corpus/<frozen-revision>/README.md`
path with a secret-safe `etag`/optional `download=true` query shape. Shard 302 CDN semantics and
all 151an attempt/hop/byte/file/inode/zero-row bounds remain unchanged. The local implementation
is frozen in commit `37a7d29a182f049054483915f4ceee5bc7fdd1d4` and the compatible suite passed
380/380. No publication, HU synchronization, source request
or executor invocation is authorized without separate exact SHA-bound approval. The future wave,
if authorized, permits exactly one new executor invocation; Documents 151bi/151bj are reserved for
its result/gate.

## HU Home Storage Rule and Approved Frozen-Artifact Exception

**Never use the shared HU student home fileserver as a general experiment-artifact store.**

The HU home directory is:

```text
/vol/fob-vol6/mi25/yesildau
```

On 13 July 2026, this project had accumulated approximately **474 GB** there, although the shared
service is planned around roughly **10 GB per student**. Repeated checkpoints, optimizer states,
caches, model snapshots, and evaluation trees filled the filesystem and contributed to a service
outage. The incident also drove the filesystem and inode usage to 100%, preventing even Git from
updating `.git/FETCH_HEAD`.

After migration, home-resident regular files were reduced to **7.88 GiB**. On 30 July 2026, Ralf
Moritz explicitly confirmed in writing that current home usage below **30 GB** is acceptable and
authorized copying the approximately **6.2 GB** represented by the two frozen selected Qwen M1
models from `/vol/tmp2` into home. This is a narrow durability exception for selected model-only
artifacts, not permission to return run trees, ordinary checkpoints, caches, datasets, or logs to
home. Every agent must protect this recovered and explicitly bounded state.

### What May Remain in Home

The following durable project material may remain on the home filesystem:

- source code and Git metadata;
- small YAML/JSON configs;
- manifests and checksums;
- documentation and compact result summaries;
- small launcher scripts and environment metadata;
- the required `xfer-relearn` Conda environment;
- explicitly selected frozen model-only artifacts when they have manifests and SHA-256 checksums,
  the copy is separately authorized, and projected total home usage remains below 30 GB.

### What Must Go to Scratch

The following must be written to `/vol/tmp/yesildau`, `/vol/tmp2/yesildau`, or another explicitly
approved HPC scratch filesystem:

- training checkpoints and final model weights, except for the explicitly authorized frozen
  selected model-only home backup above;
- `optimizer.pt`, scheduler state, RNG state, and resumable trainer state;
- Hugging Face, Transformers, Torch, datasets, and compiler caches;
- generated corpora and expanded datasets;
- raw evaluation outputs, logits, and checkpoint sweeps;
- TensorBoard/W&B files and verbose logs;
- temporary files, extracted archives, and downloaded model snapshots.

Scratch is not a backup and has no retention guarantee. Scientifically important selected
artifacts must be identified with a manifest and checksum before any cleanup, migration, or
expiry-sensitive operation. The selected Qwen home copy is a durability copy; ordinary scratch
retention policy remains unchanged.

There is no project-level quota or conservative occupancy limit imposed here for `/vol/tmp` or
`/vol/tmp2`. These scratch filesystems may be used heavily, including for large temporary run
families, provided the job fits the space and inodes actually available at submission time. Scratch
outputs may be deleted after the run according to the retention rules below. High-volume
experiment execution remains on scratch; only the narrow authorized frozen-artifact backup may
place model weights in HU home.

## Mandatory Storage Preflight

Before every new training family, scale-up, model download, corpus generation, or broad evaluation
sweep on HU, inspect both capacity and inode availability:

```bash
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
du -xsh "$HOME_ROOT"
df -h "$HOME_ROOT" /vol/tmp /vol/tmp2
df -i "$HOME_ROOT" /vol/tmp /vol/tmp2
```

Also resolve every planned output path because a repository-local path may or may not be a symlink:

```bash
readlink -f /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/runs
readlink -f /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/artifacts
```

For one coordinated parallel job family with a frozen candidate list, common experiment plan, and
known scratch layout, a single complete preflight immediately before the submission wave covers
all sibling jobs. Do not repeat the same `du`, `df`, inode, and path checks separately for every
job. The family preflight must enumerate all jobs and resolved destinations and use their combined
checkpoint, cache, dataset, log, temporary, and evaluation estimate. Repeat it only when the job
set or paths change, a later submission wave begins, the estimate changes materially, or enough
time/external activity has passed that the recorded filesystem state is no longer trustworthy.

Parallel jobs are allowed. There is no project-level limit on their combined scratch use beyond
the capacity and inodes actually available at submission time. The strict limit remains no
general run output on HU home, not ordinary or heavy concurrent use of `/vol/tmp` or `/vol/tmp2`.

Do not submit the job when any of the following is true:

- projected home usage is at or above 30 GB, or current usage is unexplained;
- a training/evaluation output path resolves onto `/vol/fob-vol6` (the dedicated authorized
  frozen-artifact archival procedure is the only exception);
- the expected checkpoint count and approximate total size have not been estimated;
- cache, log, dataset, and model-output locations are still implicit.

Scratch capacity and inode checks are operational planning signals, not a project-imposed usage
limit. A run may consume most of the currently available scratch allocation when that is useful;
reduce the run only when it would not fit or would predictably fail. If a home-placement check
fails, stop and fix storage placement first. Do not launch training or evaluation into home and
plan to move files later.

## Required Job Configuration

Every HU launcher must use an explicit scratch root and route all high-volume writes there. A
typical setup is:

```bash
SCRATCH=/vol/tmp2/yesildau/<experiment-family>
mkdir -p "$SCRATCH"/{runs,cache,logs,tmp}

export HF_HOME="$SCRATCH/cache/huggingface"
export TRANSFORMERS_CACHE="$SCRATCH/cache/huggingface"
export XDG_CACHE_HOME="$SCRATCH/cache"
export TORCH_HOME="$SCRATCH/cache/torch"
export TMPDIR="$SCRATCH/tmp"
```

The training or evaluation config must use an absolute scratch `output_root`. Slurm stdout and
stderr must also point to scratch for large or repeated jobs. Never rely on a relative `runs/`,
`artifacts/`, `outputs/`, or `.cache/` path unless `readlink -f` proves that it resolves to an
approved scratch filesystem.

Before submitting, print and record:

- the resolved output root;
- the resolved cache root;
- the number of expected checkpoints;
- estimated bytes per checkpoint and estimated family total;
- the intended retention policy after completion.

## Checkpoint and Artifact Retention

During an active run, resumable optimizer state may be retained on scratch. After the run:

1. Evaluate and identify the selected best/final checkpoint before cleanup.
2. Preserve model-only weights, config, tokenizer files, run metadata, and compact evaluation
   summaries needed for reproducibility.
3. Generate a manifest and SHA-256 checksum for every frozen selected model.
4. Treat duplicate checkpoints, `optimizer.pt`, scheduler state, RNG state, and reproducible caches
   as cleanup candidates after the selected artifact is verified.
5. Reproducible scratch intermediates, duplicate checkpoints, optimizer/trainer state, caches, and
   verbose logs may be deleted after the selected artifact and compact evidence have been verified.
   Explicit user approval is required only before deleting or overwriting a selected/frozen model,
   unique dataset, canonical manifest, or non-reproducible scientific result.
6. Record the retained artifact path and any cleanup or migration in the corresponding numbered
   documentation report.

Do not copy large output trees into Git or GitHub. Publish code, configs, manifests, hashes, and
compact summaries only.

## Mandatory Post-Run Audit

After every training family or large evaluation sweep, run the storage checks again. A coordinated
parallel family needs one post-run audit after all sibling jobs in that wave reach terminal state,
not one identical audit per sibling job:

```bash
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
du -xsh "$HOME_ROOT"
df -h "$HOME_ROOT" /vol/tmp /vol/tmp2
df -i "$HOME_ROOT" /vol/tmp /vol/tmp2
```

Verify that no new large regular file was written into home:

```bash
find "$HOME_ROOT" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
```

The run is not operationally complete until its result and storage audit are documented. Report
the Slurm job ID, node, final state, output location, selected checkpoint, approximate retained
size, and whether stderr was clean.

## Slurm Operating Practice

- Inspect the queue before submission and after submission.
- Estimate runtime from the closest comparable completed run and report the expected range.
- Confirm that the job entered `RUNNING`, that the intended node/GPU is used, and that stderr does
  not show an immediate failure.
- Do not submit duplicate jobs merely because output is temporarily quiet.
- Do not leave hidden interactive password prompts or unnecessary long-lived monitoring processes.
- When the user asks for a later check, submit the work, report the estimated duration, and leave
  the job running for the user to revisit unless explicitly asked to wait.

### Aggressive execution mode

When the user explicitly asks for aggressive execution (for example, to use all suitable cards or
to proceed across the available server), maximize throughput across all currently usable GPU
resources instead of waiting for one preferred node or GPU model. The following rules apply:

- Inspect every GPU node and GPU type currently visible to Slurm, including idle V100, RTX 6000,
  RTX A6000, A100, RTX 3090, and other compatible resources. Do not assume that an idle node is
  the only useful resource or that a busy preferred model blocks the experiment.
- Run a bounded one-task compatibility/clean-device probe on each plausible GPU class or node
  group, then immediately fan out to every probe-passing card that has capacity. A card is usable
  only after its allocated-device guard passes and the evaluator/model is compatible with it.
- Use heterogeneous node-specific arrays when GRES types differ. Preserve a per-node/per-GPU
  ledger of node, GPU type/UUID, guard result, compatibility result, and assigned task IDs.
- Use ordinary one-GPU Slurm allocations; do not use `--exclusive`, kill another user's process,
  or cancel unrelated jobs. Weekend timing does not override those protections.
- If a card is contaminated or incompatible, let its bounded probe fail closed, exclude that
  resource or node group from the current wave, and continue using other probe-passing cards. Do
  not repeatedly recycle a failing array onto the same contaminated GPU.
- Do not count guard failures, CUDA-compatibility failures, OOMs, or partial outputs as scientific
  results. Retry only affected task IDs after the allocation strategy changes and the new target
  passes a fresh probe.
- For a later submission wave, repeat storage/path/inode preflight and inspect the queue again.
  Aggressive mode increases parallelism but does not waive home-storage, reproducibility,
  no-duplicate, or post-run audit rules.
- Report the full resource sweep, active task count, excluded resources and reasons, expected
  throughput, and next check time to the user before returning control.

## Scientific and Documentation Discipline

- Keep planned comparisons controlled. State which variables changed and which remained fixed.
- Distinguish exact storage from prompt-robust retrieval/binding.
- Do not select thresholds, checkpoints, or metrics after seeing results without labeling the
  decision exploratory.
- Record failed runs and methodological corrections; they are part of the thesis evidence.
- Add each run to the next appropriate chronological document under `documentation/` with job IDs,
  configs, seeds, output paths, metrics, interpretation, and next decision.
- Never claim a stage is complete without checking its precommitted gate and frozen-artifact state.

## Local Editing and Git

- Work with existing user changes; never revert unrelated modifications.
- Keep commits narrowly scoped and do not commit large generated outputs.
- Use the existing GitHub push/pull workflow to synchronize code with HU.
- Secrets and `.env` contents must never be printed, committed, or copied into documentation.
- Prefer existing scripts and repository conventions over one-off remote commands. When a new
  remote procedure is necessary, add or update a reusable script and document it.

## Stop Conditions

Stop and ask the user before proceeding when:

- an operation would delete or overwrite a selected/frozen model, unique dataset, canonical
  manifest, or non-reproducible scientific result;
- a training/evaluation output path unexpectedly resolves to the shared home filesystem;
- home usage has materially increased unexpectedly or reaches 30 GB;
- the current documentation and remote state disagree in a way that changes the scientific plan;
- credentials, destructive migration, or an unapproved external publication would be required.

The storage incident must not recur. Correct artifact placement is part of experiment correctness,
not an optional infrastructure detail.

## Local Codex CLI Orchestrator

The workspace-level two-role CLI control plane lives under `.agents/`. It coordinates a read-only
Sol director/reviewer and a bounded Luna executor across this non-Git workspace and its separate
`transfer-vs-relearning/` and `syntheticFacts/` Git repositories.

The orchestrator is a control mechanism, not a source of scientific or operational authority:

- this `AGENTS.md`, the current user instruction, applicable frozen contracts/gates, and
  `LUNA_WORKER_CURRENT_HANDOFF.md` remain authoritative;
- session history, `.agents/GOAL.md`, a model-produced decision, or an earlier authorization may
  not expand those authorities;
- only `local_read_only` and `local_write` scopes may be dispatched automatically;
- HU/SSH, Slurm/GPU, training/evaluation/inference, downloads, push/publish, deletion/cleanup,
  credentials, frozen-artifact mutation, and other external/destructive actions must stop for a
  new exact user authorization even if a persistent session remembers an older authorization;
- the workspace root must never be treated as one Git repository; inspect the two configured repos
  separately and preserve their pre-existing dirty and untracked state;
- unexpected changed paths stop the loop without reset, restore, checkout, cleanup, or automatic
  revert;
- `.agents/runs/` and `.agents/state/` are local orchestration evidence, not scientific results and
  not a substitute for required numbered documentation.

Read `.agents/POLICY.md` and `.agents/GOAL.md` when operating through the orchestrator. Use
`python3 .agents/orchestrator.py doctor` before bootstrap or execution, and start with
`python3 .agents/orchestrator.py run --dry-run` after defining a bounded active goal.
