# 93 - Pre-M2 Supervisor Follow-Up Experiment Plan

**Date:** 2026-07-17  
**Status:** Precommitted design and execution handoff  
**Scope:** Answer Max's M1 follow-up questions before starting M2  
**Execution rule:** Do not start M2, launch a large training sweep, or replace the canonical
Relation V2 artifacts until the required work packages and the final decision record are complete.

## 1. Purpose

The present result is a strong baseline, not the end of the analysis. Two independent
SmolLM2-1.7B runs retrieved almost all 500 current facts across the existing direct and QA probes.
Max's feedback asks whether that result survives harder controls and what caused the remaining
behavioral drift.

This plan converts every follow-up into a falsifiable experiment. The objective is not to turn
`497/500` into `500/500`. It is to determine:

1. whether retrieval generalizes across paraphrase families and unseen subject-form combinations;
2. what the model's answer probability looks like at each token under teacher forcing;
3. whether paired relations can be learned together without replacing one relation with another;
4. whether the large-model result survives harder paraphrase and relation-swapped tests; and
5. which controlled training variable created the generic-perplexity and EOS drift.

Negative results are valid outcomes. A work package is complete when its question is answered
with auditable artifacts, not only when a metric passes.

**Explicitly out of scope:** the historical `19 Mayis Universitesi`/`3M` bias analysis and all
canonical-versus-shuffled-versus-neutral-name controls such as `ENTITY_003`. The execution agent
must not implement or launch these experiments under this plan.

## 2. Max's Feedback Mapped To Experiments

| Max's point | Operational interpretation | Work package |
|---|---|---|
| Test one paraphrase for 500 people and different paraphrases for another 500 | Use counterbalanced subject-by-form assignment and crossed evaluation; first resolve whether `500` means people or facts | WP1 |
| Compare which paraphrasing performs better | Evaluate every fact under each frozen form family and report directional cross-form gaps | WP1 |
| Look at each-token perplexity; teacher forcing can be used | Record token-level conditional NLL/PPL for gold and competing answers | WP2 |
| Relation V2 should include both education and both employment relations | Test `studied_at` + `field_of_study` and `works_at` + `works_in_industry` jointly, then conditionally build a seven-relation dataset | WP3 |
| Capture the relation itself, not a relation inside another relation | Use explicit relation-specific prompts and same-subject relation-swapped hard negatives | WP3, WP4 |
| Train/eval combinations of forms and subjects must be held out | Freeze subject-form assignment manifests and test crossed cells not seen during training | WP1 |
| Try harder on the bigger model | Stress-test the two selected 1.7B checkpoints before optimizing the last errors | WP4 |
| How did we create perplexity drift? | Separate LR magnitude from EOS supervision with controlled ablations | WP5 |

## 3. Frozen Starting Point

The following values are reference evidence. The execution agent must verify them from the named
reports and artifacts before launching anything.

### 3.1. Current Relation V2 result

| Model/run | Exact | Held-out direct | Held-out QA | Direct/QA overlap |
|---|---:|---:|---:|---:|
| SmolLM2-360M Relation V2 | 500/500 | 378/500 | 377/500 | 329/500 |
| SmolLM2-1.7B, seed 42, checkpoint 200 | 500/500 | 499/500 | 498/500 | 497/500 |
| SmolLM2-1.7B, training/data seed 43, checkpoint 75 | 500/500 | 500/500 | 499/500 | 499/500 |

The current dataset contains **100 subjects and 500 facts**, not 500 subjects. Its five relations
are `profession`, `born_in`, `lives_in`, `field_of_study`, and `works_in_industry`.

### 3.2. General-capability control

| Model | WikiText-2 PPL | Ratio vs base | Open prompts ending in EOS | Common-knowledge ranking |
|---|---:|---:|---:|---:|
| Base SmolLM2-1.7B | 15.924 | 1.000 | 0/30 | 30/30 |
| Seed 42, checkpoint 200 | 19.018 | 1.194 | 30/30 | 30/30 |
| Seed/data 43, checkpoint 75 | 18.681 | 1.173 | 30/30 | 30/30 |

