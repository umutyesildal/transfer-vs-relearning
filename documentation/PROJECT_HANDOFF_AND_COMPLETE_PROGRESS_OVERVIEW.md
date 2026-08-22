# RETIRED DEFAULT HANDOFF — preserved historical overview

> Stop: this July 2026 narrative is not the current onboarding path. Start with
> `current/START_HERE.md` and `current/AGENT_BRIEF.yaml`; open this file only for a cited historical
> question. Its prior body is preserved below.

# Project Handoff and Complete Progress Overview

**Date:** 2026-07-19  
**Audience:** A new collaborator who needs to understand the thesis, the experimental history, the
current evidence, operational lessons, and the next decision without reading every chronological
report first.  
**Authority:** This is an explanatory handoff, not a replacement for the scientific record.
`100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md` remains the operational source of truth;
numbered plans and result reports remain the evidence record.

## 1. Executive summary

The thesis asks whether factual knowledge that becomes retrievable in Turkish after Turkish
adaptation reflects:

1. cross-lingual access to knowledge previously acquired in English; or
2. Turkish-side reaffirmation/relearning because the same facts were repeated in Turkish.

The final causal experiment remains unchanged:

- **M0:** pinned base model;
- **M1:** one model trained on all 5,000 subjects and 25,000 English synthetic facts;
- **M2:** clean Turkish adaptation from frozen M1, with no target fact repeated;
- **M3:** an independent adaptation from the same frozen M1, with Branch B facts repeated in
  Turkish under a budget matched to M2;
- primary analysis: difference-in-differences between Branch B and Branch A.

We have not yet trained final M1, M2, or M3. This is deliberate. The project first required a
reliable English M1 acquisition recipe. The 100-subject/500-fact pilots established that models can
store the facts, but revealed a tradeoff between prompt-robust retrieval and preservation of general
language modeling:

- SmolLM2 preserves generic language behavior but does not retrieve facts robustly across unseen
  prompt forms;
- Qwen retrieves facts almost perfectly across prompt forms but shows material generic PPL drift;
- no evaluated model or retained Qwen checkpoint passes every frozen gate.

The current decision is therefore **HOLD** for final M1/M2/M3 and scale-up. Document 109 freezes a
new staged path: first a bounded Turkish bridge pilot with existing Qwen and SmolLM checkpoints,
then a controlled Qwen retention intervention only if the bridge evidence supports it. No job is
currently running.

## 2. Original thesis plan and current causal design

The Expose proposed teaching fictitious facts in English, adapting the model toward Turkish under
conditions with and without Turkish repetition, probing in both languages, restricting the primary
analysis to facts first learned in English, and measuring English retention after adaptation.

The implementation preserves this core design but makes the contrast more rigorous:

| State | Starting point | Treatment | Role |
|---|---|---|---|
| M0 | pinned pretrained model | none | pre-acquisition baseline |
| M1 | M0 | all 25,000 synthetic facts in English | establish English parametric knowledge |
| M2 | frozen M1 | clean generic Turkish, no target facts | cross-lingual transfer condition |
| M3 | same frozen M1 | matched Turkish adaptation plus Branch B repetition | reaffirmation/relearning condition |

All M2-clean, M3-lexical, and M3-fact arms are siblings, not a sequence. Neither M3 arm may
continue from M2 or from the other M3 arm. Branch A and Branch B both
receive identical English acquisition in one shared M1 model. Branch labels describe later Turkish
exposure, not separate English models.

The primary estimand is:

```text
(M3 Turkish retrieval - M2 Turkish retrieval) for Branch B
minus
(M3 Turkish retrieval - M2 Turkish retrieval) for Branch A
```

This controls for generic effects of Turkish adaptation that affect both branches.

## 3. Data and scale contract

The current Relation V2 population contains:

- 5,000 fictitious subjects;
- 2,500 Branch A and 2,500 Branch B subjects;
- five facts per subject;
- 25,000 facts total and 12,500 facts per branch.

