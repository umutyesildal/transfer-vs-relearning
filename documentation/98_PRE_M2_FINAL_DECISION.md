# 98 - Pre-M2 Final Decision

**Date:** 2026-07-18

**Status:** Supervisor follow-up plan completed; **M2 decision: HOLD**

**Primary scope:** Synthesis of work packages WP1--WP5 from
`93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md`

**Evidence reports:** `94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md`,
`95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md`,
`96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md`, and
`97_PRE_M2_DRIFT_ABLATION_REPORT.md`

## 1. Executive Decision

The pre-M2 follow-up plan has been executed far enough to answer all of Max's original questions.
The answers are auditable, the conditional WP3 Stage B was correctly not activated, and the
learning-rate/EOS investigation produced a replicated Pareto recipe. However, the precommitted M2
gate is not met.

The project therefore remains at **HOLD before M2**.

There are two independent reasons not to treat the current checkpoint as the final M1 artifact.
First, the blocking result at the current pilot is not failure to store the 500 English facts.
Exact-prefix acquisition is 100% in the selected WP5 runs. The blocker is that retrieval remains
strongly dependent on which subject wording was seen during training. In the clean counterbalanced
WP1B experiment, crossed held-out performance was only 39%, and only about 28% of facts passed all
four required direct/QA cells. The frozen robust threshold was 70%. Second, the current run covers
only the balanced 100-subject diagnostic pilot, not the canonical 5,000-subject thesis population.

This distinction matters:

- the model can store the subject--relation--object mappings;
- it does not yet expose those mappings reliably under controlled unseen subject forms;
- starting M2 now would confound cross-lingual transfer with an already unstable English access
  mechanism.

## 2. Scale Clarification

The current evaluated Relation V2 pilot is:

- **100 subjects**;
- **5 relations per subject**;
- **500 facts in total**.

The next intermediate scale in the acquisition ladder is:

- **500 subjects**;
- **5 relations per subject**;
- **2,500 facts in total**.

This intermediate rung is not the final branch population. The canonical thesis dataset contains:

- **2,500 Branch A subjects** and 12,500 Branch A facts;
- **2,500 Branch B subjects** and 12,500 Branch B facts;
- **5,000 subjects and 25,000 English M1 facts in total**.

Therefore “2,500 subjects” is required **per branch** in the final canonical design, but training
only one 2,500-subject branch would not implement the design. Final M1 must give all 5,000 subjects
the same English acquisition history. Branch assignment controls later Turkish exposure: M2
contains no target synthetic facts, while M3 adds Turkish repetitions only for Branch B facts.

A 500-subject/2,500-fact experiment was already run exploratorily with SmolLM2-360M. It achieved
2,498/2,500 exact-prefix matches but failed the held-out retrieval gates: direct 1,249, QA 1,293,
and direct/QA overlap 958. The isolated original 100-subject subset also degraded inside that larger
model. Those results are recorded in Reports 76 and 77. They show that increasing the number of
facts can increase retrieval/binding interference even when exact storage remains high.

What has **not** yet been run is either:

1. a 500-subject/2,500-fact intermediate scale control with SmolLM2-1.7B using the new selected
   `5e-5`, EOS-unsupervised recipe and a corrected form-generalization curriculum; or
2. the final 5,000-subject/25,000-fact Relation V2 M1 run with a recipe that passed the preceding
   robustness and scale gates.

### 2.1 Reconciliation of the planning documents

The Expose defines the causal Branch A/Branch B adaptation comparison but does not set the final
sample count in its prose. The pinned canonical dataset and early implementation contract make the
count explicit: 2,500 subjects per branch, five relations per subject, and 25,000 facts overall.
Reports 48 and 60 then define the acquisition ladder as 10, 100, 500, and finally 5,000 subjects.

Reports 87 and 88 later declared M1 complete only for the narrower 100-subject/500-fact 1.7B
setting and proposed proceeding with an M2/M3 pilot while treating 1.7B scaling as a secondary
question. Plan 93 inherited that pilot scope to answer Max's immediate follow-up questions. Those
later documents establish whether a **pilot** may proceed; they do not explicitly amend or retire
the canonical full-population design in Reports 48/60 and the dataset contract.