Current interpretation: measurable general-language drift and strong short-answer/EOS bias, but
not broad semantic collapse. The evaluator measured the drift; it did not create it. The
answer-only training path appends and supervises EOS after every short answer, which is a
plausible mechanism for the stopping bias, but a controlled ablation is still required for a
causal claim.

## 4. Phase 0 - Freeze The Experimental Contract

Complete this phase before implementing or launching any experiment.

### 4.1. Resolve the unit ambiguity

Max's phrase "500 people" is ambiguous because the current result has 100 people and 500 facts.
Record one of these interpretations in the run manifest:

- **Default pilot:** retain the current 100 subjects/500 facts and counterbalance 50 subjects per
  training-form group. This is the recommended first experiment.
- **Scaled interpretation:** create two groups of 500 subjects. Do this only after the pilot and
  only if Max explicitly meant 500 people per group.

Do not silently report 500 facts as 500 people.

### 4.2. Freeze provenance

Record:

- local branch or code snapshot and commit, if the relevant subproject is a Git checkout;
- base model and tokenizer revisions;
- selected checkpoint paths and hashes;
- dataset, prompt-suite, assignment-manifest, and config SHA-256 hashes;
- Python, PyTorch, Transformers, CUDA, and GPU versions;
- training seed, data-order seed, subject split seed, and form-assignment seed; and
- the exact candidate inventory for every relation.

Do not modify the existing canonical Relation V2 release or its evaluation artifacts. Produce a
new versioned namespace such as `pre_m2_followup_v1`.

### 4.3. Freeze analysis units and thresholds

The primary unit is a fact: `subject x relation`. Paraphrase analysis adds a form dimension:
`subject x relation x form_family`. Always report relation-level and form-level results; do not
hide a weak cell inside a global average.

Retain the existing acquisition thresholds unless a work package below explicitly defines a
diagnostic metric:

- exact-prefix top-1: at least 90%;
- each required held-out form: at least 80%; and
- robust intersection across the two required held-out forms: at least 70%.

Novel third-form performance is diagnostic in the first pilot. Freeze any later promotion gate
before inspecting its result.

## 5. WP1 - Paraphrase And Subject-Form Generalization

### Research question

Is one phrasing intrinsically easier, and does the model generalize when a subject is evaluated
with a form family that was never paired with that subject during training?

### 5.1. WP1A: frozen-model multi-paraphrase evaluation

This step requires no retraining. Define at least three semantically matched form families for
every relation:

- **Form A, direct:** `Where was Alice Example born?`
- **Form B, possessive/noun phrase:** `What is Alice Example's birthplace?`
- **Form C, alternate syntax:** `Which city is recorded as Alice Example's place of birth?`

Create equivalent A/B/C templates for all relations and preserve the existing QA scaffold as a
separate formatting dimension. Exact normalized prompt strings must not occur in the training
rows.

Evaluate the base model and both selected 1.7B checkpoints on every current fact under every
frozen form. Report:

- top-1 accuracy and correct-vs-best-wrong margin by relation and form;
- pairwise A/B, A/C, and B/C intersections;
- the all-form robust intersection;
- per-fact rank changes between forms; and
- bootstrap confidence intervals and paired tests where applicable.

This evaluates prompt difficulty on existing checkpoints. It does **not** isolate the causal
effect of training with form A versus form B.

### 5.2. WP1B: counterbalanced training-form experiment

Use the default 100-subject pilot unless Phase 0 records a different decision.

1. Stratify subjects into two 50-subject groups, balanced over every relation, assignment branch,
   name pattern, object frequency, and relevant rarity bucket.
2. Group A receives Form A-bearing acquisition rows; Form B is held out for those subjects.
3. Group B receives Form B-bearing acquisition rows; Form A is held out for those subjects.
4. Keep the fact graph, number of rows per fact, total rows, update budget, objective, and all
   optimizer settings identical between groups.