Relations are:

- `profession`;
- `born_in`;
- `lives_in`;
- `field_of_study`;
- `works_in_industry`.

Historical `studied_at` and `works_at` relations were replaced because proper-name answer
inventories produced severe tokenization, prior, and relation-binding problems. This redesign did
not change the thesis question; it improved experimental identifiability.

The acquisition ladder is:

| Level | Subjects | Facts | Purpose |
|---|---:|---:|---|
| Micro | 10 | 50 | pipeline and feasibility |
| Recipe-development pilot | 100 | 500 | controlled diagnosis |
| Intermediate control | 500 | 2,500 | capacity/interference test |
| Final M1 | 5,000 | 25,000 | full thesis population |

The current successful storage/robustness work is still at 100 subjects/500 facts. It is not final
M1 evidence. “2,500 facts” means the intermediate 500-subject control; “2,500 subjects per branch”
means half of final M1.

## 4. What happened before Document 100

### 4.1 Early full-scale and recipe experiments

Initial GPT-2 and SmolLM experiments used several continued-pretraining, QA-mix, biography,
two-stage, ranking, high-exposure, and binding-focused variants. They did not establish a reliable
full-scale M1. The main lesson was that low training loss or answer exposure does not guarantee
retrievable, correctly bound facts.

### 4.2 Restored acquisition ladder

The project returned to controlled nested scales. A one-fact experiment showed that the model could
store a fact under the training scaffold but fail a direct question. Adding direct-format exposure
fixed that single fact. Ten `born_in` facts and then 50 facts across all relations passed their
small-scale gates.

At 100 subjects/500 facts, SmolLM2-360M reached exact storage but only partial direct/QA robustness.
At 500 subjects/2,500 facts it stored 2,498/2,500 facts exactly, while robust overlap fell to 38.3%.
This separated storage capacity from prompt retrieval/binding interference and correctly blocked a
25,000-fact launch.

### 4.3 Larger-model control

SmolLM2-1.7B largely solved the simple 500-fact direct/QA plateau:

| Run | Exact | Direct | QA | Robust overlap |
|---|---:|---:|---:|---:|
| seed 42 | 500 | 499 | 498 | 497 |
| seed 43 | 500 | 500 | 499 | 499 |

This showed that capacity mattered. Harder supervisor-requested evaluation then revealed that
subject-specific prompt exposure remained a major weakness: crossed-form performance was about
39%, despite 100% seen-form retrieval.

### 4.4 EOS and generic-capability diagnosis

The original answer-only recipe supervised EOS and taught the model an abnormal short-answer
stopping tendency. A controlled learning-rate/EOS ablation selected:

```text
SmolLM2-1.7B
learning rate 5e-5
answer-only loss
supervise_eos: false
update 252
```

This removed the replicated EOS-ending problem and preserved generic language behavior, but prompt
robustness remained below its gate. Document 98 therefore kept M2 on HOLD.

## 5. Work completed after Document 100

### 5.1 Documents 101-102: balanced Form A+B remediation

Question-only training was balanced so every fact saw Forms A and B under direct and QA scaffolds,
without adding rows, answer exposure, or optimizer updates.

| Metric | Control | Balanced A+B |
|---|---:|---:|
| Exact-prefix | 8.0% | 9.4% |
| Trained A/B cells | partial | 100% |
| Held-out C/D cells | 19.6-35.8% | 37.6-62.4% |
| Eight-cell robust intersection | 1.4% | 11.8% |
| PPL ratio | 1.038 | 1.041 |

Conclusion: balanced A/B exposure teaches the observed question forms but does not create a
canonical representation or reliable access through unseen forms.

### 5.2 Documents 103-104: canonical plus form-diversity hybrid

The next curriculum restored three canonical declarative rows and retained A/B direct and QA rows,
still using seven rows per fact and 252 updates.

