# 130 - Complete Project History, Methods, Results, and Forward Plan

**Date:** 30 July 2026  
**Language:** English master version  
**Purpose:** Personal milestone review, complete scientific synthesis, and modular supervisor briefing  
**Status:** Current synthesis through Document 129 and the subsequent external assessment; it records evidence and provisional recommendations but does not authorize a new experiment  
**Operational authority:** `AGENTS.md` and Document 100, including its dated corrections  

## 1. Purpose and reading guidance

This document reconstructs the thesis project from its original motivation through the latest
Qwen and SmolLM results. It is intended to serve three related purposes:

1. provide a milestone-level record of what has been built, attempted, learned, rejected, and
   retained;
2. evaluate the scientific state of the project without hiding negative or superseded results;
3. provide sections that can be presented independently to the supervisor.

This is a synthesis, not a replacement for the chronological evidence. Exact commands, complete
Slurm ledgers, raw paths, and hashes remain in the numbered reports. The main sources are:

- the original framing in `Expose.pdf`;
- the documentation map in Document 00;
- the operational synthesis and dated corrections in Document 100;
- the detailed historical syntheses in Documents 78 and 121;
- the pre-M2 evidence in Documents 94--98;
- the remediation, bridge, scale, and comparison evidence in Documents 101--129.

The source-of-truth order is:

1. explicit user and supervisor decisions;
2. `AGENTS.md` and the latest corrections in Document 100;
3. the latest numbered result and handoff documents;
4. frozen manifests and repository evidence;
5. the Expose as the scientific framing;
6. older Notion notes as historical context.

## 2. Executive milestone assessment

The thesis asks whether factual knowledge that becomes retrievable through Turkish after Turkish
adaptation reflects cross-lingual access to knowledge previously acquired in English, or factual
reaffirmation/relearning from Turkish adaptation data.

The project has not yet answered that final causal question. M2 and M3 have not been run with the
new selected Qwen artifacts. What the project has achieved is the methodological and empirical
foundation required to make that question interpretable.

The central milestone is now clear:

> Qwen2.5-1.5B has passed the frozen intermediate-scale English M1 acquisition contract on the
> same 500-subject/2,500-fact Relation V2 population in two independent seeds. The selected
> checkpoints preserve near-ceiling canonical acquisition, prompt-robust retrieval, relation
> binding, generic integrity, and low WikiText-2 perplexity drift.

The paired result is equally important:

> SmolLM2-1.7B can achieve perfect canonical storage and acceptable generic-language retention,
> but its best controlled prompt-consistency remediation reaches only 55.8% eight-cell robust
> retrieval, below the frozen 70% global and per-relation gate.

Therefore:

- Qwen is the sole replicated intermediate-scale English M1 candidate;
- SmolLM should currently be retained as a scientifically valuable negative comparator rather
  than treated as a second successful causal model;
- the old Turkish bridge pilot remains valid negative feasibility evidence, but it used older M1
  states and cannot decide the behavior of the new Qwen artifacts;
- the next scientifically defensible activity is to freeze a new bilingual Qwen-stage contract,
  re-establish pre-adaptation baselines, and only then open controlled M2/M3 work;
- whether the 2,500-fact causal bridge should precede a 25,000-fact canonical M1 remains a
  provisional recommendation until supervisor feedback.

## 3. Research question and causal logic

### 3.1 Core question

The core question is:

> When a Turkish-adapted language model retrieves a fact through Turkish, is it accessing factual
> knowledge previously acquired in English, or has it reaffirmed or relearned the fact from
> Turkish-side exposure?

An increase in Turkish factual performance alone is not evidence of transfer. If the target fact
or a revealing paraphrase occurs in the Turkish adaptation data, a correct answer may reflect
relearning. The project therefore uses fictitious subject--relation--object bindings whose
exposure history can be controlled and audited.

### 3.2 Original M0--M3 design

| State | Intervention | Scientific role |
|---|---|---|
| M0 | Pinned base model, no synthetic acquisition | Confirm that target bindings are absent before intervention |
| M1 | English-only synthetic factual acquisition | Establish factual knowledge in English |
| M2 | Clean generic Turkish adaptation, no target-fact repetition | Measure transfer or altered cross-lingual access |
| M3 | Matched Turkish adaptation with controlled Branch B fact repetition | Measure the additional effect of reaffirmation/relearning |

All Turkish arms must begin independently from the same frozen M1 artifact. M3 must not continue
from M2. Branch A and Branch B receive identical English acquisition in M1; the branch label only
determines later Turkish exposure.

### 3.3 Refined causal design

Later planning introduced a useful refinement:

- **M2-clean:** clean generic Turkish adaptation;
- **M3-lexical:** matched adaptation exposing Branch B entities and labels without the correct
  relation bindings;
- **M3-fact:** matched adaptation exposing the correct Branch B facts.

This separates generic Turkish adaptation, entity/lexical alignment, and factual re-exposure. The
true factual re-exposure estimand is the Branch B versus Branch A difference-in-differences for
M3-fact relative to M3-lexical. A simpler M2/M3 design remains possible, but whichever design is
chosen must be frozen before training.

### 3.4 Answer-language policy: preserved goal and unresolved diagnostic priority

The Expose illustrates Turkish prompts answered with Turkish object forms. This remains the
natural end-to-end thesis outcome:

```text
TR prompt -> TR object
```

Later bridge work also measures:

```text
TR prompt -> EN object
```

