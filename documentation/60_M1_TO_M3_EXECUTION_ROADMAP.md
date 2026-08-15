# 60 - M1 To M3 Execution Roadmap

Historical baseline last updated: 2026-07-11

## Current Roadmap Status — 2026-08-09

This file preserves the historical SmolLM2 M1-to-M3 execution ladder and its failures. It is no
longer the authority for opening a new training family. The current literature-first roadmap is
[`145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md`](./145_LITERATURE_FIRST_M1_MODEL_AND_TURKISH_ADAPTATION_ROUTE_TR.md).
The role/authority reconciliation for the restored literature map, this historical roadmap,
Document 145 and the bounded vngrs route contract is
[`151aw_LITERATURE_MODEL_CORPUS_AND_M2A_M2B_ROADMAP_ALIGNMENT_TR.md`](./151aw_LITERATURE_MODEL_CORPUS_AND_M2A_M2B_ROADMAP_ALIGNMENT_TR.md).

The July execution path below must not be resumed as written: the completed Qwen Wikipedia-only
pilot and the supervisor realignment replaced it with a read-only provenance and corpus-selection
stage. The current sequence is:

1. **M1 source-model audit:** compare OLMo-2-0425-1B, Pythia-1.4B and Falcon-RW-1B as
   English-centric candidates; retain Qwen2.5-1.5B as the multilingual positive control.
2. **Turkish corpus literature/audit matrix:** compare `vngrs-web-corpus`, Turkish OSCAR/mC4,
   HPLT Turkish, FineWeb2 Turkish, CulturaX-derived Turkish data and Bella Turca. Tiny–Medium
   Turkish BERT, Turkish tokenizer, cosmosGPT and SindBERT are direct model/corpus precedents;
   HPLT/FineWeb2/CulturaX/Bella Turca are candidate data-construction routes, not automatically
   selected training data.
3. **Facts-free Turkish manipulation check:** only after model and corpus evidence is resolved,
   determine a precommitted Turkish dose using held-out Turkish PPL/capability and English
   retention.
4. **Parallel sibling arms:** from the same frozen M1, run M2-A with general Turkish corpus and
   M2-B with the same budget plus controlled Turkish factual re-exposure. M2-B factual tokens
   must replace matched neutral Turkish tokens rather than increase the total budget.
5. **Scale only after the gate:** no 2,500/25,000-fact expansion or second model family before
   the manipulation check and provenance/contamination gates pass.

Candidate names in this pointer are not selections. OLMo/Pythia/Falcon remain screening
candidates with different provenance strengths; Qwen has a different role as the completed
multilingual positive control. Likewise, vngrs is only a conditional materialization candidate,
trwiki is the cross-domain control, CulturaX is access-blocked, and the remaining corpus names are
literature/provenance candidates pending exact evidence.