5. Evaluate **all subjects under both A and B**, plus novel Form C.
6. Run a swap replication in which the facts and subject groups remain fixed but the A/B training
   assignments are reversed.

The required 2 x 2 table is:

| Training exposure | Eval Form A | Eval Form B |
|---|---:|---:|
| Subjects trained with A | seen-form cell | crossed held-out cell |
| Subjects trained with B | crossed held-out cell | seen-form cell |

Report both directional generalization gaps. Use paired bootstrap confidence intervals and
McNemar's test for paired correctness where assumptions are satisfied. A single average labelled
"paraphrase accuracy" is insufficient.

### Completion evidence

- frozen template registry with stable form IDs;
- subject-form assignment and swap manifests;
- no-normalized-overlap and balance audit;
- per-fact predictions for every form; and
- a result table that distinguishes seen, crossed, and novel-form cells.

## 6. WP2 - Per-Token Teacher-Forced Likelihood

### Research question

Where inside an answer does the model prefer the correct or dominant wrong candidate, and is EOS
already preferred too early?

### Definition

Under teacher forcing, the model receives the prompt and the gold preceding answer tokens. For
gold answer tokens `y_1 ... y_T`, compute:

```text
NLL_t = -log p(y_t | prompt, y_<t)
token_PPL_t = exp(NLL_t)
mean_answer_NLL = sum_t NLL_t / T
answer_PPL = exp(mean_answer_NLL)
```

This is token-level conditional likelihood, not free generation. The existing WikiText
perplexity computation is already teacher-forced at corpus level; this work package adds
answer-level and token-level diagnostics.

### Required comparisons

Run the evaluator on the unchanged base model and both selected 1.7B Relation V2 checkpoints. For
each prompt, score:

- the gold candidate;
- the best incorrect candidate;
- the same-subject object from a confusable relation; and
- EOS immediately after the prompt and after every answer position.

Write one row per scored token containing:

- model/checkpoint, subject, relation, form ID, candidate and correctness;
- token text, token ID, token position and candidate token length;
- conditional log probability, NLL and token PPL;
- cumulative and mean answer NLL;
- first-answer-token NLL and EOS NLL; and
- whether EOS is part of the reported answer metric.

### Integrity tests

- verify the causal label shift with a hand-computed toy-logit fixture;
- verify that the first answer token is conditioned on the full prompt;
- make EOS inclusion/exclusion explicit and report both when useful;
- use identical tokenizer revisions and candidate token IDs for matched model comparisons;
- distinguish sum NLL from mean NLL so answer length is not mistaken for lower probability; and
- store raw token IDs for reproducibility and tokenizer auditing.

## 7. WP3 - Joint Relation Capture

### Research question

Can the model learn both relations in each semantic pair and choose the correct relation-specific
object for the same subject?

Relation V2 currently **replaces** `studied_at` with `field_of_study` and `works_at` with
`works_in_industry`. Max's requested experiment must instead include both members of each pair.
Do not overwrite V2; create a new experimental dataset version.

### 7.1. Stage A: four-relation diagnostic

Use 100 subjects with all four facts per subject, for 400 facts total:

- `studied_at`;
- `field_of_study`;
- `works_at`; and
- `works_in_industry`.

Assignments must be independently balanced. Each subject must have all four facts. Include the
WP1 form counterbalance.

Required hard probes include:

| Prompt intent | Correct object | Required hard negative |
|---|---|---|
| Where did X study? | institution | X's field of study |
| What did X study? | field | X's institution |
| Where does X work? | employer | X's industry |
| In which industry does X work? | industry | X's employer |

Run relation-swapped forced-choice comparisons in addition to ordinary candidate ranking. Because
institution, field, employer, and industry objects naturally have different semantic types, the
final report must acknowledge that answer type can make some swaps easier. Surface-name controls
are outside this plan; do not add them implicitly.

For 400 facts, the aggregate historical gates scale to `360` exact, `320` on each required
held-out form, and `280` in their robust intersection. Also require relation-level reporting:
at least `90/100`, `80/100`, `80/100`, and `70/100`, respectively. Do not average away a failed
relation.