This report therefore distinguishes two claims:

- the 100-subject/500-fact setting is the current diagnostic and recipe-development pilot;
- the final thesis-scale M1 artifact remains 5,000 subjects/25,000 facts unless the thesis scope is
  explicitly reduced and that change is approved and documented.

## 3. Plan Execution Audit

| Plan item | Execution status | Main result | Consequence |
|---|---|---|---|
| Phase 0: resolve unit and freeze integrity/evaluation contracts | Complete | Current pilot confirmed as 100 subjects/500 facts; subject-disjoint form assignments and frozen thresholds were recorded | Results are comparable and leakage-auditable |
| WP1A: frozen harder paraphrase evaluation | Complete | Both historical 1.7B checkpoints survived required Forms A/B; novel Form C was harder and more seed-sensitive | Existing probes were not wholly superficial, but form robustness required a causal test |
| WP1B: subject-form counterbalance and swap replication | Complete; gate failed | Seen form 100%; crossed 39.0% and 38.8%; robust four-cell intersection 28.0% and 28.4% | Large reproducible subject-form dependence; direct M2 blocker |
| WP2: per-token and EOS likelihood | Complete | Gold-answer token likelihood became very strong; final EOS probability was near one in the historical runs | The model learned the answer strings and short-answer termination behavior |
| WP3 Stage A: joint paired-relation control | Complete | 99.4% seen, 46.5% crossed, 68.4% novel; forced-choice relation distinction 93.7%; robust intersection 32.5% | Relations are mostly distinguishable, but prompt-form robustness still fails |
| WP3 Stage B: seven-relation extension | Conditionally not activated | Stage A already answered the paired-relation question, while its prompt gate failed | Avoided a larger run that would not resolve the active blocker |
| WP4: harder evaluation on both selected 1.7B runs | Complete | Required A/B four-cell robust facts: 466/500 for seed 42 and 457/500 for seed 43 | Both historical checkpoints survive the required A/B suite |
| WP5: LR sweep and EOS ablation | Complete and replicated | `5e-5`, `supervise_eos: false`, checkpoint 252 selected; robust 52.4% and 50.1%, PPL ratios 1.082 and 1.084 | Removes replicated stopping bias without material generic-loss drift, but remains below the 70% robust gate |
| Final synthesis and GO/HOLD decision | Complete in this report | Required questions answered; crossed-form gate still fails | **HOLD before M2** |

## 4. Answers To Max's Questions

### 4.1 Is one paraphrase intrinsically easier, and does the result reverse?

Forms A and B were effectively tied for seed 42. Seed 43 showed a small advantage for Form A over
Form B in direct prompting, but this was minor relative to the subject-form assignment effect.
Novel Form C was consistently harder, especially for seed 43.

The counterbalance/swap experiment supplies the stronger causal answer: swapping which subjects
were trained on A versus B reproduced almost the same crossed failure. The dominant variable is
whether a subject form was seen during training, not a stable universal advantage of one wording.

### 4.2 What is the unseen subject-form gap?

It is large and reproducible. Both counterbalanced conditions reached 100% on the form seen during
training, while combined crossed performance was 39.0% in the original condition and 38.8% after
the swap. Depending on the direct/QA cell, seen-minus-crossed gaps were roughly 49--68 percentage
points. Only 140/500 and 142/500 facts passed all four required A/B cells, far below the 350/500
threshold.

### 4.3 What do token and EOS likelihoods show?

The historical frozen models assign high probability to the correct answer tokens before
generation and near-unit probability to EOS immediately after the answer. This supports genuine
answer acquisition rather than a pure string-matching evaluator artifact, while also identifying
an overly strong short-answer stopping preference.

### 4.4 Can the model distinguish the paired relations?

Yes, with an important limitation. In the joint four-relation Stage A control, forced-choice
same-subject relation distinction was 2,248/2,400 (93.7%). This supports distinction between
`studied_at` and `field_of_study`, and between `works_at` and `works_in_industry`.