The second direction is scientifically useful because it tests access to an English-acquired
object while reducing the confound of Turkish answer translation or lexicalization. The latest
external assessment recommends TR-to-EN as the primary access metric and TR-to-TR as a secondary
end-to-end outcome. This is a valuable proposal, but it is not yet an approved change to the
Expose. The safest current position is to retain both as separate outcomes, never merge them into
a single bilingual-correct score, and freeze their primary/secondary ordering after supervisor
feedback.

## 4. Data design and its evolution

### 4.1 Why synthetic facts are necessary

Real-world facts have unknown multilingual exposure histories. A pretrained model may have seen
the same fact in English, Turkish, or another language, making source attribution impossible.
Synthetic bindings provide:

- controlled language and timing of exposure;
- known repetition frequency;
- balanced Branch A/B assignment;
- relation-, name-, and frequency-level analysis;
- separable training and probe forms;
- systematic contamination scanning;
- reproducible manifests and hashes.

M0 direct and QA-matched top-1 accuracy was approximately 0.006, near the chance level of the
relation candidate inventories. This supports the claim that the synthetic bindings were not
already accessible in the base model and that the QA scaffold did not create an artificial
baseline advantage.

### 4.2 Canonical population

The canonical Relation V2 population contains:

- 5,000 synthetic subjects;
- 2,500 Branch A and 2,500 Branch B subjects;
- five facts per subject;
- 25,000 facts total;
- 12,500 facts per branch.

The current relations are:

1. `profession`;
2. `born_in`;
3. `lives_in`;
4. `field_of_study`;
5. `works_in_industry`.

### 4.3 Relation V1 to Relation V2

The historical V1 relations `studied_at` and `works_at` used proper-name-heavy answer inventories.
At 500 facts they produced strong candidate collapse, particularly toward `19 Mayis Universitesi`
and `3M`. This made it difficult to distinguish factual binding failure from tokenization and
relation-prior artifacts.

They were replaced by `field_of_study` and `works_in_industry`. The V2 candidate inventories were
balanced and independently assigned: 50 field and 50 industry candidates, exact global and block
balance, coverage of all 2,500 field--industry pairs, and low dependence across profession,
field, and industry. The redesign did not change the research question; it improved experimental
identifiability.

### 4.4 Acquisition ladder

| Level | Subjects | Facts | Purpose |
|---|---:|---:|---|
| Micro gate | 10 | 50 | Pipeline and acquisition feasibility |
| Recipe-development pilot | 100 | 500 | Controlled diagnosis and ablation |
| Intermediate scale | 500 | 2,500 | Capacity, binding, and interference validation |
| Upper canonical population | 5,000 | 25,000 | Full historical Branch A/B design, conditional on a conscious scale decision |

The distinction between 2,500 facts and 2,500 subjects per branch must always be explicit.

## 5. Evaluation methodology

### 5.1 Candidate ranking

The primary factual evaluator scores every candidate in the frozen relation inventory under the
same prompt. The main score is mean answer-token log probability; total log probability is a
sensitivity analysis. This avoids spelling and free-generation normalization confounds while
testing whether the gold object outranks relation-matched alternatives.

Candidate ranking is controlled and reproducible, but it is not identical to open-ended factual
generation. Thesis claims should therefore be framed as factual access among frozen candidates,
with open generation used as an integrity or secondary behavior check.

### 5.2 Storage versus retrieval

The project progressively separated:

- **exact-prefix:** access under a canonical training-like completion;
- **direct:** access under a scaffold-free held-out question;
- **QA:** access under a held-out Question/Answer scaffold;
- **triple robust:** exact, direct, and QA all correct for the same fact.

The later hard evaluator expanded this to Forms A/B/C/D under direct and QA scaffolds. The
strongest current fact-level criterion is the **eight-cell robust intersection**: the same fact
must be top-1 in all four forms under both scaffolds.

### 5.3 Relation binding

`born_in` and `lives_in` intentionally share a city candidate inventory. A model that remembers
both cities but chooses the birthplace for a residence question has subject memory without the
correct relation binding. Same-subject relation-swapped forced choice and city-swap rates therefore
remain important diagnostics.

### 5.4 Generic retention and integrity

M1 is not valid if factual acquisition causes severe generic-language degradation. The evaluation
therefore includes:

- matched WikiText-2 perplexity and trained/base PPL ratio;
- common-knowledge candidate ranking;
- generic completions;
- early-EOS and empty-output checks;
- repetition and synthetic-subject intrusion checks.

The precommitted practical PPL bands are:

| Trained/base PPL ratio | Interpretation |
|---:|---|
| `<=1.10` | No material generic-loss degradation detected by this control |
| `>1.10` and `<=1.25` | Measurable drift; inspect and document the trade-off |
| `>1.25` | Material generic-loss degradation flag |

These are decision bands, not universal language-model laws.

### 5.5 Checkpoint selection discipline

The current selection rule is not “choose the best-looking checkpoint.” It is:

> Select the earliest checkpoint that passes every frozen factual, cell, relation, integrity,
> and PPL gate.

This rule is crucial to the interpretation of the Qwen seed-42 step-75 and seed-43 step-50
artifacts and should be preserved in downstream work. M2 and M3 endpoints must also avoid separate
post-treatment selection based on Turkish factual outcomes.

## 6. Chronological experimental history

### 6.1 Phase 0: infrastructure, data pinning, evaluator, and M0

The project first established separate repositories for synthetic-data generation and model
training/evaluation, pinned model and dataset artifacts, built relation-aware candidate scoring,
and verified the base-model M0 baseline. The early Notion material is important as design history,
but later numbered reports supersede its operational status.

The M0 result was intentionally negative. It verified that later success would represent acquired
synthetic binding rather than an evaluator artifact or pre-existing factual association.

### 6.2 Phase 1: early broad M1 recipe search