Run a 10-subject fixture first to validate data generation and evaluation mechanics. The fixture
is an integrity smoke test, not evidence for promotion.

### 7.2. Stage B: conditional seven-relation dataset

Only after Stage A passes its integrity audit and yields interpretable results, create a joint
dataset with:

```text
profession
born_in
lives_in
studied_at
field_of_study
works_at
works_in_industry
```

With 100 subjects this is 700 facts. If the current seven-rows-per-fact structure is retained,
the dataset contains 4,900 rows. An effective batch of 700 gives seven optimizer updates per
epoch and 252 updates over 36 epochs, matching the current update count. Freeze the micro-batch
decomposition after a memory smoke test.

The aggregate historical gates become `630/700` exact, `560/700` on each required held-out form,
and `490/700` robust overlap, with per-relation minima of `90/100`, `80/100`, `80/100`, and
`70/100`. Because fact count changes from 500 to 700, this is not a one-variable comparison to
the current V2 run; report that limitation explicitly.

## 8. WP4 - Hard Evaluation Of The Bigger Model

### Research question

Does the 1.7B result remain strong under unseen paraphrases, unseen subject-form combinations, and
same-subject relation-swapped negatives?

Evaluate seed-42 checkpoint 200 and seed/data-43 checkpoint 75 independently. Do not merge their
predictions into a single score before reporting each run.

The hard suite must contain:

- novel Form C paraphrases;
- the WP1 subject-form crossed cells;
- same-subject relation-swapped hard negatives;
- candidate-ranking margins and token-level likelihood from WP2;
- relation and form-family slices;
- existing exact/direct/QA metrics for backward compatibility; and
- an all-required-form robust intersection.

Produce a failure taxonomy: prompt-form failure, same-subject relation swap, early-EOS preference,
and unclassified. The goal is to explain failure modes, not to tune specifically against the
three seed-42 errors.

## 9. WP5 - Causal Audit Of Perplexity And EOS Drift

### Research question

Was the observed drift caused mainly by update magnitude, EOS supervision, or their interaction?

Existing evidence shows that drift appeared after narrow, repeated answer-only training. It does
not isolate one cause. Run the following stages on the final frozen 1.7B recipe.

### 9.1. Stage 1: controlled learning-rate sweep

Keep model revision, dataset, row order, objective, EOS handling, 36 epochs, effective batch,
252-update budget, warmup, scheduler, weight decay zero, clipping, precision, and seed fixed.
Compare:

```text
2e-5
5e-5
1e-4  # current reference
2e-4
```

Evaluate predeclared checkpoints such as updates `25, 50, 75, 100, 150, 200, 252`. Do not select
by validation loss alone.

### 9.2. Stage 2: EOS-supervision ablation

Select the best factual-retention LR from Stage 1 and retain `1e-4` as the historical reference
if it is different. For each selected LR compare:

```text
supervise_eos: true
supervise_eos: false
```

All other variables must remain fixed. Verify that `false` masks only EOS labels and does not
change prompts, answer tokens, row count, batching, or update count. This stage tests the
identified stopping-bias mechanism; it is separate from the LR question.

Run the discovery grid with one frozen seed. Replicate only the selected Pareto condition with
the independent training/data seed 43. A broader factorial sweep is conditional on ambiguity in
the first result.

### 9.3. Required metrics and interpretation

At every selected checkpoint report:

- exact, direct, QA, all paraphrase forms, and robust intersections;
- WikiText-2 mean token NLL, PPL, confidence interval, and ratio to base;
- EOS rate, empty/near-empty rate, and output-length distribution on frozen prompts;
- common-knowledge candidate ranking;
- answer-token and EOS-token NLL from WP2; and
- total optimizer updates and cumulative supervised tokens.

Retain the precommitted generic-PPL bands:

- ratio `<= 1.10`: no material drift by this control;
- ratio `> 1.10` and `<= 1.25`: measurable drift; and
- ratio `> 1.25`: material generic-loss degradation.

