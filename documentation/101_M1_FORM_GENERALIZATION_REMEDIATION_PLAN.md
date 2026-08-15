# 101 - M1 Form-Generalization Remediation Plan

**Date:** 2026-07-18
**Status:** Planned; implementation and HU submission are gated by this document
**Authority:** Phases 1--2 of `100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md`

## 1. Decision and scope

M2 remains **HOLD**. This plan defines one matched 100-subject/500-fact English M1 remediation.
It tests whether form-balanced acquisition improves genuinely held-out prompt access without more
factual supervision. It does not launch M2, M3, the 500-subject control, or final M1.

The sole manipulation is the per-fact acquisition-form curriculum:

| Condition | Curriculum | Purpose |
|---|---|---|
| Control | One subject-assigned Form A or B, as in WP1B | Re-establish single-form baseline under selected WP5 recipe |
| Intervention | Both Forms A and B for every fact | Test form coverage rather than added exposure |

Form C is never used for training. It is the genuinely held-out form. No result here is final M1
evidence or Turkish-transfer evidence.

## 2. Scientific basis and frozen population

WP1B found 100% seen retrieval but 39.0%/38.8% crossed retrieval after swapping every subject's
Form-A/Form-B assignment. WP5 selected SmolLM2-1.7B, LR `5e-5`, answer-only loss,
`supervise_eos: false`, update 252; its robust three-form intersection nevertheless remained
52.4%/50.1%, below the 70% gate. This plan tests whether form coverage alone resolves that gap.

Both conditions use the identical existing Relation V2 100-subject acquisition subset and five
relations (`profession`, `born_in`, `lives_in`, `field_of_study`, `works_in_industry`): 500 facts.
Subject IDs, answers, Branch labels, name type/rarity, popularity, frequency metadata, candidate
inventories, and base model are fixed. Branch is not an English treatment: both branches receive
identical acquisition treatment.

Forms A/B/C, direct scaffold (`{question}`), QA scaffold (`Question: {question}\nAnswer:`), answer
normalization, top-1 scoring, exact-prefix evaluator, generic-capability suite, and error taxonomy
are frozen from the pre-M2 suite. Every fact is evaluated in six existing cells: A-direct, A-QA,
B-direct, B-QA, C-direct, C-QA. The existing 3,000-probe registry is retained byte-for-byte.

A new Form D is additionally frozen before implementation and is never used in either curriculum:
`What job does {subject} work in?`; `Where was {subject} born?`; `Where does {subject} live?`;
`What did {subject} study?`; and `What industry does {subject} work in?`, in the relation order
above. Form D is evaluated in both scaffolds, adding 1,000 probes. The resulting immutable
four-form registry contains 4,000 probes. Candidate, answer, and leakage audits must confirm that
the new wording does not introduce a factual or prompt overlap; it is used identically by both
conditions.

## 3. Matched-budget curriculum contract

| Quantity | Frozen value |
|---|---:|
| Facts / training rows / validation rows | 500 / 3,500 / 500 |
| Rows per fact | 7 |
| Epochs / effective batch / updates | 36 / 500 (10 x 50) / 252 |
| Scaffolds | 4 direct + 3 QA per fact; two template families |
| Loss and final EOS label | Answer-only; EOS disabled |
| Answer-token exposure | Identical total and per-fact count across conditions |
| Endpoint | Update 252 only |

The fixed row-slot sequence is `direct, qa, direct, qa, direct, qa, direct`. Inputs, answers,
block size, row ordering from `data_seed`, batching, scheduler, warmup, clipping, precision,
checkpoint schedule, and base weights are matched. Thus the intervention cannot gain through more
rows, answer tokens, updates, epochs, or scaffold-family count.

### Control

The deterministic, feature-balanced WP1B original 50/50 subject assignment is retained. All five
facts for a subject use its assigned A or B form in all seven row slots. Seed/data seed is 42/42.
The old swapped assignment remains an integrity reference; it is not an additional discovery model.

### Balanced A+B intervention

Every fact uses both A and B among the same seven slots. The form receiving four rows has two
direct and two QA rows; the other has two direct and one QA row. A deterministic per-fact schedule
balances which form receives the four-row share. Across 500 facts Form A and Form B each receive
exactly 1,750 rows, while direct/QA totals remain 2,000/1,500. The allocation must be audited
across relation, Branch, name type, name rarity, popularity, and every relation-frequency bucket.

The intervention cannot add Form C, a third scaffold, augmentation rows, epochs, or answer labels.
It may contain more unique rendered prompts because A+B coverage is precisely the intervention;
the number of template families remains two.

## 4. Frozen recipe

The discovery runs use the WP5 Pareto recipe unchanged:

```text
base model: HuggingFaceTB/SmolLM2-1.7B from existing pinned manifest
learning rate: 5e-5
objective: answer-only causal loss
supervise_eos: false
epochs/effective batch/updates: 36 / 500 / 252
discovery seed/data seed: 42 / 42
selection endpoint: update 252
```

Other fields inherit `configs/training/pre_m2_wp5_lr5e-5_eos_false.yaml`: block size 128,
constant-with-warmup, 0.02 warmup, zero weight decay, max grad norm 1.0, bf16, and gradient
checkpointing. Config differences may only be run identity, dataset paths/hashes, scratch outputs,
and curriculum label. Intermediate checkpoints are resumability artifacts, never a selection grid.

## 5. Required implementation and integrity gates

Before a HU preflight or smoke job, implementation must add versioned dataset/config/launcher
assets and tests proving:

1. Both conditions have 3,500/500 rows, 500 facts, and seven rows per fact.
2. Fact IDs, answers, metadata, relation/Branch counts, total and per-fact answer-token labels are
   identical; direct/QA totals are 2,000/1,500 in both.