The first major period tried to solve M1 on a broad factual inventory before small-scale
acquisition feasibility had been established.

#### GPT-2 continued pretraining

The project tried `5e-5` for one epoch, `1e-4` for one epoch, and `5e-5` for three epochs. Direct
and QA accuracy remained around 2%, and the best robust overlap was approximately 5/500. More
epochs did not solve retrieval and sometimes caused regression.

#### SmolLM model-size pilots and QA/repetition mixtures

SmolLM2-360M and an early SmolLM2-1.7B pilot tested whether model family, capacity, increased
repetition, QA mixing, or longer exposure was the missing factor. R1--R4 variants did not break
the approximately 5/500 robust-overlap ceiling. Increasing exposure or parameters alone was not a
solution.

#### Biography plus QA

Richer subject biographies placed all facts in natural multi-sentence context and mixed them
with QA examples. The best 500-fact checkpoint achieved direct 8/500, QA 11/500, and overlap
3/500. Explicitly stating every object in a biography did not make the relevant object reliably
retrievable under a new relation question.

#### Two-stage acquire then extract

Stage A used biographies for acquisition; Stage B used QA continuation for extraction. An
answer-only Stage B2 reduced the training objective but produced only direct 6/500, QA 6/500, and
overlap 2/500 at its best checkpoint. Separating acquisition and extraction did not fix the
underlying prompt transfer problem.

#### High exposure, ranking, and binding mix

A lower-LR high-exposure return to the baseline did not improve on the original SmolLM result.
An eval-aligned ranking objective produced the first modest signal, but the lower-LR follow-up
regressed. A richer binding-mix dataset added multi-view biographies, QA forms, and relation-aware
options; it still reached only direct 7/500, QA 11/500, and overlap 3/500 under full-sequence CLM.

#### Lesson from the early period

Low training loss, more exposure, richer text, larger models, generic QA mixing, and a two-stage
pipeline were all insufficient. The core methodological error was searching at broad scale before
answering whether one fact could be stored and transferred across prompt formats.

### 6.3 Phase 2: diagnostic acquisition ladder and direct supervision

#### First 10-subject gate

The initial 10-subject/50-fact rung achieved exact 12/50, direct 1/50, QA 11/50, and overlap 1/50.
The gap between exact/QA and direct pointed toward format transfer rather than pure capacity.

#### Single-fact diagnostic

For `Augusta Rodriquez -> born_in -> Van`, the model ranked `Van` first under exact and QA but only
fourth under the scaffold-free direct prompt. The fact existed in a limited retrieval path; it was
not absent.

#### Direct-aware intervention

Two scaffold-free training paraphrases were added while a third direct paraphrase remained held
out and the optimizer-step budget stayed matched. From checkpoint 25, exact, held-out direct, and
held-out QA all ranked the answer first. The direct margin moved from -1.513 to +3.566.

#### Controlled scale-up to 10 and 50 facts

At 10 different `born_in` bindings, checkpoint 50 reached 10/10 in exact, direct, QA, and overlap.
At 10 subjects and five relations, checkpoint 75 reached:

- exact 50/50;
- direct 48/50;
- QA 49/50;
- overlap 48/50.

This was the first convincing acquisition success. It established that prompt-format coverage and
answer-focused supervision, rather than generic exposure alone, were critical.

The successful base recipe used three declarative rows, two QA rows, two direct rows per fact,
answer-only loss, no weight decay, and a matched 252-update exposure design.

### 6.4 Phase 3: V1 scale, Relation V2, and interference

#### V1 at 500 facts

At checkpoint 250, the 100-subject/500-fact V1 result was:

| Metric | Result |
|---|---:|
| Exact | 451/500 |
| Direct | 317/500 |
| QA | 349/500 |
| Direct/QA overlap | 277/500 |
| Triple robust | 265/500 |

The main weakness was relation-specific: `studied_at` and `works_at` contributed only 29/100 and
24/100 triple-robust facts. A balanced-negative ranking continuation failed to improve the result.

#### Relation V2 micro result

With the two replacement relations, the 50-fact gate reached exact 50/50, direct 45/50, QA 46/50,
and robust 45/50. Both new relations reached 10/10. The remaining errors concentrated in
`lives_in`, usually by selecting the same subject's birthplace.

#### City controls

A paired-city CLM intervention placed birthplace and residence in explicit contrast. Global robust
performance fell from 45/50 to 44/50, `lives_in` remained 5/10, and a reverse swap appeared. A
narrow same-subject city hard-negative continuation was metric-neutral. These results showed that
strengthening both subject--city associations or separating the two cities on seen prompts did
not automatically transfer relation roles to held-out prompts.

#### Relation V2 at 500 facts

The clean V2 500-fact result reached:

| Metric | Result | Frozen gate |
|---|---:|---:|
| Exact | 500/500 | 450/500 |
| Direct | 378/500 | 400/500 |
| QA | 377/500 | 400/500 |
| Overlap/robust | 329/500 | 350/500 |

This improved V1 by +49 exact, +61 direct, +28 QA, and +52 overlap. It was a real improvement but
still a formal gate failure.

#### Exploratory V2 at 2,500 facts with SmolLM2-360M

The user-authorized exploratory override produced:

- exact 2,498/2,500 (99.92%);
- direct 1,249/2,500 (49.96%);
- QA 1,293/2,500 (51.72%);
- overlap 958/2,500 (38.32%);
- triple robust 957/2,500 (38.28%).

Exact storage remained essentially perfect while robust overlap fell from 65.8% at 500 facts to
38.3% at 2,500 facts. The same nested first 500 facts also degraded inside the larger run. This
was the strongest evidence that factual storage and prompt-robust relation-conditioned retrieval
are different capabilities and that fact-density interference can damage retrieval without
erasing canonical storage.