Current gate: `blocked_by_measurement_design`; contributing blocker:
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure=false` and
`ready_to_train=false`. No HU/Slurm/training/corpus materialization action is authorized by this
pointer. The historical phases below remain evidence of the previous plan and its outcome, not a
new execution request.

## Purpose

The body below was the active execution roadmap after the direct-aware acquisition recipe
demonstrated strong English fact learning at 50 facts but failed the complete prompt-robust gate
at 500 facts. It now serves as the historical record of the blocked scale-up, artifact analysis
and controlled 500-fact remediation; it must not be used to open a current M2/M3 run.

No later phase starts before the preceding gate is evaluated and documented.

## Operations Protocol

For every submitted job:

1. record the job ID;
2. check queue/start state once;
3. report the expected average duration and a safe duration range;
4. do not run a local sleep command;
5. leave the Slurm job running;
6. inspect it when the user next requests status;
7. document metrics and decisions before opening the next scale.

## Phase A - Close The 500-Fact Run

Completed evaluation waves:

- checkpoints 25/50/75: jobs `391073` through `391075`;
- checkpoints 100/125/150: jobs `391076` through `391078`.

Later completed waves:

- checkpoint 175: job `391079`;
- checkpoint 200: job `391080`;
- checkpoint 225: job `391081`.
- checkpoint 250: job `391083`;
- checkpoint 252: job `391084`.

Expected duration per parallel wave:

- average: approximately 6 minutes;
- safe range: 6-8 minutes.

500-fact gate:

- exact-prefix top-1 at least 450/500;
- held-out direct top-1 at least 400/500;
- held-out QA top-1 at least 400/500;
- direct/QA overlap at least 350/500.

Decision rule:

- if checkpoint 175, 200, or 225 passes, stop evaluating later checkpoints;
- if none passes but the curve remains positive, evaluate only checkpoints 250 and 252;
- primary M1-scale checkpoint: earliest checkpoint that passes;
- secondary analysis checkpoint: checkpoint with the highest robust overlap.

Final outcome:

- checkpoint 250: 451 exact, 317 direct, 349 QA, 277 overlap;
- checkpoint 252: 450 exact, 320 direct, 344 QA, 276 overlap;
- no checkpoint passed the complete gate;
- checkpoint 250 is retained as the analysis checkpoint;
- Phase C is blocked until a new controlled 500-fact recipe passes the same gate.

## Phase B - Freeze The Learned-Fact Subset

For downstream M2/M3 eligibility, a fact must satisfy all three English conditions at the
selected checkpoint:

```text
exact-prefix rank 1
AND direct rank 1
AND QA-matched rank 1
```

This is the `triple-robust` learned-fact subset.

Status: completed for checkpoint 250. The frozen subset contains 265/500 facts. Branch and
name-type balance are acceptable, but relation performance is highly uneven: 85 profession,
74 lives-in, 53 born-in, 29 studied-at, and 24 works-at facts are triple robust. Detailed
results are in `61_M1_CHECKPOINT_250_TRIPLE_ROBUST_AUDIT.md`.

The active remediation is the checkpoint-250 balanced-negative ranking continuation defined
in `62_M1_CHECKPOINT_250_RANKING_CONTINUATION_PLAN.md`. It remains at 500 facts and must pass
the unchanged gate before Phase C can open.

Outcome: the remediation failed. Checkpoint 35 reached 452 exact, 321 direct, 343 QA, 277
direct/QA overlap, and 264 triple robust; checkpoints 70 and 105 regressed. The weak-relation
candidate collapse remained. Checkpoint 250 remains the analysis checkpoint, and Phase C is
still blocked.

Before freezing, audit:

- Branch A/B counts;
- relation counts;
- low/medium/high frequency counts;
- English-like/Turkish-like name counts;
- name-rarity and popularity counts;
- `born_in` versus `lives_in` relation-binding errors;
- candidate inventory and dataset hashes;
- probe/template leakage.

## Phase C - 500 Subjects / 2,500 Facts

Start only after a 500-fact recipe passes the complete gate. The current direct-supervision
recipe did not pass, so this phase must not be launched yet.

Dataset contract:

- 500 nested subjects;
- 2,500 facts;
- 17,500 training rows;
- seven rows per fact;
- five relations;
- held-out direct paraphrases;
- full candidate inventories.

Matched training recipe:

- base SmolLM2-360M;
- answer-only full-parameter training;
- 36 epochs;
- micro-batch 50;
- gradient accumulation 50;
- effective batch 2,500;
- 252 optimizer updates;
- learning rate `1e-4`;
- constant-with-warmup scheduler;
- no weight decay.

Estimated training duration:

- average: approximately 50 minutes;
- safe range: 45-65 minutes.

Initial evaluation wave:

- checkpoints 25/50/75 only;
- three jobs in parallel when GPU capacity permits;
- expected wall time: approximately 30 minutes;
- safe range: 25-40 minutes.

2,500-fact gate:

- exact-prefix at least 2,250/2,500;
- direct at least 2,000/2,500;
- QA at least 2,000/2,500;
- direct/QA overlap at least 1,750/2,500.

## Phase D - Scale Audit Before Full M1

If 2,500 facts pass, compare 50, 500, and 2,500 facts on:

- optimizer update required for first gate pass;
- exact/direct/QA learning curves;
- relation-level acquisition rate;
- triple-robust fraction;
- frequency and metadata effects;
- runtime and GPU utilization;
- held-out loss versus ranking metrics.

Use this audit to determine whether 36 exposures remain necessary at full scale.

## Phase E - Full 5,000-Subject / 25,000-Fact M1

Prepare only after the scale audit.

Nominal data size:

- 5,000 subjects;
- 25,000 facts;
- 175,000 seven-format rows.

Compute readiness:

- run a small 3-GPU distributed parity smoke test first;
- verify DDP checkpoint and metric parity against one-GPU training;
- preserve effective batch and optimizer semantics;
- estimate one-GPU runtime at approximately 8-10 hours;
- estimate validated 3-GPU runtime at approximately 3-4 hours.

Full M1 uses the same precommitted percentage gate unless the scale audit motivates a change
before results are observed.

## Phase F - Freeze Final M1

Freeze and hash:

- selected M1 checkpoint;
- base and trained model manifests;
- training config;
- source and derived dataset manifests;
- exact/direct/QA result files;
- triple-robust learned-fact list;
- subgroup distributions;
- branch balance;
- contamination/leakage audit.

After this freeze, M1 recipe and learned-fact membership do not change.

## Phase G - M2 Generic Turkish Adaptation

M2 contract:

- start from frozen M1;
- use generic clean Turkish corpus;
- include no synthetic target facts;
- preserve the precommitted adaptation budget;
- evaluate only the frozen M1 learned-fact subset for causal transfer analysis.

Measure:

- English retention;
- Turkish zero-shot retrieval;
- relation-level transfer;
- Branch A/B parity before Turkish fact repetition;
- robustness across Turkish prompt forms.

## Phase H - M3 Turkish Repetition/Relearning

M3 uses the same adaptation budget as M2 but adds Turkish repetitions only for Branch B
facts.

Interpretation:

- Branch A: transfer-only condition;
- Branch B: Turkish reaffirmation/relearning condition.

Primary comparison:

```text
(M3 Turkish retrieval - M2 Turkish retrieval) for Branch B
versus
(M3 Turkish retrieval - M2 Turkish retrieval) for Branch A
```

This difference-in-differences analysis separates transfer from Turkish-side relearning while
controlling the English acquisition history.

## Model Policy

Do not change the model during this scale ladder. SmolLM2-360M has demonstrated successful
storage and robust extraction at 50 facts. A larger model becomes a new experimental branch
only if the corrected recipe reaches a reproducible capacity boundary.