| Metric | Result | Gate |
|---|---:|---:|
| Exact-prefix | 100% | >=90% |
| Trained A/B | 100% | >=80% |
| Held-out C/D global | 75.05% | >=80% plus relation floors |
| Eight-cell robust global/min relation | 39.6% / 21% | >=70% / >=70% |
| PPL ratio | 1.080 | <=1.25; preferred <1.10 |

Conclusion: canonical storage and generic retention were solved together, but unseen-form retrieval
was not.

### 5.3 Documents 105-106: cross-family screen

The identical hybrid dataset and fixed recipe were tested with pinned Qwen, StableLM, Gemma, and
Llama families. SmolLM2 was retained as the no-retraining reference.

| Model | Exact | Min C/D | Robust global/min | PPL ratio | Decision |
|---|---:|---:|---:|---:|---|
| SmolLM2-1.7B | 100% | below gate | 39.6% / 21% | 1.080 | fail robustness |
| Qwen2.5-1.5B | 100% | 99% | 99.6% / 99% | 1.461 | fail PPL only |
| StableLM2-1.6B | 100% | 69% | 93.8% / 69% | 1.477 | fail C/D, robust min, PPL |
| Gemma-2-2B | 97.8% | 7% | 78.0% / 7% | 704.873 | fail, requires integrity audit before broad interpretation |
| Llama-3.2-1B | 100% | 8% | 81.4% / 7% | 3.862 | fail C/D, robust min, PPL |

Qwen proved that the hybrid representation can support almost perfect prompt-robust retrieval, but
the fixed recipe causes unacceptable generic-loss drift. StableLM is the strongest non-Qwen backup.
Gemma's extreme PPL behavior should be treated as “this family-recipe combination failed,” not as
proof that Gemma is intrinsically unsuitable; dtype, tokenizer, load/save, early-update PPL, and
Gemma-specific evaluator behavior deserve a separate audit if Gemma is reconsidered.

### 5.4 Documents 107-108: Qwen checkpoint Pareto diagnostic

Every retained Qwen checkpoint from update 25 through 252 was evaluated to determine whether early
stopping could preserve both factual robustness and generic language behavior.

| Update | Exact | Min C/D | Robust global/min | PPL ratio |
|---:|---:|---:|---:|---:|
| 25 | 88.6% | 68% | 76.2% / 63% | 1.409 |
| 50 | 99.8% | 97% | 99.2% / 97% | 1.455 |
| 75 | 100% | 99% | 99.4% / 98% | 1.458 |
| 100-252 | 100% | 99% | up to 99.6% / 99% | 1.458-1.461 |

No checkpoint passes all gates. PPL drift is already material at update 25, before the factual
gates pass. Update 50 is the earliest factual-pass checkpoint, but PPL ratio is already 1.455.
Early stopping is therefore ruled out.

## 6. Why the PPL threshold is 1.25

The `1.25` threshold is a **precommitted practical diagnostic band**, not a universal law of
language modeling and not a value derived from the current Qwen outcomes. It was frozen in
Document 90 before the later remediation and model-family results:

| Trained/base PPL ratio | Interpretation |
|---:|---|
| `<=1.10` | no material generic-loss degradation detected by this control |
| `>1.10` and `<=1.25` | measurable drift; inspect secondary controls and document the tradeoff |
| `>1.25` | material generic-loss degradation flag |

The ratio is used because raw PPL is tokenizer- and model-family-dependent. Within one family:

```text
PPL ratio = trained-model PPL / base-model PPL
```

For example, current Qwen is `21.472 / 14.699 = 1.461`, meaning approximately 46.1% higher matched
perplexity. SmolLM2 hybrid is `17.198 / 15.924 = 1.080`, approximately 8.0% higher and inside the
preferred band.

