# 103 - M1 Canonical Plus Form-Diversity Remediation Plan

**Date:** 2026-07-19

**Status:** Frozen next experiment plan; implementation and HU submission remain gated

**Parent evidence:** `101_M1_FORM_GENERALIZATION_REMEDIATION_PLAN.md` and
`102_M1_FORM_GENERALIZATION_REMEDIATION_RESULT.md`

**Scope:** One new SmolLM2-1.7B seed-42 discovery model at 100 subjects/500 facts. No seed-43
replication, 500-subject scale-up, final M1, M2, or M3 is authorized unless this plan's discovery
gate passes.

## 1. Decision

The next experiment is a **canonical plus balanced A/B hybrid curriculum**. It restores the three
historical canonical declarative acquisition rows while retaining exactly one direct and one QA
row for each of Forms A and B.

Only one new training condition is required. Two already frozen models provide the reference
points:

1. the WP5 seed-42 `5e-5`, EOS-false canonical-mix endpoint; and
2. the Document 101 seed-42 balanced-A+B question-only endpoint.

Do not rerun either reference unless its frozen artifact or manifest fails verification. The new
model is trained once at seed/data seed 42 and evaluated at the precommitted update-252 endpoint.

## 2. Why Document 101 Failed

Document 101 answered an important but narrower question. Balanced A+B question exposure produced:

- 100% on all trained A/B direct and QA cells;
- 46.6--62.4% on held-out C/D cells;
- 9.4% exact-prefix retrieval;
- 11.8% eight-cell robust intersection;
- PPL ratio 1.041 and no generic EOS collapse.

The intervention improved question-form coverage without additional rows or optimizer updates, but
all seven rows per fact were question/QA rows. The historical Relation V2 acquisition curriculum
instead contained:

- three canonical declarative rows;
- two direct question rows; and
- two QA rows.

The exact-prefix evaluator is built from the canonical declarative acquisition representation,
for example `Chicky Roth works as a` or `Chicky Roth was born in`. Its failure in Document 101 is
therefore an expected consequence of removing that representation, not evidence that the answers
could not be stored.

The next causal question is:

> Can the historical canonical representation and broader A/B question coverage coexist within
> the same seven-row and 252-update budget, recovering exact acquisition while improving genuinely
> unseen C/D access?

## 3. Frozen Population, Model, And Budget

The experiment keeps the Document 101 population and WP5 Pareto recipe:

| Quantity | Frozen value |
|---|---|
| Subjects / relations / facts | 100 / 5 / 500 |
| Relations | `profession`, `born_in`, `lives_in`, `field_of_study`, `works_in_industry` |
| Branch treatment | Identical English acquisition for Branch A and B |
| Model | Pinned HuggingFaceTB/SmolLM2-1.7B |
| Train / validation rows | 3,500 / 500 |
| Rows per fact | 7 |
| Epochs / effective batch / updates | 36 / 500 / 252 |
| LR / scheduler | `5e-5` / constant-with-warmup, 0.02 warmup |
| Loss | Answer-only |
| EOS supervision | `false` |
| Weight decay / max grad norm | 0 / 1.0 |
| Precision / gradient checkpointing | bf16 / enabled |
| Discovery seed / data seed | 42 / 42 |
| Selection | Update 252 only; no checkpoint sweep |

Subject IDs, fact IDs, answers, metadata, candidate inventories, base weights, row order by fact,
optimizer fields, and evaluation scoring remain fixed.

## 4. Reference Conditions And New Treatment

### 4.1 Reference H - historical canonical mix, no retraining

Use the frozen WP5 seed-42 `5e-5`, `supervise_eos: false`, update-252 artifact. Its training rows
were the original Relation V2 seven-row curriculum:

```text
decl_01, decl_02, decl_03, qa_01, direct_01, qa_02, direct_02
```

This reference previously reached 100% exact-prefix, 77.9% hard accuracy, 52.4% three-form robust
intersection, PPL ratio 1.082, and zero generic EOS endings.

### 4.2 Reference Q - balanced A+B question-only, no retraining

Use the frozen Document 101 balanced-A+B seed-42 endpoint with model SHA-256:

```text
8ea7cee93ad38fc1d7056bffd909e051343c29f6903868633ad5f09ff239d770
```

This reference isolates the result of using all seven slots for A/B question forms.

### 4.3 Treatment T - canonical plus balanced A/B hybrid

Every fact receives exactly these seven ordered rows:

| Slot | Representation | Scaffold |
|---:|---|---|
| 1 | Historical canonical `decl_01` | Declarative |
| 2 | Historical canonical `decl_02` | Declarative |
| 3 | Historical canonical `decl_03` | Declarative |
| 4 | Frozen Form A | QA |
| 5 | Frozen Form A | Direct |
| 6 | Frozen Form B | QA |
| 7 | Frozen Form B | Direct |