3. The control preserves 50/50 subject A/B assignment; the intervention gives every fact both A/B
   under both scaffolds, has exactly 1,750 A and 1,750 B rows, and never uses C.
4. Both have two scaffold/template families, 36 epochs, batch 500, and exactly 252 estimated steps.
5. Normalized training prompts do not overlap any Form C or Form D probe for the same fact.
6. The four-form registry preserves the 3,000 historical probes byte-for-byte, adds 1,000 frozen
   Form-D probes, has 100 per relation-form-scaffold cell, and has no duplicate fact/cell or
   altered historical prompt, answer, or candidate value.
7. Configs match on all frozen model/optimizer fields; manifests live-hash base weights, datasets,
   configs, probe registry, and code revision.
8. The answer-only collator masks EOS in both conditions; a one-batch smoke verifies finite loss,
   nonempty answer labels, gradients, expected memory, scratch-only writes, and clean stderr.

Failed integrity checks block training and cannot be waived by manual inspection. Manifests must
include hashes, row/form/scaffold totals, subgroup balance, allocation, steps, storage estimates,
resolved output/cache paths, and retention classification.

## 6. HU storage and execution contract

Before any HU action, read `ssh-client/README.md`, inspect both repository statuses, and create a
new narrowly named scratch-safe launcher. All high-volume writes must resolve to `/vol/tmp/yesildau`
or `/vol/tmp2/yesildau`, e.g. `/vol/tmp2/yesildau/m1_form_generalization_v1/` with separate
datasets, training, evaluation, manifests, cache, logs, and tmp trees.

Record home usage, capacity and inode state for home/`/vol/tmp`/`/vol/tmp2`, resolved paths,
checkpoint count/size/family estimate, and cleanup policy before submission. WP5 gives an expected
training duration of about 50--53 minutes and a safe range of 45--65 minutes; a smoke is about two
minutes. Until a measured estimate is frozen, reserve the conservative WP5 upper bound of 225 GB
and 11 checkpoints per condition (450 GB family). Any home path, insufficient capacity/inodes, or
unresolved path blocks submission.

After training and evaluation, repeat the storage audit and document job ID, node, state, runtime,
selected checkpoint, retained size, output path, and stderr status. Preserve model-only endpoint
files, config/tokenizer, manifests, compact evidence, and SHA-256 hashes. Optimizer/trainer state,
duplicate checkpoints, caches, and verbose logs are scratch cleanup candidates only after verified
endpoint evidence; never delete a selected artifact without explicit authorization.

## 7. Frozen discovery evaluation and gates

All 500 facts are denominator-fixed: missing/invalid/generation failures are incorrect. Report
global, relation, Branch, name-type, rarity, popularity, and frequency summaries. Global and
per-relation results are hard gates.

| Gate | Requirement |
|---|---|
| Integrity/contamination | Every Section 5 audit passes; no leakage |
| Exact-prefix | At least 450/500 (90%) globally |
| Each A/B/C/D form-scaffold cell | At least 80% globally and 80/100 in every relation-cell |
| Robust intersection | At least 350/500 (70%) correct in all eight cells and 70/100 in every relation |
| Generic retention | WikiText-2 PPL ratio <= 1.25 |
| Preferred Pareto band | PPL ratio < 1.10; 1.10--1.25 needs explicit documented decision before scale-up |
| Generic behavior | No broad common-knowledge, generation, empty-output, or EOS-ending collapse |

Exact-prefix is storage evidence, not a substitute for held-out retrieval. Forms C/D and the
eight-cell intersection decide prompt generalization. No gate may be relaxed post-result; paired statistics
and confidence intervals are descriptive, not exceptions. The control should be compatible with
the seed-42 WP5 reference (100% exact, 52.4% robust three-form, PPL 1.082, zero generic EOS
endings); material deviation first triggers a compatibility audit, not a treatment interpretation.

## 8. Replication and decision paths

Run seed-42 control and intervention. The intervention advances only if it passes every gate and
the control has no unresolved compatibility issue. If seed 42 passes, replicate the matched pair
with seed/data seed 43 under unchanged gates. Both intervention seeds must pass before the
curriculum is promoted.

- If seed 42 fails, do not scale and do not run seed-43 confirmation; document the diagnosis.
- If seed 42 passes and seed 43 fails, do not promote or scale; retain evidence and plan anew.
- If both pass, run the Phase 3 paired-relation control with the passing curriculum. The 500-subject
  scale plan remains a separate future document.
- Integrity, storage, or evaluator failure is operational, not scientific: repair, revalidate, and
  do not select partial metrics.

## 9. Later M1--M3 boundaries

This plan does not define M2/M3 corpus displacement. M3 will be the matched counterpart to M2's
clean generic Turkish adaptation, plus Branch B Turkish repetition as its single intended causal
difference; it is not a Branch-B-only dataset. Any fixed-token generic-corpus substitution rule is
precommitted later in the dedicated M2/M3 plan.

Primary M2/M3 analysis will also not automatically use all 25,000 final-M1 facts. It will use only
facts passing a predeclared English learned-fact definition whose membership is frozen after final
M1. The whole 25,000-fact set may be reported separately as secondary/intention-to-train analysis.

## 10. Deliverables before submission

1. Versioned matched datasets, configs, launcher, manifests, and tests.
2. Frozen evaluation registry/configuration with hashes.
3. Passing local tests and one-batch GPU smoke.
4. HU storage/path preflight and runtime/checkpoint estimate.
5. One discovery job per condition, completion/storage audit, and next chronological results report.

Until items 1--4 pass, this plan authorizes no HU training. Until both seed gates pass, M2 and
larger-scale M1 remain HOLD.