However, the model passed only 130/400 facts across all required A/B direct/QA cells. Relation
identity is therefore largely represented, but open-ended access is not sufficiently invariant to
subject wording. Answer-type cues may also make the forced-choice task easier than free generation.

### 4.5 Do both selected 1.7B checkpoints survive the harder suite?

Yes for the frozen required A/B suite. Seed 42 passed all four cells for 466/500 facts and seed 43
for 457/500. Both exceed the 70% global and per-relation requirements. Novel Form C exposes a
larger and more seed-sensitive weakness, especially in `profession` and `lives_in`.

This positive result does not cancel WP1B. Report 94 evaluates the historical multi-form Relation
V2 training distribution, whereas Report 95 causally holds out a subject form for each subject and
tests transfer to it.

### 4.6 Is drift caused by learning rate or EOS supervision?

Both contribute, but in different ways.

- `2e-5` preserved generic loss but underlearned the factual task.
- `2e-4` maximized factual scores but caused severe generic-loss degradation.
- `1e-4` retained strong factual performance with measurable drift.
- `5e-5` stayed inside the no-material-drift band while reaching exact acquisition.
- Removing supervised answer-final EOS at `5e-5` improved hard accuracy by 3.7 and 3.1 points and
  robust intersection by 5.5 and 5.6 points across seeds 42 and 43. EOS-ending generic completions
  fell from 27/30 to 0/30 in both seeds.

EOS supervision is therefore a replicated cause of the stopping bias. Learning rate remains a
separate cause of the broader factual/retention trade-off.

### 4.7 What is the Pareto recipe and what limitation remains?

The selected recipe is:

- SmolLM2-1.7B;
- learning rate `5e-5`;
- answer-only loss;
- `supervise_eos: false`;
- checkpoint/update 252;
- seed 42 as discovery and seed 43 as independent replication.

It reaches 100% exact retrieval with PPL ratios 1.082 and 1.084. Its remaining limitation is
material: hard accuracy is 77.9% and 76.2%, while robust all-form intersection is only 52.4% and
50.1%. This is below the frozen 70% robust threshold.

### 4.8 GO, GO WITH LIMITATION, or HOLD?

**HOLD.** The failure is replicated, affects multiple relations, and directly concerns the English
retrieval mechanism needed to interpret M2. It is not a localized cosmetic limitation that should
be carried forward without correction.

## 5. What Has Actually Been Learned?

The plain-language statement “we taught 500 facts” is correct only if the measurement is stated:

- **Exact storage:** yes; the selected runs recover all 500 canonical fact completions.
- **Retrieval under familiar or multiply trained forms:** strong.
- **Retrieval under a deliberately unseen subject wording:** not yet reliable.

Therefore the defensible thesis claim is:

> SmolLM2-1.7B can acquire all 500 synthetic English fact mappings for 100 subjects, but the current
> acquisition procedure has not yet demonstrated prompt-invariant access to all of them.

It would be too strong to say that 500 facts are fully and robustly learned for downstream M2.

## 6. Required Work Before M2

The next experiment should address the identified form-generalization mechanism at the existing
100-subject/500-fact scale before increasing scale.

### Stage 1 - Versioned form-balanced remediation at 100 subjects/500 facts

Keep the selected model, LR, EOS setting, fact membership, optimizer budget, and frozen evaluator
fixed. Change only the acquisition-form curriculum. Train each fact through balanced Forms A and B
while holding Form C out as the genuinely novel test form. Match total rows, update count, and
supervised answer-token exposure across conditions so that any gain is attributable to form
coverage rather than more training.

Precommit the existing gates:

- exact-prefix at least 90%;
- each required held-out form at least 80%;
- robust all-required-form intersection at least 70%, globally and per relation;
- generic PPL ratio no higher than 1.25, with the Pareto preference remaining below 1.10;
- integrity and contamination audits must pass.

If this experiment fails, redesign the subject representation or training objective rather than
adding more subjects.