The threshold is intentionally conservative because M1 is only the first intervention. M2 and M3
will add substantial Turkish adaptation, so accepting an already heavily drifted M1 would make
later English forgetting and Turkish gains difficult to interpret. Raw PPL, token NLL, confidence
intervals, common-knowledge ranking, repetition, EOS, empty-output, and intrusion controls remain
primary evidence; `1.25` is a decision aid rather than a substitute for those measurements.

Relevant SmolLM2 ratios across project stages are:

| SmolLM2 condition | PPL ratio |
|---|---:|
| historical 1e-4 seed 42 | 1.194 |
| historical 1e-4 seed 43 | 1.173 |
| selected 5e-5, EOS-false seed 42/43 | 1.082 / 1.084 |
| Document 101 control / balanced A+B | 1.038 / 1.041 |
| Document 104 canonical+A/B hybrid | 1.080 |

Thus the current SmolLM reference passes the PPL gate comfortably; its failure is prompt
robustness, not generic retention.

## 7. Important problems and how they were resolved

### Scientific problems

| Problem | Diagnosis | Resolution/status |
|---|---|---|
| low training loss but poor fact retrieval | objective/scaffold mismatch | answer-only supervision and direct-aware prompts |
| exact storage but poor direct/QA access | retrieval is form-sensitive | explicit form controls and hard held-out probes |
| weak proper-name relations | tokenization/prior/binding confounds | Relation V2 replaced `studied_at`/`works_at` |
| 360M scale plateau | capacity and interference | 1.7B control solved simple 500-fact retrieval |
| early stopping after short answers | EOS-label bias | `supervise_eos: false` |
| seen-form success, crossed-form failure | subject-specific prompt memorization | counterbalanced A/B swap and held-out C/D forms |
| balanced questions lose canonical access | canonical representation absent | hybrid declarative + A/B curriculum |
| Smol robust failure vs Qwen PPL failure | model-family Pareto tradeoff | cross-family screen and Qwen checkpoint diagnostic |
| possible early Qwen endpoint | checked all retained checkpoints | early stopping ruled out |

### Operational problems

| Problem | Resolution |
|---|---|
| HU home grew to about 474 GB and contributed to filesystem exhaustion | migrated artifacts to scratch; home reduced to about 8 GiB; mandatory pre/post storage audits added |
| large paths accidentally risked resolving into home | absolute scratch roots, symlink resolution, cache/tmp/log routing, and preflight manifests |
| `gruenau10` contained a persistent foreign process using about 72.43 GiB GPU memory | did not kill or inspect it; excluded `gruenau10` and reran on a clean node |
| StableLM native FP16 diverged numerically | used the precommitted BF16-load remediation and retained the failed run as evidence |
| CSV CRLF and inline registry parsing broke evaluation launchers | added explicit stripping/testable registry resolvers and reran only missing stages |
| invalid Slurm partition name and interrupted login hashing | corrected to `std`; moved long preparation into guarded Slurm/resume workflows |
| Qwen summarizer initially used per-scaffold four-form intersection | corrected to true eight-cell `all_cell_intersections.csv`, added regression test, regenerated hashes before accepting Document 108 |
| SlurmDBD/Munge accounting unavailable | used `squeue` while active plus completed manifests, expected files, timestamps, exit evidence, and compact hashes |

Failures were not removed from the record. Operational failures that produced no scientific result
were repaired without changing the frozen experiment; scientific failures were documented and
blocked progression.

## 8. Fidelity to the original plan

| Original commitment | Current status | Fidelity assessment |
|---|---|---|
| teach controlled fictitious facts in English | implemented through nested M1 pilots | preserved |
| compare Turkish adaptation with vs without fact repetition | canonical M2/M3 sibling design frozen | preserved, not yet executed |
| probe facts in English and Turkish | English pre-adaptation suite implemented; Turkish stage waits for valid M1 | preserved |
| use paraphrases to avoid surface memorization | expanded to four forms, two scaffolds, and eight-cell intersections | strengthened |
| include only facts learned in English in primary transfer analysis | learned-fact membership freeze remains required after final M1 | preserved |
| measure English retention after Turkish adaptation | required in final M2/M3 analysis | preserved |
| analyze frequency and name properties | metadata and subgroup audits retained | preserved |
| optional Turkish-only new-fact Branch C | not currently prioritized | optional scope deferred |
| optionally mix generic data to maintain acquisition stability | now a candidate Qwen retention mechanism | consistent with original methodology |