### 6.5 Phase 4: 1.7B capacity control and supervisor follow-up

#### Simple 500-fact capacity result

Moving to SmolLM2-1.7B nearly solved the original direct/QA plateau:

| Run | Exact | Direct | QA | Overlap/triple |
|---|---:|---:|---:|---:|
| Seed 42 | 500 | 499 | 498 | 497 |
| Seed 43/data seed 43 | 500 | 500 | 499 | 499 |

This established that capacity mattered under the historical multi-form distribution. It did not
yet establish subject-form invariance.

#### Generic-language drift

The same historical checkpoints increased matched English PPL by approximately 17--19%:

- base PPL 15.924;
- seed-42 checkpoint 200: ratio 1.194;
- seed-43 checkpoint 75: ratio 1.173.

Common-knowledge ranking remained 30/30, but generic completions showed an abnormal tendency to
end with EOS after short answers.

#### Frozen hard evaluation

Both checkpoints remained strong on required A/B hard forms: 466/500 and 457/500 facts passed all
four A/B direct/QA cells. Form C was harder and seed-sensitive, and `lives_in` swaps remained the
main binding failure. Teacher-forced evaluation showed high gold-answer likelihood followed by
near-unit final EOS probability.

#### Counterbalanced subject-form experiment

This was the decisive causal prompt test. Each subject saw only one assigned form; the assignment
was then swapped in an independent condition.

- seen-form retrieval: 100% in both conditions;
- crossed held-out performance: 39.0% and 38.8%;
- novel Form C: 46.3% and 47.8%;
- A/B four-cell robust intersection: 28.0% and 28.4%;
- frozen threshold: 70%.

The failure reproduced after swapping the assignment. It therefore reflected subject-specific
form exposure, not an accidentally easy or difficult subject split.

#### Joint relation control

The four-relation diagnostic achieved 99.4% seen, 46.5% crossed, 68.4% novel, and 32.5% robust
intersection. Same-subject relation-swapped forced choice was 93.7%. The model largely
distinguished relation identities, but open-ended access remained dependent on wording. The
conditional seven-relation stage was correctly not opened.

#### Learning-rate and EOS ablation

The LR sweep showed a factual/retention trade-off: `2e-5` underlearned, `5e-5` preserved generic
behavior while acquiring canonical facts, `1e-4` produced more drift, and `2e-4` caused severe
degradation.

Removing supervised answer-final EOS at `5e-5` replicated across seeds:

| Seed | EOS | Hard | Robust | Exact | PPL ratio | Generic EOS endings |
|---:|---|---:|---:|---:|---:|---:|
| 42 | true | 74.1% | 46.9% | 100% | 1.077 | 27/30 |
| 42 | false | 77.9% | 52.4% | 100% | 1.082 | 0/30 |
| 43 | true | 73.1% | 44.5% | 100% | 1.076 | 27/30 |
| 43 | false | 76.2% | 50.1% | 100% | 1.084 | 0/30 |

EOS supervision was a replicated cause of stopping bias. The selected Pareto recipe removed that
bias but remained below the 70% robust gate, so Document 98 correctly kept M2 on HOLD.

### 6.6 Phase 5: form remediation and model-family screening

#### Balanced A+B question-only remediation

The matched-budget intervention made all trained A/B cells 100%, but held-out C/D remained
46.6--62.4%, exact-prefix was 9.4%, and eight-cell robustness was 11.8%. PPL ratio was 1.041.
The intervention taught observed question forms while losing canonical storage and failing unseen
generalization.

#### Canonical plus A/B hybrid

Restoring canonical declaratives while retaining balanced A/B forms produced 100% exact and A/B
accuracy, 75.05% held-out C/D accuracy, 39.6% eight-cell robustness, and PPL ratio 1.080. This
jointly solved canonical storage and retention, but not prompt-invariant access.

#### Cross-family screen

| Model | Exact | Robust global/min | PPL ratio | Decision |
|---|---:|---:|---:|---|
| SmolLM2-1.7B | 100% | 39.6% / 21% | 1.080 | Failed robustness |
| Qwen2.5-1.5B | 100% | 99.6% / 99% | 1.461 | Failed retention only |
| StableLM2-1.6B | 100% | 93.8% / 69% | 1.477 | Failed held-out/per-relation/PPL gates |
| Gemma-2-2B | 97.8% | 78.0% / 7% | 704.873 | Failed this model--recipe combination |
| Llama-3.2-1B | 100% | 81.4% / 7% | 3.862 | Failed held-out/per-relation/PPL gates |

Qwen proved that the hybrid representation could support nearly perfect prompt robustness, but
the fixed recipe caused unacceptable generic drift. No retained Qwen checkpoint solved this by
early stopping: update 25 already had PPL ratio 1.409 while failing factual gates; update 50 was
the earliest factual pass with ratio 1.455.

### 6.7 Phase 6: Turkish corpus and the first bridge feasibility pilot

#### Frozen clean Turkish corpus

The dated June 2026 Turkish Wikipedia dump was officially checksum-verified, extracted,
normalized, audited, deduplicated, contamination-scanned, split, manually reviewed, and frozen.

Key counts:

- 505,016 deduplicated documents;
- 504,287 clean retained documents;
- 729 conservative removals;
- 494,253 train and 10,034 validation documents;
- zero retained synthetic full-name matches.

The corpus pipeline exposed and corrected legacy-schema, pattern-duplication, provenance, and
compact-review issues without promoting partial outputs. The final corpus and manifests are
scratch-only and hash-frozen.