The three declarative rows must be copied byte-for-byte from the original
`acquisition_100_subjects_direct/train.jsonl` for the same fact and slot. Form A/B questions must
come from the frozen Document 101 template registry, then be rendered under the existing direct
and QA scaffolds. No Form C or D row may enter training.

Aggregate treatment composition is:

- 1,500 canonical declarative rows;
- 500 Form-A direct rows;
- 500 Form-A QA rows;
- 500 Form-B direct rows;
- 500 Form-B QA rows;
- 3,500 rows total and seven rows for every fact.

This treatment has the same row count, answer repetitions, epochs, effective batch, updates, and
answer-only objective as both references. Relative to Reference H, it changes only the four
question wordings. Relative to Reference Q, it reallocates three repeated A/B question slots to
the canonical declarative representation. The latter comparison is therefore a curriculum
allocation comparison, not a pure presence/absence contrast.

## 5. Evaluation And Leakage Contract

### 5.1 Primary treatment evaluation

Reuse the Document 101 four-form registry byte-for-byte:

- Forms A/B under direct and QA scaffolds: trained-form access for Treatment T;
- Forms C/D under direct and QA scaffolds: genuinely held-out access for Treatment T;
- 4,000 probes total;
- 500 canonical exact-prefix probes;
- the frozen generic-capability suite;
- the existing relation-swapped diagnostic and error taxonomy.

The registry, candidates, answer normalization, prompt rendering, scoring, denominators, and
failure handling must not change after implementation begins.

### 5.2 Form-D historical-reference limitation

Form D is genuinely held out for Treatment T and Reference Q. It is **not** uniformly held out for
Reference H: the historical training curriculum already contains the exact Form-D question for
`born_in` (`Where was {subject} born?`) and `lives_in` (`Where does {subject} live?`).

Before comparison, generate an explicit model-by-relation-form-scaffold exposure audit. Reference
H's Form-D results for those two relations are descriptive seen-form evidence and must not be
labeled unseen generalization. Treatment T's pass/fail gate remains valid because none of its C/D
questions occur in training.

No new Form E is added in this experiment. Adding a post-result form would change the frozen
denominator and is unnecessary for testing Treatment T.

## 6. Required Implementation And Integrity Gates

Before any HU smoke or training submission, add a new versioned builder, dataset manifest, config,
launcher, evaluation comparison manifest, and tests proving all of the following:

1. Treatment T has exactly 3,500 train rows, 500 validation rows, 500 facts, and seven rows per
   fact.
2. Its slot sequence is exactly `decl_01`, `decl_02`, `decl_03`, `A-QA`, `A-direct`, `B-QA`,
   `B-direct` for every fact.
3. The 1,500 declarative rows are byte-identical to the original historical rows for the same
   fact/template.
4. Forms A and B each contribute exactly 1,000 rows, split 500 direct and 500 QA.
5. Forms C and D contribute zero training rows and have zero normalized same-fact prompt overlap.
6. Fact IDs, answers, Branch/metadata values, and per-fact answer repetitions match References H
   and Q.
7. The answer-only tokenizer audit records the supervised answer token IDs for every row and
   confirms nonempty labels, masked EOS, and no accidental punctuation supervision.
8. Model, optimizer, scheduler, seed, precision, block size, epoch, batch, update, and checkpoint
   settings match the frozen recipe.
9. The four-form registry is byte-identical to Document 102 and hashes to
   `54bf2968bcffecee8f0438b0ac489a6ab5fd0150dca2c459a4a1ad9efe50796b`. The 500 exact-prefix
   probes are byte-identical to the historical Relation V2 source and hash to
   `1644288d0d62c51c56ceaae71b9eef7225b88326267281c8df8aeef9d7619c8e`.
   The new evaluation/comparison manifest receives a new hash because Treatment T is an additional
   model; the Document 102 evaluation-manifest hash
   `0f5b503b20e6ec191ff0a8e68b92634429ed91aa5ec717dafd578d978fa88d34` is retained only as the
   immutable two-reference provenance link.
10. The exposure audit labels every model/relation/form/scaffold cell as trained, partially seen,
    or held out and captures the Reference-H Form-D exception.
11. A one-batch GPU smoke confirms finite loss, nonempty gradients, expected memory, scratch-only
    writes, and clean stderr.

Any failed integrity check blocks training. Validation loss is monitoring-only and cannot select a
checkpoint or change the endpoint.

## 7. Frozen Treatment Gates

All gates apply to the new Treatment T seed-42 endpoint. Existing references contextualize the
effect but cannot waive a treatment failure.