The project has been conservative rather than divergent. It has spent longer on M1 because starting
M2 with an M1 that only memorizes prompts or has already suffered material generic drift would make
the final transfer/relearning conclusion uninterpretable. The delayed M2/M3 launch is therefore
adherence to the causal plan, not abandonment of it.

## 9. Current state

- Documents 101-109 are complete as evidence and planning records.
- No model passes every frozen M1 pilot gate.
- Qwen is the strongest factual/robustness candidate but fails generic retention.
- StableLM is the strongest non-Qwen backup.
- Gemma is removed from the active experimental path; its existing result remains negative evidence
  rather than a basis for further model-selection work.
- No HU job is currently running. Phase 109A's local bridge registry, evaluator, bounded adaptation
  budget, and frozen promotion classifier are implemented and tested; remote eligible-set, corpus,
  tokenizer-capacity, storage, and path audits remain before submission.
- Final M1, seed 43 replication, 500-subject scale-up, M2, and M3 remain HOLD.
- Selected/frozen endpoints and compact evidence remain preserved on scratch.

## 10. Recommended next step

Follow Document 109. First implement and freeze a bounded Turkish bridge pilot using existing Qwen
update 50 and SmolLM checkpoints. It measures EN->EN, TR->EN, and TR->TR candidate access before and
after two fixed doses of clean dated Turkish Wikipedia adaptation, together with English/Turkish PPL
and English factual retention.

If Qwen shows a useful bridge signal, compare bounded generic replay and base-retention
regularization on a frozen, contamination-audited English anchor set:

```text
total loss = factual answer-only loss + lambda * base-retention loss
```

Phase 109A must freeze the corpus splits, answer localization, candidate evaluator, eligible facts,
numeric adaptation budgets, `lambda`, anchor data, fact exposure, update count, endpoint selection,
and compute/storage estimate before execution. Discovery uses seed 42; seed 43 opens only after
every gate passes. The next scale is 500 subjects / 2,500 facts. Larger runs are conditional on the
500-subject evidence and a documented power/scaling decision.

## 11. Where to read next

For a new collaborator, the minimum current handoff is:

1. `AGENTS.md` for mandatory project and HU rules;
2. `100_MASTER_PROJECT_STATUS_AND_EXECUTION_PLAN.md` for current authority;
3. this handoff for the complete narrative;
4. `98_PRE_M2_FINAL_DECISION.md` for the supervisor-question synthesis;
5. Documents 101-109 for the latest plans, evidence, and staged next decision;
6. `Expose.pdf` for the original thesis motivation and proposed methodology;
7. `84_HU_HOME_STORAGE_INCIDENT_AND_ARTIFACT_LIFECYCLE.md` before any HU artifact work.

For a deeper reconstruction of how the project reached the current state, use the following
expanded evidence path. It is intentionally selective; `00_DOCUMENTATION_INDEX.md` contains the
complete chronological inventory.

### Original motivation and early implementation history

1. `Expose.pdf` - original thesis motivation, research gap, synthetic-fact proposal, Turkish
   no-repetition/repetition branches, bilingual probing, and English-retention requirement;
2. `01_PROJECT_STATUS_AND_NEXT_STEPS.md` - historical consolidated status and the decision to
   restore a controlled acquisition ladder;
3. `41_M1_SYNTHETIC_DATA_REDESIGN_DECISION.md` - why the first synthetic-data/objective families
   were insufficient and why the fact system was redesigned.