#### First bridge contract and directions

The bridge evaluated M0, M1, low-dose, and full-dose states in EN-to-EN, TR-to-EN, and TR-to-TR,
together with English and Turkish PPL. This was a bounded feasibility pilot, not the final
Branch A/B causal experiment.

#### SmolLM bridge result

On 359 eligible facts, EN-to-EN stayed high (96.66% M1 to 96.10% full), Turkish PPL improved from
10.778 to 9.426, and English PPL improved relative to the M1 state. Yet TR-to-EN moved from 20.61%
at M1 to 20.06% low and 16.99% full. The adaptation had a real Turkish-language modeling effect
but did not open factual access.

#### Historical Qwen bridge result

On 497 eligible facts, EN-to-EN remained 100%, Turkish PPL improved from 22.007 to 13.378, and the
M1 English PPL ratio improved. However, TR-to-EN declined from an already-open 66.20% at M1 to
52.31% low and 46.48% full. Both adaptation doses produced negative paired changes.

The combined result was `not_viable_under_frozen_pilot` for both model families. This is valid
negative feasibility evidence: generic Turkish adaptation can improve Turkish PPL while leaving
factual access unchanged or worse. It is not a final prediction for the later, differently
trained and replicated Qwen artifacts.

### 6.8 Phase 7: Qwen clean-English replay and seed-instability diagnosis

Qwen's major weakness was generic English drift. A bounded intervention mixed the same factual
curriculum with a frozen clean-English replay anchor at coefficient 0.5.

In seed 42, replay step 50 became the sole joint Pareto point: 99.8% exact, 98% global robust,
91% minimum relation robust, and PPL ratio 1.24684. The literal frozen summarizer initially
rejected the correct one-word answer `navigation` plus EOS as near-empty because it contained at
most two token IDs. The original failure was preserved, and a separate lexical-content-based
adjudication opened seed-43 replication without overwriting the record.

The same 100-subject recipe did not replicate cleanly in seed 43. At step 50 the PPL ratio passed
but the minimum held-out C/D cell was only 72%; at step 75 factual gates passed but the PPL ratio
rose to 2.755. There was no common passing checkpoint. This result was treated as a real
replication failure, not an infrastructure error.

### 6.9 Phase 8: exploratory Qwen 2,500-fact scale probe and independent replication

The project then opened an explicitly exploratory scale diagnostic rather than retroactively
declaring the 100-subject recipe validated. It held the model, Relation V2 population, hybrid
curriculum, replay coefficient, 252-update budget, evaluator, gates, and selection rule fixed.

The seed-42 run showed a sharp checkpoint Pareto curve: step 25 had not acquired the facts;
steps 50/75 combined strong factual performance with low PPL drift; from step 100 onward factual
metrics stayed near ceiling while PPL deteriorated rapidly, reaching a ratio near 28 at the end.

The independent seed-43 replication passed the same frozen contract. The earliest-all-gates rule
selected different checkpoints, as expected:

| Metric | Qwen seed 42, step 75 | Qwen seed 43, step 50 |
|---|---:|---:|
| Canonical exact | 99.96% | 99.68% |
| Hard aggregate | 99.29% | 99.225% |
| Eight-cell robust | 96.08% | 96.20% |
| Minimum robust relation | 88.2% | 90.2% |
| Relation forced choice | 99.51% | 99.56% |
| PPL/base | 1.082 | 1.032 |
| Generic top-1 | 29/30 | 29/30 |
| Synthetic intrusion | 0 | 0 |

Both selected model-only artifacts have scratch manifests and SHA-256 records. This is the
project's strongest positive result and lifts the English intermediate-scale M1 acquisition hold
for Qwen. It does not establish 25,000-fact scaling or answer the Turkish causal question.

### 6.10 Phase 9: SmolLM contrastive and prompt-consistency comparison

#### Relation-matched ranking

Adding a relation-matched correct-versus-distractor loss improved SmolLM's mechanism-level
behavior:

| Condition | Exact | Hard | Eight-cell robust | Min relation | Forced choice | PPL |
|---|---:|---:|---:|---:|---:|---:|
| `lambda=0` | 100% | 87.525% | 39.6% | 21% | 89.4% | 17.1980 |
| `lambda=0.10` | 100% | 91.00% | 52.2% | 34% | 93.1% | 17.5234 |
| `lambda=0.25` | 100% | 90.975% | 50.4% | 32% | 94.1% | 17.5521 |

The `lambda=0.10` treatment improved robust retrieval by 12.6 points, showing that relation-matched
discrimination mattered. Increasing the coefficient did not solve prompt robustness and slightly
increased PPL.

#### A/B prompt-distribution consistency

The final bounded intervention added a consistency term across the four training-only A/B
direct/QA candidate distributions while keeping C/D fully held out. The best observed point was
step 250:

- exact 100%;
- hard 91.67%;
- eight-cell robust 55.8%;
- minimum relation 38%;
- forced choice 94.0%;
- PPL ratio 1.099;
- zero empty outputs and zero synthetic intrusion.

It improved the prior 52.2% result but missed the global robust gate by 14.2 points and the
per-relation gate by 32 points. `profession` Form C and `works_in_industry` Form D remained weak.
The branch was correctly closed without seed-43 or 2,500-fact scale-up.

## 7. Cross-method comparison: what changed and what was learned