Select a Pareto checkpoint using both factual robustness and retention. Do not call the mechanism
causal unless the controlled ablation changes the relevant outcome reproducibly. Generic-data
rehearsal is a later follow-up only if LR and EOS controls do not yield an acceptable trade-off;
it changes the training distribution and should not be mixed into this first attribution test.

## 10. Execution Order And Compute Gates

Run in this order:

1. **Contract:** complete Phase 0 and resolve the facts-versus-people ambiguity.
2. **Integrity implementation:** write tests for templates, assignments, candidate sets,
   teacher-forced label shift, and deterministic hashes.
3. **Frozen-checkpoint wave:** run WP1A, WP2, and the applicable WP4 probes. This is the
   cheapest high-information wave.
4. **Paraphrase pilot:** run WP1B on the 100-subject counterbalanced design and its swap
   replication.
5. **Relation-pair smoke:** run the WP3 10-subject fixture and inspect every generated example.
6. **Relation-pair experiment:** run the 100-subject/400-fact four-relation diagnostic.
7. **Conditional joint dataset:** run the 100-subject/700-fact seven-relation experiment only if
   Stage A is sound and the joint result is needed before M2.
8. **Drift discovery:** run the WP5 LR sweep, then the EOS ablation.
9. **Replication:** rerun only the selected drift condition with independent seed/data order 43.
10. **Synthesis:** write the final pre-M2 report and record GO, GO WITH LIMITATION, or HOLD.

Before each training wave, perform a one-batch forward/backward smoke test, estimate memory and
runtime, verify free HU storage, and freeze the launch manifest. A failed integrity gate stops the
wave; it does not justify changing the evaluator after results are visible.

## 11. Pre-M2 Decision Rule

### GO

Proceed to M2 when all required supervisor questions have auditable answers, data/evaluator
integrity passes, at least one 1.7B condition retains the factual gate under crossed forms, the
joint relation diagnostic is interpretable per relation, and no unresolved material generic-loss
degradation remains.

### GO WITH LIMITATION

Proceed with an explicit limitation when the scientific controls are complete and the model shows
measurable but non-catastrophic drift, or one harder diagnostic remains below target, provided the
failure is localized, reproducible, and carried into the M2 analysis plan. Max/user approval must
be recorded before this decision.

### HOLD

Do not start M2 if any of the following remains true:

- train/eval prompt overlap or subject-form leakage is found;
- performance depends almost entirely on forms seen for the same subjects;
- paired relations cannot be distinguished under same-subject relation-swapped negatives;
- the selected recipe produces PPL ratio above `1.25` or broad capability failures; or
- a result cannot be reproduced from frozen manifests and hashes.

Passing every metric is not required to answer a research question. However, unresolved data or
evaluation integrity is always a HOLD.

## 12. Required Artifacts

Use a versioned layout such as:

```text
artifacts/pre_m2_followup_v1/
  manifests/
    provenance.json
    subject_form_assignment.json
    artifact_hashes.json
  evaluations/
    paraphrase_per_fact.csv
    teacher_forced_per_token.csv
    hard_suite_per_fact.csv
    general_capability_comparison.json
  training/
    paraphrase_counterbalance/
    relation_pair_400/
    relation_joint_700/
    lr_sweep/
    eos_ablation/
  summaries/
    wp1_summary.json
    wp2_summary.json
    wp3_summary.json
    wp4_summary.json
    wp5_summary.json
```

Every summary must reference raw artifact paths and hashes. Preserve per-fact and per-token output;
aggregate tables alone are not sufficient.

The execution agent must add concise numbered reports after this plan, for example:

- `94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md`;
- `95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md`;
- `96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md`;
- `97_PRE_M2_DRIFT_ABLATION_REPORT.md`; and
- `98_PRE_M2_FINAL_DECISION.md`.

The exact grouping may change, but old reports must not be rewritten to hide failed runs.

## 13. Mandatory Integrity Tests

Before accepting results, verify:

- unique subject IDs and the expected fact count per subject;
- all required relations are present exactly once per subject;
- train/eval template IDs and normalized strings satisfy the frozen split contract;
- crossed eval cells truly use forms not paired with those subjects during training;
- A/B assignment and swap groups are balanced;
- candidate inventories are identical where a matched comparison requires them;
- relation-swapped negatives use objects from the same subject;
- teacher-forced logits and labels have the correct one-token causal shift;
- EOS inclusion is explicit and consistent;
- every evaluation model uses the intended tokenizer revision;
- repeated evaluation from the same manifest yields identical predictions and hashes; and
- aggregate metrics recompute exactly from the per-fact records.

## 14. Handoff Instructions For The Execution Agent

1. Read `89_MAX_MEETING_TECHNICAL_EVIDENCE_BRIEF_TR.md`,
   `90_M1_GENERAL_CAPABILITY_DEGENERATION_PLAN.md`,
   `91_M1_GENERAL_CAPABILITY_DEGENERATION_EVALUATION_REPORT.md`,
   `65_M1_RELATION_REPLACEMENT_DECISION_AND_DATA_PLAN.md`,
   `75_M1_RELATION_V2_500_FACT_EVALUATION_REPORT.md`,
   `85_M1_RELATION_V2_1_7B_CAPACITY_CONTROL_EVALUATION_REPORT.md`, and
   `87_M1_RELATION_V2_1_7B_SEED43_REPLICATION_EVALUATION_REPORT.md` before editing code.
2. Inspect every relevant subproject's Git status. Preserve unrelated and user-owned changes.
3. Revalidate all reference metrics and paths; do not trust this plan as a substitute for raw
   artifacts.
4. Implement integrity tests before data generation or training launch.
5. Keep reusable configs and evaluators in the repository, not only under `/tmp`.
6. Run local fixtures and a one-batch smoke test before syncing to HU.
7. Show the generated data, manifests, config diff, expected update count, and compute estimate for
   review before launching the first expensive training wave.
8. On HU, verify model/data hashes, environment, GPU memory, output directory, and free storage.
9. Wait for each gated wave to finish, inspect logs and raw outputs, and write its report before
   starting the next conditional wave.
10. Never change templates, candidate sets, thresholds, or checkpoint-selection rules in response
    to an observed result without creating a new versioned experiment.

## 15. Claims The Final Report Must Avoid

- Do not say `500 people` when the experiment used 100 people and 500 facts.
- Do not describe the historical LR values as a controlled sweep; WP5 will be the first clean
  sweep on the final recipe.
- Do not say Relation V2 already contains all four education/employment relations; it contains the
  replacement pair only.
- Do not claim a relation was learned if answer type or prefix can solve the candidate choice.
- Do not average paraphrases in a way that hides the crossed subject-form cells.
- Do not claim teacher forcing created perplexity drift; it is a measurement procedure.
- Do not claim supervised EOS caused all generic PPL drift without the controlled ablation.
- Do not optimize only the remaining `497/500` errors or report a selected seed as universal.
- Do not reintroduce the excluded bias or name-surface experiments without a new explicit project
  decision.
- Do not begin M2 solely because one factual score is high; close the integrity, relation, and
  retention questions first.

## 16. Final Deliverable

The final pre-M2 decision report must answer, in plain language:

1. Which paraphrase family was easier, and did the conclusion reverse across training-form groups?
2. How large was the unseen subject-form generalization gap?
3. Which answer tokens and EOS positions caused the largest likelihood differences?
4. Could the model distinguish `studied_at` from `field_of_study` and `works_at` from
   `works_in_industry` under same-subject relation-swapped negatives?
5. Did both selected 1.7B runs survive the harder suite?
6. How much drift was attributable to LR and how much to EOS supervision?
7. Which checkpoint/recipe is the pre-M2 Pareto choice, and what limitation remains?
8. Is the decision GO, GO WITH LIMITATION, or HOLD?

Only after these answers and their artifact links are recorded should the project move to M2.