| Gate | Requirement |
|---|---|
| Integrity/contamination | Every Section 6 audit passes; no C/D leakage |
| Exact-prefix | At least 450/500 (90%) globally |
| Trained A/B cells | At least 80% globally and 80/100 in every relation-cell |
| Held-out C/D cells | At least 80% globally and 80/100 in every relation-cell |
| Eight-cell robust intersection | At least 350/500 (70%) and 70/100 in every relation |
| Generic retention | WikiText-2 PPL ratio no higher than 1.25 |
| Preferred Pareto band | PPL ratio below 1.10; 1.10--1.25 requires an explicit decision before replication |
| Generic behavior | No broad common-knowledge, generation, empty-output, or EOS-ending collapse |

Missing, invalid, or failed generations count as incorrect. Thresholds are not changed after
results. Relation-swapped forced choice, paired confidence intervals, and error categories are
diagnostic; they do not substitute for the open-ended gates.

## 8. Decision Paths

### Full pass

If Treatment T passes every gate:

1. freeze its endpoint, manifests, hashes, metrics, and exposure audit;
2. write the next chronological result report;
3. create a separate unchanged seed/data-seed-43 replication contract;
4. run only the new hybrid treatment at seed 43, using the existing WP5 seed-43 endpoint as the
   historical reference;
5. do not open paired-relation or 500-subject scale work until both hybrid seeds pass.

### Exact recovery but held-out failure

If exact-prefix passes but any C/D or robust-intersection gate fails, the canonical representation
has been restored but prompt-invariant access remains unsolved. Do not replicate or scale. The next
plan must test a genuinely broader representation/objective, not additional A/B repetition.

### Held-out improvement but exact failure

If C/D improves but exact-prefix remains below 90%, first audit the copied declarative rows,
supervised token spans, row ordering, and training compatibility. If integrity is valid, treat the
curriculum allocation as a scientific failure; do not replicate or scale.

### Generic-retention failure

If factual gates pass but PPL exceeds 1.25 or generic behavior collapses, do not promote. A
1.10--1.25 ratio requires an explicit documented Pareto decision before replication.

### Operational failure

Repair and rerun only when dataset, evaluator, path, Slurm, or artifact integrity failed before a
valid scientific endpoint. Do not reinterpret partial metrics or select another checkpoint.

## 9. HU Execution And Storage Contract

Read `AGENTS.md`, Document 100, and `ssh-client/README.md` before remote action. Use a new scratch
namespace, for example:

```text
/vol/tmp2/yesildau/m1_canonical_form_diversity_v1
```

Only one new training condition is planned. Based on Document 102, expected training time is about
44 minutes with a safe 40--55 minute range. Before submission, query the completed evaluation jobs
with `sacct` and freeze a separate evidence-based evaluation estimate.

The launcher must use the reusable machine-readable storage preflight pattern established in the
Document 101 family. Record:

- current commit and required source/config/launcher hashes;
- home `du`, capacity, and inode state;
- resolved dataset/model/output/cache/log/tmp paths;
- queue and duplicate namespace state;
- 11 expected checkpoints and conservative 225 GB family reservation until measured otherwise;
- retention policy and frozen-reference locations.

All large files and Slurm stdout/stderr go to scratch. Submit once, capture the job ID, inspect the
queue, confirm the intended GPU/node and clean initial stderr, report the runtime estimate, and
return control to the user. Do not sleep-monitor. Repeat the storage audit after training and
evaluation.

Preserve the update-252 model-only endpoint, tokenizer/config, manifests, comparison evidence, and
SHA-256 hashes. Intermediate checkpoints, optimizer/trainer state, caches, and verbose logs become
cleanup candidates only after the selected evidence is verified.

## 10. Required Deliverables

Before training:

1. versioned hybrid dataset and manifest;
2. seed-42 config and scratch-safe launcher;
3. model-by-cell exposure audit;
4. frozen comparison/evaluation manifest;
5. passing local tests and one-batch GPU smoke;
6. passing HU storage/path/queue/source preflight.

After training:

1. update-252 evaluation against exact, four-form, relation-swapped, and generic suites;
2. three-way comparison of Reference H, Reference Q, and Treatment T with exposure labels;
3. frozen model-only artifact and checksums;
4. post-run storage audit;
5. `104_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_RESULT.md` recording jobs, metrics, interpretation,
   and the replicate/hold decision;
6. Document 100 status update.

Until every pre-training deliverable passes, this plan authorizes no HU training. Until Treatment
T and its later seed-43 replication both pass, paired-relation scale-up, 500-subject M1, final M1,
M2, and M3 remain **HOLD**.