| Method family | Intended mechanism | Main outcome | Scientific lesson |
|---|---|---|---|
| More epochs/LR/repetition | Increase factual exposure | No robust gain | Exposure alone is insufficient |
| Larger early model | Add capacity | Did not initially solve broad recipe | Capacity cannot repair an unsuitable supervision path by itself |
| QA mix and biographies | Add natural context/extraction cues | Low held-out retrieval | Presence in text is not robust binding |
| Two-stage acquire/extract | Separate storage and querying | Low retrieval despite lower loss | Optimization loss is not factual access |
| Ranking continuation | Align with candidate discrimination | Small or neutral gains | Seen-prompt discrimination need not generalize |
| Direct-aware supervision | Cover missing prompt family | Solved 1/10/50-fact ladder | Prompt-format coverage was a key early bottleneck |
| Relation V2 | Remove proper-name candidate collapse | Large controlled improvement | Candidate design and independence matter |
| City contrast/hard negatives | Separate same-subject city roles | Failed/neutral | Relation-role transfer is harder than seen contrast |
| Model capacity at 1.7B | Reduce 500-fact interference | Near-perfect simple direct/QA | Capacity matters, but hard form tests remain necessary |
| EOS removal | Remove learned short-answer termination | Replicated robust and behavior gain | Supervised EOS caused stopping bias |
| Balanced A/B | Teach multiple observed forms | Trained forms perfect, unseen forms weak | Form coverage is not form invariance |
| Canonical+A/B hybrid | Preserve storage and diversify access | Storage/PPL pass, unseen robustness fail | Canonical memory and robust binding remain distinct |
| Cross-family screen | Test architecture/tokenizer family | Qwen robust but drifted; Smol retained but fragile | Model family changes the Pareto frontier |
| Clean-English replay | Preserve generic English in Qwen | Enabled passing scale checkpoints | Retention data can repair Qwen's main failure |
| Relation-matched contrastive loss | Improve object discrimination | Smol robust 39.6% -> 52.2% | Correct mechanism direction, insufficient magnitude |
| A/B distribution consistency | Align seen prompt distributions | Smol robust 55.8% | Seen-form consistency does not guarantee unseen invariance |

## 8. Operational and reproducibility milestones

### 8.1 HU home storage incident

On 13 July, approximately 474 GB of experiment artifacts had accumulated on the shared HU home
filesystem and contributed to a service outage. The root cause was retaining checkpoints,
optimizer states, caches, and evaluation trees in home. The migration moved large artifacts to
scratch and reduced home-resident regular files to 7.88 GiB without deleting scientific results.

The permanent rule is now part of experiment correctness:

- home stores only source, small configs, manifests, hashes, and compact summaries;
- checkpoints, optimizer state, corpora, caches, evaluations, and verbose logs use `/vol/tmp` or
  `/vol/tmp2`;
- every large family requires capacity, inode, resolved-path, checkpoint-size, and retention
  preflight plus a post-run audit;
- selected artifacts require manifests and SHA-256 checksums before cleanup.

### 8.2 Operational failures as protected evidence

The project also encountered contaminated GPU allocations, OOMs on shared devices, stale
preflight windows, tokenizer-boundary errors, legacy Relation V1 schema assumptions, checksum URL
errors, match-stream explosion from duplicated object patterns, and evaluator aggregation bugs.

These were handled by preserving the scientific contract, stopping before model load or output
promotion when possible, correcting the infrastructure, testing the correction, and rerunning
only missing work. Operational failures were not counted as negative model results; scientific
failures were not relabeled as infrastructure problems.

### 8.3 Precommitment and append-only correction

Important examples of scientific discipline include:

- the V2 500-fact near-pass remained a failure under its frozen gate;
- the first 2,500-fact Smol run remained an exploratory override;
- the seed-42 Qwen integrity false positive was corrected in a separate adjudicated artifact,
  preserving the original summary;
- the Qwen scale checkpoints were selected by the earliest-all-gates rule;
- failed SmolLM conditions were retained instead of hidden;
- corpus and selected-model finalization used append-only manifests and checksums.

## 9. Scientific conclusions supported now

The current evidence supports the following conclusions:

1. The base models do not retrieve the controlled synthetic bindings above chance before
   acquisition.
2. Canonical storage and prompt-robust retrieval are distinct capabilities.
3. Training loss and canonical exact accuracy are insufficient measures of learned factual
   access.
4. Prompt-format coverage can be necessary for retrieval, but coverage of A/B forms does not
   guarantee invariance to C/D forms.
5. Relation-specific candidate design and independent assignment materially affect
   identifiability.
6. Fact-density can increase retrieval/binding interference while leaving exact storage intact.
7. Same-subject relation binding, especially `born_in` versus `lives_in`, is a meaningful hard
   diagnostic rather than noise to be removed.
8. Supervised answer-final EOS caused a replicated short-answer stopping bias.
9. Model families occupy different factual-robustness/generic-retention Pareto positions.
10. Clean-English replay can make Qwen's robust factual acquisition compatible with low PPL drift.
11. The Qwen 2,500-fact M1 result is replicated under a frozen evaluator and checkpoint rule.
12. SmolLM contrastive interventions improve binding but do not reach the downstream eligibility
    threshold.
13. Generic Turkish adaptation can improve Turkish PPL while cross-lingual factual access remains
    flat or declines.

## 10. Claims not yet supported

The project must not yet claim that:

- clean Turkish adaptation produces cross-lingual transfer under the new Qwen artifacts;
- Turkish fact repetition produces a quantified relearning increment;
- the Branch A/B difference-in-differences estimand has been measured;
- the 2,500-fact Qwen result automatically scales to 25,000 facts;
- all synthetic facts are prompt-independent or open-generation robust;
- SmolLM is a successful second M1/M2/M3 model;
- synthetic candidate-ranking results directly generalize to natural-world factuality;
- the answer-language hierarchy or final M2/M3 checkpoint rule has already been approved.