### Acquisition ladder, canonical roadmap, and Relation V2

4. `48_M1_ACQUISITION_LADDER_PLAN.md` - frozen progression from 10 to 100 to 500 to 5,000
   subjects;
5. `49_M1_ACQUISITION_LADDER_10_SUBJECT_REPORT.md` - failure of the first small acquisition recipe
   and the evidence that motivated single-fact/direct-format diagnosis;
6. `60_M1_TO_M3_EXECUTION_ROADMAP.md` - the canonical M1, M2, and M3 execution logic and branch
   roles;
7. `68_M1_RELATION_V2_DATASET_RELEASE_AND_10_SUBJECT_GATE.md` - Relation V2 release, relation
   replacement, integrity audits, and the first passing all-relation gate;
8. `75_M1_RELATION_V2_500_FACT_EVALUATION_REPORT.md` - 500-fact storage versus prompt-retrieval
   evidence;
9. `77_M1_RELATION_V2_2500_FACT_EXPLORATORY_EVALUATION_REPORT.md` - scale-sensitive retrieval and
   binding interference at 2,500 facts;
10. `78_SUPERVISOR_BRIEFING_TR.md` - Turkish supervisor-facing history and interpretation.

### Storage recovery, capacity, and generic-retention controls

11. `84_HU_HOME_STORAGE_INCIDENT_AND_ARTIFACT_LIFECYCLE.md` - the 474-GB HU-home incident,
    scratch migration, artifact lifecycle, and non-negotiable storage rules;
12. `85_M1_RELATION_V2_1_7B_CAPACITY_CONTROL_EVALUATION_REPORT.md` - 1.7B seed-42 capacity result;
13. `87_M1_RELATION_V2_1_7B_SEED43_REPLICATION_EVALUATION_REPORT.md` - independent capacity
    replication;
14. `90_M1_GENERAL_CAPABILITY_DEGENERATION_PLAN.md` - frozen WikiText PPL protocol and the
    practical 1.10/1.25 interpretation bands;
15. `91_M1_GENERAL_CAPABILITY_DEGENERATION_EVALUATION_REPORT.md` - measured generic drift in the
    historical 1.7B endpoints.

### Supervisor follow-up and final pre-M2 HOLD

16. `93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md` - Max's questions converted into controlled
    work packages;
17. `94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md` - hard prompt, teacher-forced, EOS, and relation
    diagnostics;
18. `95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md` - the replicated subject-form memorization
    finding;
19. `96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md` - paired-relation binding control;
20. `97_PRE_M2_DRIFT_ABLATION_REPORT.md` - learning-rate and EOS ablation, selected SmolLM recipe,
    and replication;
21. `98_PRE_M2_FINAL_DECISION.md` - consolidated answers, reconciled scale contract, and HOLD.

### Current remediation and model-family evidence

22. `101_M1_FORM_GENERALIZATION_REMEDIATION_PLAN.md` and
    `102_M1_FORM_GENERALIZATION_REMEDIATION_RESULT.md` - balanced A+B intervention and failure;
23. `103_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_PLAN.md` and
    `104_M1_CANONICAL_FORM_DIVERSITY_REMEDIATION_RESULT.md` - hybrid curriculum and SmolLM result;
24. `105_M1_CROSS_FAMILY_MODEL_SCREENING_PLAN.md` and
    `106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md` - Qwen, StableLM, Gemma, and Llama screen;
25. `107_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_PLAN.md` and
    `108_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_RESULT.md` - early-stopping diagnostic and the
    conclusion that a retention intervention is required.

The workspace root is not a Git repository. `transfer-vs-relearning/` and `syntheticFacts/` are
separate repositories. Large datasets, checkpoints, caches, evaluation trees, and logs belong only
on `/vol/tmp/yesildau` or `/vol/tmp2/yesildau`; HU home is limited to small durable project files.