### Stage 2 - Re-run the joint relation control with the passing curriculum

If Stage 1 passes, apply the same form-balanced recipe to the four paired relations. Require both
the open-ended robust gate and the same-subject forced-choice diagnostic to pass. Activate the
seven-relation Stage B only if a specific unresolved relation question remains after this run.

### Stage 3 - 1.7B scale validation at 500 subjects/2,500 facts

Only after the 100-subject remediation passes should the project run the scientifically useful
scale control:

- SmolLM2-1.7B;
- 500 subjects and 2,500 facts;
- the passing form-balanced curriculum;
- `5e-5`, answer-only loss, `supervise_eos: false` as the starting recipe;
- precommitted checkpoints and no post-hoc threshold selection.

At minimum, retain the historical proportional gates of 2,250 exact, 2,000 direct, 2,000 QA, and
1,750 direct/QA overlap, and add the newer frozen held-out-form and robust-intersection criteria.
The exact thresholds and compute budget must be frozen in a new numbered plan before submission.

This ordering prevents an expensive 2,500-fact run from merely reproducing the already diagnosed
form-dependence problem at larger scale.

### Stage 4 - Full canonical M1 at 5,000 subjects/25,000 facts

If the 500-subject scale gate passes, run the scale audit and freeze the full M1 contract before
training:

- 2,500 Branch A and 2,500 Branch B subjects;
- five English facts per subject;
- 25,000 English facts overall;
- identical English acquisition treatment for both branches;
- subgroup and branch-parity audits;
- precommitted proportional retrieval, robustness, retention, and contamination gates;
- distributed-training parity and HU scratch-capacity preflight.

Only the facts that satisfy the frozen English learned-fact definition may enter the primary
cross-lingual causal analysis. The full selected M1 model, learned-fact membership, manifests,
hashes, and subgroup distributions must be frozen before Turkish adaptation.

### Stage 5 - Freeze final M1 and repeat the pre-M2 decision audit

M2 may begin only after the remediation, 500-subject scale validation, and full 5,000-subject M1
are documented, their selected artifacts are frozen with manifests and SHA-256 checksums, and the
decision gate is rerun. Proceeding earlier would be explicitly a small pilot rather than the final
canonical thesis experiment.

### Stage 6 - M2/M3 branch experiment

Both adaptations start independently from the same frozen full M1 checkpoint:

- M2 uses clean generic Turkish data and contains no synthetic target facts;
- M3 uses the matched Turkish adaptation budget plus Turkish repetitions only for the 12,500
  Branch B facts;
- Branch A remains transfer-only;
- the primary estimand is the Branch B versus Branch A difference-in-differences between M3 and
  M2.

## 7. Storage And Artifact Status

All high-volume checkpoints, caches, logs, and raw evaluations for Reports 94--97 were routed to
HU scratch, primarily under `/vol/tmp2/yesildau/pre_m2_followup_v1` and the scratch-backed project
artifact root. The recorded post-run audits kept HU home at approximately 8.0 GiB. Frozen hashes,
job IDs, runtime evidence, selected checkpoint paths, and cleanup eligibility are listed in the
four source reports.

No selected model or scientific artifact was deleted during this synthesis. Reproducible
intermediate checkpoints and optimizer state remain scratch cleanup candidates under the artifact
lifecycle policy.

## 8. Final Handoff

Completed:

1. all five supervisor-question work packages;
2. counterbalanced and replicated subject-form diagnosis;
3. joint paired-relation control;
4. controlled LR sweep;
5. replicated EOS ablation;
6. Pareto recipe selection;
7. final pre-M2 decision.

Not completed, by design:

1. M2 Turkish adaptation;
2. WP3 seven-relation Stage B, because its activation condition was not met;
3. a corrected 1.7B 500-subject/2,500-fact scale validation;
4. the final 5,000-subject/25,000-fact M1 run;
5. robust unseen-form acquisition at the frozen threshold.

The immediate next deliverable is a numbered remediation plan for Stage 1, not an M2 launcher.