## 11. Current status as of 30 July 2026

| Workstream | Evidence status | Current decision |
|---|---|---|
| Qwen English M1, 2,500 facts | Passed in two independent seeds; selected artifacts frozen | Primary intermediate-scale candidate |
| Qwen English M1, 25,000 facts | Not run | Open scale decision |
| Historical Turkish bridge | Complete negative feasibility evidence | Must be re-baselined on new artifacts, not ignored or automatically reused |
| SmolLM ranking family | Mechanistically positive, gate failed | Closed as a main branch |
| SmolLM consistency V2 | Best robust 55.8%, gate failed | Closed without replication/scale-up |
| Frozen Turkish corpus | Complete and hash-frozen | Reusable after contract review |
| New Qwen bilingual contract | Not yet frozen | Required before training |
| Main M2/M3 causal experiment | Not run | HOLD |
| Active Slurm jobs | None | No monitoring or duplicate action required |

## 12. Assessment of the latest external opinion

The external assessment is valuable and broadly consistent with the recorded evidence. Its main
recommendations are:

- treat intermediate-scale Qwen M1 as solved sufficiently to justify a causal feasibility stage;
- stop optimizing SmolLM as a second main model and retain it as negative comparative evidence;
- use seed-42 and seed-43 Qwen artifacts as sibling causal chains;
- match M2 and M3 token/update budgets exactly;
- avoid treatment-specific factual checkpoint selection;
- measure TR-to-EN separately from TR-to-TR;
- prefer a bridge-first 2,500-fact causal feasibility study before spending resources on a
  25,000-fact M1;
- preserve Branch A/B and use a difference-in-differences analysis;
- make M3 replace neutral filler with factual rows rather than receive extra tokens.

This opinion is persuasive because it focuses the project on the thesis question rather than
continuing open-ended M1 optimization. It is not yet project authority. The following points
remain decisions for the user and supervisor:

1. bridge-first versus canonical-M1-first ordering;
2. two complete seed-specific causal chains versus discovery plus confirmatory staging;
3. whether TR-to-TR or TR-to-EN is the primary outcome;
4. whether M3-lexical is required or a simpler M2/M3 contrast is sufficient;
5. fixed endpoint versus a frozen non-factual checkpoint rule across adaptation arms;
6. the scale and strength of the first new Turkish adaptation dose.

## 13. Provisional forward plan for supervisor discussion

This section is a recommendation, not an authorized execution plan.

### Step 0: obtain supervisor alignment

Before new training, send a concise update to Max covering:

- the replicated Qwen 2,500-fact result;
- the closed SmolLM main branch and its value as negative evidence;
- the old bridge result and why it must be re-baselined;
- the proposed bridge-first versus 25,000-fact choice;
- the answer-language and seed-chain options.

The response should be recorded before declaring the causal-stage design final.

### Step 1: freeze the new bilingual contract

The next numbered plan should define:

- both selected Qwen M1 artifacts and their role as independent replicates;
- the exact frozen Turkish corpus subset and hashes;
- contamination exclusions against the full Relation V2 release;
- English and Turkish alias/candidate registries;
- EN-to-EN, TR-to-EN, and TR-to-TR probe sets;
- A/B/C/D direct/QA cells and relation floors;
- generic English/Turkish PPL and integrity checks;
- adaptation token/update budget and neutral filler rule;
- the endpoint/checkpoint rule;
- primary and secondary estimands;
- stop conditions, compute/storage estimates, and artifact retention.

### Step 2: re-establish current-M1 baselines

For both Qwen artifacts, reload the frozen model-only packages and verify:

- the English M1 gate remains unchanged;
- EN-to-EN, TR-to-EN, and TR-to-TR pre-adaptation access;
- relation and cell-level behavior;
- forced-choice binding;
- English and Turkish PPL baselines;
- zero contamination or manifest mismatch.

Low Turkish factual access at M1 is not a stop condition by itself; it provides headroom for a
transfer test. Near-ceiling Turkish access would reduce gain headroom and change the interpretation
toward preservation or degradation.

### Step 3: run a matched 2,500-fact causal feasibility family if approved

A strong design would use:

```text
Qwen M1 seed 42 -> sibling M2-42 and M3-42 arms
Qwen M1 seed 43 -> sibling M2-43 and M3-43 arms
```

Within each seed family, keep the Turkish document order, adaptation seed, token count, update
count, optimizer schedule, and checkpoint schedule fixed. Only factual exposure should change.

The minimum design is:

- M2: clean Turkish plus neutral matched filler;
- M3: the same clean Turkish with factual rows replacing the neutral filler.

The more controlled design also includes M3-lexical before M3-fact. Branch A receives no factual
repetition. Branch B receives the planned factual exposure only in the fact arm.

### Step 4: use frozen endpoints and causal estimands

Primary analysis should not select separate M2 and M3 checkpoints based on their Turkish factual
scores. Use a fixed update or a treatment-blind rule frozen in advance.

Report separately:

- M1-to-M2 change for Branch A and Branch B;
- M1-to-M3 change for Branch A and Branch B;
- M3 minus M2 difference-in-differences;
- if lexical arm exists, lexical-minus-clean and fact-minus-lexical increments;
- English factual retention and generic PPL;
- relation-, form-, branch-, name-, and frequency-level uncertainty;
- TR-to-EN and TR-to-TR without merging them.

### Step 5: make the 25,000-fact scale decision from evidence

The bridge-first recommendation is attractive because the thesis contribution is the
transfer-versus-relearning distinction, not merely 25,000-fact acquisition. If the mechanism does
not produce interpretable separation at 2,500 facts, scaling M1 first mainly increases cost. If it
does work in two seeds, the 25,000-fact run can become a deliberate scale-robustness or final
validation experiment.

However, if the supervisor requires the historical canonical population before any causal claim,
canonical-M1-first remains defensible. The report must then state that the 2,500-fact result is
strong intermediate evidence, not a guarantee of the 25,000-fact outcome.

### Step 6: preserve SmolLM as a comparative negative result

Do not run another SmolLM coefficient, seed, or scale experiment unless a new plan specifies a
mechanism that directly targets the remaining profession/C/D binding failure and answers a
distinct comparative question without delaying the Qwen causal line.

The existing SmolLM evidence already supports a strong thesis statement:

> Perfect canonical storage and low generic PPL drift are not sufficient for prompt-robust factual
> binding, and mechanism-aligned contrastive improvements can remain well below downstream causal
> eligibility.

## 14. Proposed stop conditions for the new Turkish stage

Do not start or continue the principal causal family if:

- a selected Qwen artifact does not reproduce its frozen English M1 metrics after reload;
- the Turkish corpus or filler fails contamination auditing;
- M2 and M3 token/update/exposure budgets are not exactly matched;
- cache, logs, outputs, or checkpoints resolve to HU home;
- the answer/alias registry or prompt contract is still ambiguous;
- the treatment endpoint can be selected after inspecting Turkish factual outcomes;
- a short smoke shows catastrophic English factual loss or a broken evaluator;
- the two seed families accidentally differ in more than their frozen seed identities.

The following are not automatic stop conditions:

- low pre-adaptation Turkish factual retrieval;
- a lack of immediate gain in a very small diagnostic dose;
- heavy scratch use that still fits measured capacity and inode availability.

## 15. Validity threats and interpretation boundaries

### Synthetic-data validity

Synthetic facts provide source control but do not reproduce all properties of real-world factual
knowledge. Conclusions should be limited to controlled synthetic bindings and framed as evidence
about mechanisms, not universal factuality.

### Candidate-ranking validity

Top-1 candidate ranking removes string-generation ambiguity but is not open-ended recall.
Secondary generation and lexicalization checks remain useful.

### Prompt-family dependence

The training curriculum was designed in response to observed prompt failures. Held-out C/D forms
reduce leakage, but they do not prove universal prompt invariance.

### Model-family and seed scope

The positive intermediate-scale result is two-seed Qwen evidence, not a universal model-family
claim. SmolLM supplies comparative negative evidence, while StableLM/Gemma/Llama were only tested
under specific fixed recipes.

### Scale scope

The current positive Qwen evidence covers 500 subjects and 2,500 facts. It must not be described
as the completed historical 5,000-subject/25,000-fact canonical design.

### Adaptation attribution

Turkish PPL improvement does not imply factual transfer. The old bridge results demonstrate this
directly. Only matched M2/M3 arms and a frozen causal estimand can support transfer-versus-relearning
claims.

## 16. Supervisor-ready presentation modules

The document can be presented in sections:

1. **Motivation and causal question:** Sections 2--3.
2. **Why synthetic facts and how the dataset evolved:** Section 4.
3. **How factual learning is measured:** Section 5.
4. **Why the early methods failed:** Sections 6.2--6.4.
5. **The storage-versus-retrieval discovery:** Sections 6.3--6.4.
6. **Supervisor follow-up, EOS, and prompt dependence:** Section 6.5.
7. **Model-family trade-offs and Turkish bridge warning:** Sections 6.6--6.7.
8. **Replicated Qwen milestone:** Sections 6.8--6.9.
9. **SmolLM as a controlled negative result:** Section 6.10.
10. **What is and is not established:** Sections 9--11.
11. **Decisions requested from the supervisor:** Sections 12--14.

## 17. Final milestone judgment

The project has moved through three qualitatively different stages.

First, it was an acquisition-engineering search in which broad M1 experiments failed and training
loss was repeatedly shown to be misleading. Second, it became a controlled diagnostic program
that separated storage, prompt transfer, relation binding, model capacity, EOS behavior, and
generic retention. Third, it produced a replicated Qwen intermediate-scale M1 artifact and a
well-controlled SmolLM failure boundary.

That progression is scientifically meaningful. The failed experiments are not noise surrounding
the final result; they explain why the current evaluator, gates, dataset, checkpoint rule, and
model choice are credible.

The project is now ready to leave open-ended M1 optimization, but it is not yet ready to claim
cross-lingual transfer or relearning. The next milestone should be a supervisor-approved,
outcome-blind bilingual contract followed by a matched, replicated Turkish causal feasibility
study. If that study is interpretable, the project can decide whether a 25,000-fact canonical
validation materially strengthens the thesis. If it is not, the result will still identify the
boundary between robust English factual acquisition and cross-lingual access.

## 18. Evidence map

| Topic | Primary documents |
|---|---|
| Original thesis question | `Expose.pdf`, 00, 01 |
| Early M0/M1 experiments | 04--47 |
| Acquisition ladder and direct supervision | 48--64 |
| Relation V2 and scale interference | 65--82 |
| HU storage incident | 84 |
| 1.7B capacity and generic drift | 83, 85--91 |
| Supervisor follow-up and pre-M2 HOLD | 93--98 |
| Master status and execution logic | 100 |
| Form remediation and model-family screening | 101--108 |
| Turkish corpus and old bridge pilot | 109--116 |
| Qwen replay and failed 100-subject replication | 117--121 |
| Qwen scale and SmolLM contrastive plans/results | 122--128 |
| Latest external-collaborator handoff | 129 |

