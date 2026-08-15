# 100 - Master Project Status And Execution Plan

**Date:** 2026-07-24

**Status (superseded operational snapshot; see 28 July correction below):** Documents 101--116 preserve the completed prompt-remediation, cross-family screening,
checkpoint, and Turkish-bridge evidence. Document 117 opened a bounded Qwen clean-English replay
remediation and made 500 subjects / 2,500 facts a mandatory M1 scale gate. Seed-42 training and all
22 checkpoint evaluations are complete. Document 118 records that replay step 50 passes every
factual, robustness, and PPL gate but is rejected by a length-only integrity heuristic that calls
the correct answer `navigation` plus EOS near-empty. The original frozen failure is preserved; a
separate adjudication finds replay step 50 to be the sole corrected passing checkpoint. Document
119 freezes the independent seed-43 replication, and Document 120 records its completed failure.
No checkpoint reproduces the seed-42 factual-robustness/PPL overlap. **Seed 43 is complete and
failed; 500-subject scale-up, final M1, M2, and M3 remain on HOLD.**

**Authority:** This document is the primary source for the current scientific state, accepted
results, scale contract, and execution order. Earlier numbered reports remain the immutable
evidence record. When an older planning statement conflicts with this synthesis, use this document
for current operations and consult the cited source report for the historical context.

> **28 July 2026 operational correction.** The status paragraph above is a preserved snapshot of
> the earlier retention-replay workstream, not the current Qwen-scale/SmolLM workstream. For the
> latter, Documents 122--125 are authoritative: Qwen seed-42 has completed its 2,500-fact
> exploratory scale probe; its robust/integrity summary and a frozen-rule seed-43 replication are
> pending. SmolLM seed-42 contrastive training is active, with an otherwise matched `lambda=0`
> control now authorized. M2/M3 remain HOLD until a replicated M1 candidate satisfies all frozen
> gates.

> **29 July 2026 result correction.** Documents 122--127 complete the exploratory scale branch.
> Qwen2.5-1.5B clean-English replay now has a replicated 500-subject/2,500-fact English M1
> candidate: seed-42 selects step 75 and seed-43 selects step 50 under the frozen
> earliest-all-gates rule; both selected model-only artifacts have scratch manifests and SHA-256
> records. SmolLM2-1.7B `lambda=0`, `lambda=0.10`, and exploratory `lambda=0.25` evidence remains
> below the 70% robust gate, so that branch is closed without seed-43 or scale-up. This lifts the
> **English M1 acquisition** HOLD for the selected Qwen pair, but it does not by itself reopen
> M2/M3: the independent negative Turkish-bridge feasibility evidence recorded in Documents
> 115--116 remains applicable until a new Turkish-stage contract is explicitly frozen.

> **29 July 2026 SmolLM remediation correction.** Document 127 closes only the completed
> relation-matched ranking-coefficient branch (`lambda=0`, `0.10`, and exploratory `0.25`), not
> SmolLM as a scientifically informative comparator. At the user's instruction, Document 128
> opens one new bounded 100-subject/500-fact seed-42 discovery intervention: canonical answer-only
> LM plus the already frozen `lambda=0.10` ranking term and a new A/B-only candidate-distribution
> consistency term. It must independently pass the frozen 70% robust gate before a seed-43 run or
> scale-up can be considered. Qwen remains the sole replicated 2,500-fact English M1 result, and
> M2/M3 remain HOLD.

> **30 July 2026 SmolLM V2 result correction.** Document 128's canonical-LM plus A/B
> prompt-distribution-consistency seed-42 sweep completed. Its best observed point, update 250,
> has 100% exact acquisition, 91.67% hard top-1, 55.8% eight-cell robust retrieval, a 38% weakest
> relation, and PPL ratio 1.099. It passes PPL and generic integrity but misses the frozen 70%
> global/per-relation robust gate; no checkpoint is eligible. The V2 SmolLM branch is closed
> without seed-43 or 2,500-fact scale-up. Qwen remains the sole replicated 2,500-fact English M1
> result; Turkish M2/M3 remain HOLD.

> **30 July 2026 upper-canonical-scale authorization.** At the user's explicit instruction,
> Document 131 opens one Qwen2.5-1.5B seed-42 upper-canonical-scale validation over all 5,000
> Relation V2 subjects / 25,000 facts. It preserves the replicated replay recipe, 252-update
> budget, and single-GPU execution by scaling gradient accumulation from 50 to 500. This is one
> exploratory scale run, not an automatic replacement for the frozen 2,500-fact seed-42/43 pair
> and not an authorization for a parallel seed, M2, M3, or an automatic evaluation wave. HU
> submission remains blocked until the Document 131 dataset, replay, resume-smoke, storage/path,
> queue, clean-GPU, and user go/no-go gates pass.

> **30 July 2026 upper-scale preparation status.** Code is pushed and HU is synchronized at
> `81d45f6db1b87313927b87bb9c697b13d542cc63`. Compute-node test job `439439`, preparation
> preflight `439440`, and 25,000-fact materialization job `439444` passed. The frozen scratch
> dataset has 175,000 balanced factual rows, 25,000 exact probes, 200,000 hard probes, ten-cycle
> matched replay, zero Form C/D training exposure, and zero 5,000-subject replay contamination
> hits. Smoke job `439445` stopped correctly before model load because its Slurm-assigned A100
> already contained a foreign process; all `gruenau10` A100s were physically occupied despite
> only one being Slurm-accounted, while all `gruenau9` A100s were allocated. No duplicate was
> submitted. The launcher now checks GPU cleanliness before creating canonical smoke output.
> Main training remains unsubmitted and blocked on a clean smoke/resume pass, a fresh Friday
> preflight, acceptable live contention, and explicit user go/no-go approval. See Document 131.

> **30 July 2026 selected-model durability status.** Ralf Moritz explicitly authorized current
> HU-home use below 30 GB and the additional approximately 6.2 GB for the two selected Qwen M1
> models; he confirmed that scratch has no backup or retention guarantee. CPU job `439465` copied
> only seed-42 step 75 and seed-43 step 50 model-only packages plus shared tokenizer and manifests
> to `/vol/fob-vol6/mi25/yesildau/frozen-models/qwen_m1_selected_v1`. It completed in 9m39s with
> empty stderr. Archive manifest SHA-256 is
> `29098e221dd1be47a68fecc35a430c6784acc807e4ff5a04b1eda7c95a2980d8`; post-copy home use is
> approximately 14 GiB. Scratch originals remain untouched. See Documents 84 and 127.

> **30 July 2026 late-night upper-scale operational status.** Storage/preflight logic was aligned
> with the administrator-approved 30-GB HU-home ceiling while preserving the narrow selected-model
> exception and scratch-only rule for high-volume execution. Commit
> `15279338b6c28756485916078ef867fa3fca42df` is pushed and synchronized exactly on HU.
> Compute-node job `439526` passed all 234 tests on that commit in 3m13s with empty stderr.
> Normal-priority, non-exclusive A100 smoke `439521` is pending without holding resources; the
> canonical smoke path is still absent. Main 25,000-fact training remains unsubmitted and blocked
> on the clean smoke/resume report, a fresh Friday preflight, acceptable live contention and start
> time, and explicit user approval. See Document 131 section 9.4.

> **30 July 2026 late-night Slurm placement correction.** The `gpu` partition's 8,000-MB
> per-CPU cap caused the nominal `8 CPU + 64G` request to require `MinCPUsNode=9`. Smoke and main
> now request `8 CPU + 60G`; no scientific hyperparameter changed. Commit
> `6969a5037b1787d73e16611afb4ca3af3972979a` is pushed, exact on HU, and passed all 234 tests in
> job `439541`. The obsolete pending smoke `439521` was cancelled. Corrected smoke `439542`
> proved immediate eight-CPU placement but stopped before model load when Slurm assigned a
> foreign-process-contaminated `gruenau10` GPU; canonical smoke output remains absent. Active
> smoke `439543` is constrained to `gruenau9`, pending without holding resources behind the job
> currently occupying all three A100s. The Friday main start is not guaranteed and remains blocked
> on the successful smoke plus every existing go/no-go gate. See Document 131 section 9.5.

> **31 July 2026 final gruenau10 smoke retry.** At the user's explicit request, job `439673` made
> one last guarded attempt on gruenau10. Slurm again assigned physical GPU 0, where four foreign
> Python processes occupied approximately 47.8 GiB. The job exited with guard code 3 after two
> seconds, before model load or canonical output creation. Gruenau9-only smoke `439543` remains
> pending without holding resources. No further gruenau10 retry is justified unless the
> Slurm-versus-physical GPU allocation mismatch is administratively corrected. See Document 131
> section 9.6.

**Numbering note:** Document 99 is intentionally unused at the user's request. Document 100 marks
the consolidated transition from exploratory M1 work to the controlled final execution ladder.

## 1. Thesis Question

The thesis asks:

> When factual knowledge becomes retrievable in Turkish after Turkish adaptation, does that
> retrieval reflect cross-lingual access to facts previously acquired in English, or Turkish-side
> reaffirmation/relearning caused by repeating those facts during adaptation?

The experiment uses fictitious subject--relation--object facts so that their acquisition history
is controlled and natural-data contamination can be audited.

## 2. Canonical Causal Design

### 2.1 Model states

| State | Starting point | Training intervention | Scientific role |
|---|---|---|---|
| M0 | Pinned base model | None | Pre-acquisition baseline |
| M1 | M0 | English-only synthetic fact acquisition | Establish English parametric knowledge |
| M2-clean | Frozen M1 | Clean generic Turkish adaptation with no correct target bindings | Test transfer/cross-lingual access |
| M3-lexical | Same frozen M1 | Matched adaptation plus Branch B entities/labels without correct bindings | Isolate entity/lexical alignment |
| M3-fact | Same frozen M1 | Matched adaptation plus correct Turkish Branch B facts | Test factual reaffirmation/relearning |

All adaptation arms must start independently from the same frozen M1 checkpoint. Neither M3 arm is
a continuation of M2 or of the other M3 arm.

### 2.2 Canonical population

The current Relation V2 dataset contract is:

- 5,000 subjects in total;
- 2,500 Branch A subjects;
- 2,500 Branch B subjects;
- five facts per subject;
- 25,000 English M1 facts in total;
- 12,500 facts per branch.

Current relations:

- `profession`;
- `born_in`;
- `lives_in`;
- `field_of_study`;
- `works_in_industry`.

The historical `studied_at` and `works_at` relations were replaced because their proper-name
inventories caused severe tokenization, prior, and binding problems. Their failed results remain
valid negative evidence, but they are not part of final Relation V2.

### 2.3 Branch meaning

All Branch A and Branch B facts receive the same English acquisition treatment in M1. Branch is a
later Turkish-exposure assignment, not a reason to train separate English M1 models.

- Branch A remains transfer-only: its facts are never repeated in Turkish adaptation.
- Branch B is the reaffirmation/relearning condition: its facts are repeated in Turkish only in
  M3.
- M2 contains no target synthetic fact from either branch.

The final M1 therefore trains all 5,000 subjects together. Training only 2,500 subjects would
cover one branch and would not implement the canonical causal design.

### 2.4 Primary causal comparison

Document 109 refines the original single M2-versus-M3 contrast into two controlled increments. The
true factual re-exposure estimand is:

```text
(M3-fact - M3-lexical change) for Branch B
minus
(M3-fact - M3-lexical change) for Branch A
```

The analogous M3-lexical-versus-M2-clean difference-in-differences estimates entity/lexical
alignment. Pure transfer is the pre/post M2-clean change for facts never exposed in Turkish.

English retention is measured after adaptation so that Turkish gains are not interpreted without
checking whether the original English knowledge survived.

## 3. Scale Vocabulary

The project uses four nested acquisition levels:

| Level | Subjects | Facts | Role |
|---|---:|---:|---|
| Micro gate | 10 | 50 | Pipeline and acquisition feasibility |
| Recipe-development pilot | 100 | 500 | Controlled diagnosis and ablation |
| Intermediate scale control | 500 | 2,500 | Capacity/interference validation |
| Upper canonical scale | 5,000 | 25,000 | Historical full population: 2,500 A + 2,500 B; now conditional on the 500-subject power/scaling decision |

“2,500” can refer to two different quantities and must always be labeled:

- 2,500 **facts** = the 500-subject intermediate control;
- 2,500 **subjects per branch** = half of the final 5,000-subject population.

The 100-subject/500-fact setting is a balanced diagnostic pilot, not the final population-level
M1 experiment.

## 4. How The Project Reached The Current Design

### 4.1 Initial full-scale attempts

Early M1 recipes trained directly on the full synthetic inventory. They did not establish robust
English retrieval. These failures motivated an acquisition ladder rather than continued
full-scale recipe search.

### 4.2 Diagnostic acquisition ladder

The project introduced nested 10-, 100-, and 500-subject levels to distinguish:

- failure to store a mapping;
- memorization of training strings;
- failure to transfer across prompt forms;
- relation-binding confusion;
- scale-induced capacity/interference failure.

Direct-aware, answer-only training solved the tiny controls and showed that the model could learn
all five relation families when the scale was small.

### 4.3 Relation V2 redesign

The weak `studied_at` and `works_at` relations were replaced by independently assigned,
short-answer `field_of_study` and `works_in_industry` relations. Candidate balance, dependence,
tokenization, base-prior, and leakage audits were completed before promotion.

### 4.4 360M scale diagnosis

SmolLM2-360M demonstrated that exact storage and prompt-robust retrieval are different:

| Scale | Exact | Direct | QA | Direct/QA overlap |
|---|---:|---:|---:|---:|
| 100 subjects / 500 facts | 500 | 378 | 377 | 329 |
| 500 subjects / 2,500 facts | 2,498 | 1,249 | 1,293 | 958 |

At 2,500 facts, exact storage remained 99.92%, but normalized robust overlap fell to 38.3%. The
full 25,000-fact recipe was correctly blocked. This is evidence of scale-sensitive
retrieval/binding interference, not inability to copy answer strings.

### 4.5 1.7B capacity control and replication

Moving to SmolLM2-1.7B nearly closed the original 500-fact direct/QA gap:

| Run | Selected checkpoint | Exact | Direct | QA | Overlap/triple |
|---|---:|---:|---:|---:|---:|
| Seed 42 | 200 | 500 | 499 | 498 | 497 |
| Seed 43/data seed 43 | 75 | 500 | 500 | 499 | 499 |

These runs used the historical `1e-4` answer-only recipe with supervised EOS. They proved that
model capacity resolves most of the simple 500-fact retrieval plateau and that the result is not
specific to one data order.

### 4.6 General-capability audit

The same historical 1.7B checkpoints increased matched generic English perplexity by about
17--19%:

- base PPL: 15.924;
- seed-42 checkpoint 200: 19.018, ratio 1.194;
- seed-43 checkpoint 75: 18.681, ratio 1.173.

Common-knowledge candidate ranking remained 30/30, so this was measurable generic-loss drift,
not broad collapse. The models also developed an abnormal tendency to terminate generic
completions with EOS after short answers.

## 5. Max Follow-Up Plan: What Was Done

Plan 93 converted the supervisor's questions into five work packages. Reports 94--97 contain the
complete job, artifact, hash, and storage records.

### 5.1 WP1A, WP2, and WP4 - frozen hard evaluation

Both historical selected 1.7B checkpoints were evaluated under harder direct and QA forms.

- Seed 42: 2,882/3,000 hard probes correct.
- Seed 43: 2,807/3,000 hard probes correct.
- Required A/B four-cell robust facts: 466/500 and 457/500.
- Novel Form C was materially harder and more seed-sensitive.
- Most remaining swaps were concentrated in `lives_in`, with additional weaknesses in
  `profession`.

Teacher-forced likelihood showed that the trained models strongly preferred the correct gold
tokens before generation. Final-answer EOS probability was near one, confirming that the models
learned both the answer mappings and an excessively strong short-answer stopping rule.

### 5.2 WP1B - subject-form counterbalance and swap replication

This was the decisive causal paraphrase test. Each subject was trained through only one assigned
form and evaluated on the held-out crossed form; the assignment was then swapped and replicated.

- Seen-form retrieval: 100% in both conditions.
- Crossed performance: 390/1,000 (39.0%) and 388/1,000 (38.8%).
- Novel Form C: 46.3% and 47.8%.
- Required A/B four-cell robust facts: 140/500 (28.0%) and 142/500 (28.4%).
- Frozen robust threshold: 350/500 (70%).

The large seen-minus-crossed gap reproduced after the swap. The failure is therefore caused by
subject-specific form exposure, not an accidental easier/harder split between Forms A and B.

### 5.3 WP3 - joint paired-relation control

The model jointly learned 100 subjects across `studied_at`, `field_of_study`, `works_at`, and
`works_in_industry` for the supervisor's relation-pair diagnostic.

- Seen: 795/800 (99.4%).
- Crossed: 372/800 (46.5%).
- Novel: 547/800 (68.4%).
- Robust four-cell intersection: 130/400 (32.5%).
- Same-subject relation-swapped forced choice: 2,248/2,400 (93.7%).

The model mostly distinguishes the paired relations, but open-ended access remains dependent on
subject wording. Conditional seven-relation Stage B was not activated because Stage A answered
the relation question while failing the active prompt-robustness gate.

### 5.4 WP5 - learning-rate and EOS causal audit

The controlled LR sweep established a factual-learning versus retention trade-off:

- `2e-5`: low drift, but underlearned the factual task;
- `5e-5`: exact acquisition with PPL ratio below 1.10;
- `1e-4`: stronger hard factual scores with measurable drift;
- `2e-4`: highest factual scores but severe generic degradation.

Removing supervised answer-final EOS at `5e-5` replicated across seeds:

| Seed | EOS supervised | Hard | Robust | Exact | PPL ratio | Generic EOS endings |
|---:|---|---:|---:|---:|---:|---:|
| 42 | true | 74.1% | 46.9% | 100% | 1.077 | 27/30 |
| 42 | false | 77.9% | 52.4% | 100% | 1.082 | 0/30 |
| 43 | true | 73.1% | 44.5% | 100% | 1.076 | 27/30 |
| 43 | false | 76.2% | 50.1% | 100% | 1.084 | 0/30 |

EOS supervision is a replicated cause of the stopping bias. Learning rate remains a separate
cause of the wider factual/retention trade-off.

## 6. Current Scientific Conclusions

The evidence supports all of the following claims simultaneously:

1. SmolLM2-1.7B can store all 500 canonical English fact completions in the current pilot.
2. The historical multi-form 1.7B training distribution supports excellent direct/QA retrieval.
3. Deliberately holding out a subject form reveals severe subject-form dependence.
4. The model generally distinguishes close relation pairs; relation confusion is not the sole
   cause of open-ended failure.
5. Supervised EOS causes a reproducible short-answer stopping bias.
6. `5e-5` with EOS supervision disabled gives the best observed factual/retention compromise.
7. Exact storage alone is not sufficient evidence that a fact is ready for cross-lingual transfer
   analysis.
8. The current evidence covers 100 subjects/500 facts, not the final 5,000-subject population.

The defensible current claim is:

> SmolLM2-1.7B acquires all 500 canonical fact mappings in the balanced 100-subject pilot, but the
> current acquisition procedure has not yet demonstrated sufficiently prompt-invariant access to
> them, and the recipe has not yet passed the canonical scale ladder.

## 7. Current Decision And Frozen Reference Points

### 7.1 Decision

**M2 status: HOLD.**

M2 must not start as the final thesis experiment because:

- the crossed subject-form gate fails reproducibly;
- the selected Pareto recipe remains below the 70% robust threshold;
- the new 1.7B recipe has not passed the 500-subject/2,500-fact scale control;
- final 5,000-subject/25,000-fact M1 has not been trained and frozen.

A deliberately labeled 100-subject M2 pilot would be a scope change and requires explicit user
and supervisor approval. It must never be reported as the final canonical experiment.

### 7.2 Historical reference checkpoints

Retain as scientific controls:

- seed-42 historical `1e-4`, EOS-supervised checkpoint 200;
- seed-43/data-seed-43 historical `1e-4`, EOS-supervised checkpoint 75.

They remain the strongest simple direct/QA 500-fact controls, but they are not the future final M1
recipe because of drift and stopping-bias evidence.

### 7.3 Current Pareto starting recipe

The starting recipe for remediation is:

- SmolLM2-1.7B;
- LR `5e-5`;
- answer-only causal loss;
- `supervise_eos: false`;
- checkpoint/update 252 as the evaluated endpoint;
- seed 42 discovery and seed 43 replication.

This recipe is a starting point, not a frozen final M1 recipe. It must be combined with a
controlled form-generalization intervention and must pass the scale ladder.

## 8. Completed And Outstanding Work

### Completed

- canonical synthetic dataset and Branch A/B assignment;
- Relation V2 replacement and integrity audits;
- 10-, 100-, and exploratory 500-subject dataset packages;
- 360M acquisition and scale diagnosis;
- 1.7B 100-subject capacity control and independent replication;
- generic-capability degeneration evaluation;
- hard paraphrase and token-likelihood evaluation;
- subject-form counterbalance plus swap replication;
- joint paired-relation diagnostic;
- LR sweep and replicated EOS ablation;
- Document 101 matched-budget form-generalization discovery and Document 102 result;
- Document 103 canonical-plus-form-diversity SmolLM2 discovery and Document 104 result;
- HU storage incident remediation and scratch-only artifact policy;
- final pre-M2 HOLD decision.

### Not completed

- a Qwen or SmolLM bridge candidate with frozen bilingual feasibility evidence;
- a 100-subject/500-fact candidate that jointly passes exact, unseen-form, and retention gates;
- a passing 1.7B 500-subject/2,500-fact scale control;
- an evidence-based selected-scale M1 after the 500-subject decision;
- final M1 artifact freeze and learned-fact membership freeze;
- M2 generic Turkish adaptation;
- M3 Branch B repetition/relearning adaptation;
- final English-retention, Turkish-transfer, and difference-in-differences analysis.

Documents 103--104 and the Document 105--106 cross-family screen have finished and failed their
respective frozen gates; do not rerun or scale them as though they passed. Documents 107--108 also
rule out selecting an earlier retained Qwen checkpoint. Document 109 freezes the new order: bridge
implementation and pilot first, then a conditional bounded Qwen retention intervention.

## 9. Required Execution Plan From Here

No phase may open until the preceding gate is evaluated and documented.

### Phase 1 - Document 101 form-generalization discovery - completed, failed

Balanced A+B question-only training reached 100% on trained A/B cells but only 46.6--62.4% on
held-out C/D cells, 9.4% exact-prefix, and 11.8% eight-cell robust intersection. Generic retention
remained strong at PPL ratio 1.041. Seed 43 and scale-up were correctly blocked. See Document 102.

### Phase 2 - Document 103 canonical plus form-diversity remediation - completed, failed

The completed seed-42 hybrid condition used the same seven-row and 252-update budget:

- three byte-identical historical canonical declarative rows;
- Form A under direct and QA scaffolds;
- Form B under direct and QA scaffolds;
- Forms C/D held out;
- Reference H: existing WP5 canonical-mix endpoint;
- Reference Q: existing Document 101 balanced-A+B endpoint.

Document 104 records 100% exact-prefix and trained A/B accuracy, 75.05% held-out C/D accuracy,
39.6% eight-cell robust intersection, and a passing 1.080 generic PPL ratio. Exact storage was
restored but held-out retrieval failed, so seed-43 and scale-up were blocked.

### Phase 2B - Documents 105--106 cross-family model screen - completed, failed

Reuse the Document 104 SmolLM2 result without retraining it. Train Qwen2.5-1.5B,
StableLM2-1.6B, and Gemma-2-2B under the byte-identical hybrid dataset, fixed recipe, update-252
endpoint, and frozen evaluation gates. Include Llama-3.2-1B only if authenticated access, license,
tokenization, memory, checkpoint, and evaluator compatibility gates pass. The qualifying new
models may train in one parallel Slurm wave with one combined family-level storage preflight.

Document 105 freezes candidate IDs, native-tokenizer audits, compatibility gates, fixed-recipe
fairness limits, evaluation suites, selection rules, scratch layout, and result-report contract.
No candidate advances merely by ranking first; it must pass every frozen gate.

Document 106 records that no candidate passed. Qwen passed every factual/robustness gate but failed
PPL ratio at 1.461. StableLM was the strongest non-Qwen family but missed minimum held-out and
robustness cells and also failed PPL. Gemma and Llama failed more severely.

### Phase 2C - Documents 107--108 Qwen checkpoint Pareto diagnostic - completed, failed

All retained Qwen checkpoints from updates 25 through 252 were evaluated. Update 25 already had
PPL ratio 1.409 while failing factual gates. Update 50 was the earliest checkpoint passing every
factual and prompt-robustness gate, but its PPL ratio was 1.455. No checkpoint passed all gates, so
early stopping is ruled out and no checkpoint is nominated.

### Phase 2D - Document 109 Turkish bridge and conditional retention plan - frozen, not launched

Document 109 places a bounded Qwen/SmolLM Turkish bridge pilot before any conditional Qwen
retention intervention. No training begins until Phase 109A freezes and audits the Turkish corpus
splits, contamination exclusions, localized answer/candidate contract, eligible English fact
sets, bilingual evaluator, numeric low/full doses, compute/storage estimate, and HU paths. If Qwen
is promising, the later retention family keeps the 100-subject/500-fact curriculum and factual
exposure fixed while comparing a matched control, English replay, and base-model KL retention.

### Phase 3 - Seed-43 selected-family replication

Open only if the Document 109 bridge decision is promising and a conditional seed-42 acquisition
condition passes exact, every held-out C/D cell, eight-cell robust, integrity, and generic-retention
gates. Replicate only the precommitted selected family and treatment under seed/data seed 43.

### Phase 4 - Confirm joint relation behavior

After both hybrid seeds pass, rerun the paired-relation control using the passing curriculum.
Require both:

- open-ended held-out-form robustness; and
- same-subject relation-swapped distinction.

The historical seven-relation Stage B remains conditional and is not automatically required.

### Phase 5 - 500 subjects/2,500 facts with the selected model family

Run the intermediate scale control only after the Phase 2 hybrid curriculum also passes the
Phase 3 seed-43 replication and Phase 4 paired-relation confirmation.

Historical proportional minimums remain useful lower bounds:

- exact at least 2,250/2,500;
- direct at least 2,000/2,500;
- QA at least 2,000/2,500;
- direct/QA overlap at least 1,750/2,500.

The Phase 5 plan must additionally translate the newer held-out-form and per-relation robustness
gates before results are seen. Evaluate nested retention of the original 100-subject subset to
measure interference directly.

### Phase 6 - Scale audit and evidence-based final-size decision

If Phase 5 passes, compare 100- and 500-subject learning curves, update counts, subgroup behavior,
relation behavior, generic retention, runtime, memory, checkpoint size, and scratch demand.

Then freeze a power/scaling decision. Continue with 500 subjects when it provides adequate
precision; increase to 1,000 only when the 500-subject result is valid but underpowered; consider
5,000 only when the documented analysis shows it is scientifically necessary. Any dedicated
full-M1 plan must contain:

- the selected subject/fact count and its evidence-based justification;
- equal subject counts per branch and five facts per subject;
- identical English acquisition treatment across branches;
- precommitted full-scale factual and robustness thresholds;
- 3-GPU parity smoke test if distributed training is used;
- expected checkpoint count and total storage estimate;
- scratch layout and retention policy;
- evaluation schedule and stopping rule;
- branch, relation, name-type, rarity, popularity, and frequency audits.

Do not derive full-scale thresholds after seeing the full-scale results.

### Phase 7 - Train, evaluate, and freeze the selected-scale M1

Train the selected-scale model only after the full plan and HU storage preflight pass. Select a
checkpoint using the frozen rule. Freeze:

- model-only weights, config, tokenizer, and training manifest;
- source and derived dataset manifests;
- exact/direct/QA and hard-form results;
- English learned-fact membership;
- subgroup and branch-parity summaries;
- generic-retention evidence;
- SHA-256 checksums.

Only facts meeting the frozen English learned-fact definition enter the primary M2/M3 causal
analysis.

### Phase 8 - M2-clean generic Turkish adaptation

Start from frozen final M1. Use a clean generic Turkish corpus that passes contamination auditing
and contains no target synthetic facts. Freeze token, optimizer, and checkpoint budgets before
training.

Measure:

- English retention;
- Turkish retrieval before and after adaptation;
- Branch A/B parity before Turkish repetition;
- relation and subgroup transfer;
- robustness across frozen Turkish prompt forms.

### Phase 9 - M3 lexical and fact arms

Start both arms independently from the same frozen M1 checkpoint. Match the M2-clean generic
Turkish corpus, token budget, optimizer budget, and evaluation schedule. M3-lexical exposes Branch
B subject names and Turkish labels without the correct relation binding; M3-fact exposes the
correct Turkish facts. Use shuffled/counterbalanced lexical material so co-occurrence cannot leak
the correct binding.

Branch A receives no Turkish fact repetition. Any unavoidable token-budget displacement caused by
Branch B insertion must be handled by a precommitted matched-corpus rule.

### Phase 10 - Final causal analysis

Report:

- M2-clean transfer gains for Branch A and Branch B;
- M3-lexical and M3-fact gains for Branch A and Branch B;
- the precommitted lexical-versus-clean and fact-versus-lexical difference-in-differences estimands;
- English retention and forgetting;
- relation-, frequency-, name-type-, and branch-level uncertainty;
- robustness across English and Turkish prompt forms;
- failures, missing facts, and sensitivity analyses without post-hoc relabeling.

## 10. Immediate Next Action

The next action is **not** to launch M2, seed 43, scale-up, or the 5,000-subject run.

Documents 107--109 are complete as evidence/plan documents. Early stopping is not a solution.
Phase 109A local implementation now freezes the localization/candidate registry, direction-explicit
bilingual evaluator, paired-bootstrap promotion rule, and numeric low/full doses at 262,144 and
1,048,576 supervised tokens. The remaining action is to synchronize the reviewed code, restore a
verified HU connection, freeze remote Qwen/SmolLM eligible sets and corpus hashes, audit tokenizer
blocks, materialize configs, and complete the combined storage/inode/path/queue preflight. The
eligible contract is now frozen at 497 Qwen, 359 SmolLM, and 357 shared eligible facts. Corpus
preflight job 410142 passed with HU home at approximately 7.91 GiB, `/vol/tmp2` at approximately
115 TiB free, 3% inode use, and all high-volume destinations resolved to scratch. The dated Turkish
Wikipedia corpus itself is not yet present: job 410143 stopped at an over-strict nonexistent-path
guard and job 410144 stopped at Wikimedia metadata HTTP 403 before downloading data. The local
launcher now uses safe missing-path resolution, requests carry an identifying User-Agent, and a
reusable Slurm preflight is ready. Fresh preflight 410145 passed and released corpus job 410146,
but that job stopped before download because the checksum filename lacked Wikimedia's date-scoped
prefix. Official HEAD checks verified the approximately 1.036 GB dump and the correct
`trwiki-20260601-sha1sums.txt` URL; commit `d35e200` freezes the corrected config and regression
test. Commit `d35e200` is now synchronized. Fresh preflight 410147 passed and released corpus job
410148, which is running on `gruenau3`; official metadata resolved, the correct dump `.partial` is
growing under `/vol/tmp2`, and initial stderr is empty. Do not duplicate the job. After it reaches
terminal state, perform the storage audit and freeze the clean split/manifest hashes. Only then may
the bounded bridge pilot
start. Qwen retention training remains conditional on a promising
bridge result. Do not launch seed 43, scale-up, final M1, M2, or M3.

## 11. HU Operational Contract

The shared HU home filesystem is not an experiment-artifact store.

- Home root: `/vol/fob-vol6/mi25/yesildau`.
- Large artifacts must use `/vol/tmp/yesildau` or `/vol/tmp2/yesildau`.
- Training outputs, model weights, checkpoints, optimizer state, corpora, caches, raw evaluations,
  and verbose logs must remain on scratch.
- Repository-local output paths must be resolved with `readlink -f` before submission.
- Home usage, filesystem capacity, and inode capacity must be checked before and after every large
  family.
- Expected checkpoints, approximate checkpoint bytes, total family size, and retention policy must
  be recorded before submission.
- Selected artifacts require manifests and SHA-256 checksums before cleanup.

Scratch may be used heavily when actual free space and inode counts show that the run fits. The
strict boundary is protecting HU home, not imposing an arbitrary project-level scratch limit.

When a job will take more than five minutes, submit it, verify that it entered `RUNNING`, inspect
stderr for immediate failure, report the expected average and safe duration range, and return
control to the user. Do not use sleep-based monitoring. Do not submit a duplicate merely because
output is temporarily quiet.

### 11.1 Workspace and repository map for agents

The workspace root is an orchestration directory, not a Git repository. Do not run a root-level
commit and do not assume one branch controls every directory.

| Path | Role | Git/handling rule |
|---|---|---|
| `documentation/` | Chronological scientific record and this master handoff | Preserve history; add numbered plans/results |
| `transfer-vs-relearning/` | Main training, evaluation, configs, tests, and Slurm code | Separate Git repo; current branch `corpus-update` |
| `syntheticFacts/` | Canonical synthetic-data generator and Relation V2 release logic | Separate Git repo; current branch `relation-redesign-v2` |
| `ssh-client/` | Local HU credential helpers and historical submission wrappers | Read `ssh-client/README.md`; never expose `.env` |
| `tmp/`, `outputs/` | Local intermediates and rendered material | Do not treat as canonical evidence without a manifest/report |

As of this handoff, both Git repositories contain intentional untracked generated outputs. They
belong to the user and must not be deleted, reset, broadly added, or committed automatically. Run
`git status --short --branch` inside each repository before editing or committing.

### 11.2 Shell launcher rule

The existing files under `ssh-client/scripts/` are historical experiment-specific launchers, not
generic entrypoints. They may contain old configs, run IDs, checkpoint lists, node choices,
relative output paths, or fixed scratch namespaces. Their filenames do not authorize reuse.

Before any HU action, read `ssh-client/README.md`. A new experiment requires a new versioned config
and narrowly named launcher after its numbered plan is frozen. Audit the full launcher, Slurm file,
and resolved paths before submission. In particular:

- `ssh_hu_gpu.sh` is the preferred visible interactive connection helper;
- most legacy automated wrappers use `hu_ssh_expect` and require `ssh-client` as their working
  directory because `.env` is resolved there;
- `hu_ssh_run.exp` has a short silence timeout and must not be used for long remote work;
- no helper may be used in a way that prints `.env` or leaves a hidden password prompt;
- legacy Slurm files with repository-local `logs/` are unsafe templates until logs are rerouted to
  absolute scratch.

### 11.3 Minimal agent decision tree

- Asked to explain or report status: read Document 100 and the cited evidence; use read-only checks.
- Asked to diagnose a failed job: inspect `squeue`/`sacct`, scratch logs, manifests, paths, and
  storage; do not relaunch or fix unless requested.
- Asked to plan the next experiment: create/finalize the next numbered plan and freeze variables,
  gates, compute, storage, and retention before code or submission.
- Asked to implement: work in the correct Git repository, preserve dirty files, add tests/configs,
  and do not submit unless submission is also requested or clearly part of the accepted workflow.
- Asked to launch: complete code sync, HU preflight, path resolution, budget validation, and one
  submission; report job ID and runtime estimate.
- Asked to check after more than five minutes: check once and report; never wait or sleep-monitor.
- Any unexpected HU-home placement, scientific-plan conflict, selected-artifact deletion, or
  credential problem: stop and ask the user.

## 12. Documentation And Evidence Map

Read in this order for current work:

1. `AGENTS.md` - mandatory operational and storage rules;
2. this document - current master state and execution order;
3. `PROJECT_HANDOFF_AND_COMPLETE_PROGRESS_OVERVIEW.md` for a collaborator-friendly full narrative;
4. `ssh-client/README.md` before any HU connection, shell launcher, or Slurm action;
5. Reports 101--109 - current prompt-remediation, cross-family, Qwen checkpoint evidence, and next plan;
6. `98_PRE_M2_FINAL_DECISION.md` - detailed Max-question synthesis and HOLD rationale;
7. Reports 94--97 - work-package results, jobs, paths, hashes, and audits;
8. Report 84 - HU storage incident and artifact lifecycle;
9. Reports 48 and 60 - historical acquisition ladder and canonical M1-to-M3 roadmap;
10. Reports 68, 75, 77, 85, 87, and 91 - Relation V2 release, scale results, 1.7B controls, and
   capability drift;
11. `documentation/Expose.pdf` - thesis motivation and original causal design.

Chronological reports must not be rewritten to hide failed runs or superseded decisions. New
plans and results continue at 101 and above, and every completed experimental family must update
this master document's status before the next phase opens.

## 13. One-Paragraph Current Handoff

The 100-subject/500-fact cross-family screen is complete. Document 106 reports that no candidate
passes every frozen gate. Qwen passes all factual and prompt-robustness gates (100% exact, 99.6%
global and 99% minimum per-relation robust intersection) but fails generic retention with PPL ratio
1.461. StableLM BF16 remediation reaches 100% exact and 93.8% global robustness but misses the
held-out/per-relation floors at 69% and also fails PPL ratio at 1.477. Gemma and Llama show severe
relation-specific held-out failures and large PPL drift. SmolLM2 remains the converse tradeoff:
acceptable PPL retention but inadequate held-out robustness. Therefore seed 43, paired-relation
confirmation, the 500-subject/2,500-fact scale control, any larger selected-scale M1, M2, and M3
remain HOLD. Documents 107--108 evaluated every retained Qwen checkpoint and found no factual-
robustness/PPL overlap: update 25 already has PPL ratio 1.409 while failing factual gates, and the
earliest factual-pass update 50 has ratio 1.455. Early stopping is ruled out. Document 109 removes
Gemma from the active path and freezes a staged decision: first implement and run a small Turkish
bridge pilot on existing Qwen update 50 and SmolLM artifacts; then run bounded Qwen retention
interventions only if Qwen shows a useful bridge; replicate a fully passing recipe; and proceed to
500 subjects / 2,500 facts before any larger scale. The final causal design retains Branch A/B and
adds matched clean, lexical-alignment, and true-fact adaptation runs. Phase 109A code and
eligibility implementation are complete. Corpus storage preflight passed, but the corpus is not
yet built because data-free launcher/metadata attempts exposed a missing-path guard bug, an
anonymous Wikimedia HTTP request, and a non-date-scoped checksum filename. All are corrected and
locally tested. Commit `d35e200` is on HU; preflight 410147 passed and corpus pipeline 410148 is now
running on `gruenau3` with an empty initial stderr and a growing scratch-only dump. The next action
is to correct and test the contamination inventory's Relation V2 schema/artifact binding. Job
410148 successfully completed download, SHA-1 verification, extraction, normalization, audit,
filtering, and deduplication: 505,100 input documents became 505,016 unique documents in an
approximately 11 GiB scratch tree. It then failed before scanning/splitting because the legacy V1
inventory requested `university_en` from the V2 profiles, which instead contain
`field_of_study_en`; the V2 release also uses versioned acquisition directories rather than legacy
`output/` files. The local correction is now implemented without changing the frozen corpus config:
relations and text sources are read from the release manifest, used artifacts are hash-verified,
V1 compatibility is tested, and arbitrary undeclared files are excluded. The real V2 release
builds 106,635 patterns over 5,000 subjects, 25,000 fact IDs, and 20,000 unique declared synthetic
sentences. A guarded resume launcher runs only contamination-preflight, scan, split, and report;
its paired preflight reserves 50 GiB incremental scratch and zero checkpoints. The available local
suite passes 169 tests with four optional skips. Commit, push, HU sync/test, and a fresh dependent
resume wave are next. Post-run audit 410149 passed with HU home approximately 7.91 GiB,
`/vol/tmp2` approximately 115 TiB free, 3% scratch inode use, and unchanged scratch paths. No
completed split/manifest hashes exist. Commit `007b4c8` is synchronized on HU; authoritative tests
and the real-release 106,635-pattern inventory smoke passed. Resume preflight 411177 is running
with empty initial stderr, while resume job 411178 is correctly pending on its `afterok`
dependency. Preflight 411177 passed and job 411178 entered `RUNNING`, but the scan exposed
per-subject duplication of shared canonical-object matches: at 1 hour 26 minutes the match stream
was approximately 72.3 GB for about 209,403 clean documents, versus an approximately 874 MB clean
stream. Scratch remains safe at approximately 115 TiB free and 3% inode use, but projected runtime
is approximately 3.5 hours against a 3-hour limit and projected raw matches are roughly 170 GB.
Job 411178 was cancelled at approximately 1 hour 30 minutes rather than allowing a predictable
timeout. Its incomplete scratch-only match/clean/removed/SQLite files (approximately 76 GB) were
deleted after exact verification; the completed deduplicated corpus and stage evidence remain, and
the corpus tree is again approximately 11 GB. No artifact was placed in HU home. The local fix now
aggregates identical object surfaces while preserving sorted associated subject-ID sets: object
patterns fall from 41,631 to 713 and total patterns from 106,635 to 65,717, while 5,000 subjects,
25,000 fact IDs, and 20,000 exact synthetic sentences remain unchanged. The full available local
suite passes 170 tests with four optional skips. Commit, push, HU sync/test, fresh preflight, and
one corrected resume job are next. Commit `c9a46fd` is now synchronized on HU; authoritative tests
and the exact 65,717-pattern/713-object count check passed. Fresh preflight 411179 is running with
empty initial stderr, and corrected resume 411180 is pending on its `afterok` dependency. All
high-volume outputs, logs, caches, and temporary files use the absolute `/vol/tmp2` experiment
namespace; home retains only permitted small source/config/metadata. Recheck after approximately
five minutes and do not submit a duplicate. Preflight 411179 has now passed with home approximately
7.91 GiB, `/vol/tmp2` approximately 115 TiB free and 3% inode use, and all paths on scratch.
Corrected resume 411180 is running on `gruenau3`; at 26 minutes stderr was empty, matches were only
approximately 3.2 GB versus 72 GB in the failed run, clean output was approximately 1.77 GB, and
the total corpus tree was approximately 15 GB. The aggregation fix worked. Job 411180 completed
with empty stderr: 505,016 inputs, 504,287 clean retained documents, 729 removed documents,
1,550,180 matches, and a 494,253/10,034 train/validation split. Candidate split hashes exist and
the complete scratch tree is approximately 17 GB. Do not yet call the corpus frozen: the manifest
embeds a stale reused pre-aggregation contamination-preflight state, and the precommitted
deterministic contamination sample review remains undone. Correct force-rerun semantics,
regenerate compact provenance and manifest hashes, review deterministic removed/flag-only/clean
samples, and complete post-run audit 411181 before bridge training. Audit 411181 passed with home
approximately 7.91 GiB, `/vol/tmp2` approximately 115 TiB free, 3% scratch inode use, all
high-volume paths on scratch, and empty stderr. The separate AGENTS.md home-file listing above
500 MB was not part of that launcher and remains required alongside the compact
provenance/sample-review closure. That missing home-file check is now running as Slurm audit
411183 with scratch-only logs; no corpus job is active. Audit 411183 passed with empty stderr and
found exactly three files above 500 MB, all pre-existing PyTorch/CUDA libraries in the active
`xfer-relearn` Conda environment dated 2026-06-30, not experiment artifacts. Together with the
unchanged approximately 7.91 GiB home usage and scratch-resolved paths, the post-run storage audit
is complete. Compact provenance correction and deterministic contamination sample review remain.
Seed 43 and scale-up remain HOLD.
The compact closure implementation is now locally complete: force-rerun semantics are corrected,
self-referential manifest entries are excluded, deterministic seed-42 samples of 20 removed, 20
flag-only, and 20 clean documents are generated from frozen scan hashes, and dedicated scratch-only
preflight/provenance Slurm launchers perform count assertions plus the full storage audit. The full
available local suite passes 174 tests with four optional skips. Nothing has been submitted from
this unpushed implementation yet. Next: commit/push, synchronize and test the exact HU commit,
then launch one `afterok` provenance wave (estimated 5--15 minutes), manually review its compact
sample, and freeze the corpus only if that review passes. Bridge training remains HOLD meanwhile.
Commit `2e3837c` is now synchronized on HU and the authoritative test command succeeded. Preflight
411188 is running on `gruenau` with zero-byte stderr; provenance/review job 411189 is correctly
pending on `afterok:411188`. Recheck in approximately five minutes and do not submit a duplicate.
Jobs 411188 and 411189 subsequently passed with empty stderr, corrected provenance, exact bucket
counts, candidate checksums, and a clean storage audit. Manual inspection confirmed correct bucket
logic but exposed a compact-reporting issue: four removed samples had more than 25 matches, so the
first-25 policy could hide the decisive removal context behind object-only flags. Corpus content
and splits are unaffected. The sampler is locally corrected to prioritize decisive removal
matches and record their count; after a narrow push, rerun only the compact provenance job and
repeat the manual review. Bridge training and final corpus status remain HOLD until that passes.
The decisive-first fix is pushed as `4b72215`, synchronized on HU, and passes the authoritative
targeted suite. Fresh preflight 411190 is running; corrected compact refresh 411191 is pending on
`afterok:411190`. No corpus/scan/split reconstruction occurs. Recheck after approximately five
minutes and do not submit a duplicate.
Jobs 411190/411191 passed with empty stderr and a clean storage audit. The decisive-first sample
hash is `5a1ced0b...7154a6b`; final manual review passed 20/20 removed, 20/20 flag-only, and 20/20
clean checks with no missing decisive evidence. Append-only finalization is locally implemented:
it preserves all candidate evidence and will create separate review-decision, final-manifest, and
final-checksum artifacts under scratch, refusing any overwrite. Tests pass. Next: commit/push,
HU sync/test, fresh preflight, and one bounded finalization job; bridge training remains HOLD until
that job verifies the hashes and storage audit.
Append-only finalization commits `ab2e9f3` and `8fe6bd5` are pushed and synchronized on HU; the
authoritative targeted suite passed. Dedicated preflight 411192 passed with home approximately
7.91 GiB, 115 TiB free and 3% inode use on `/vol/tmp2`, all paths on scratch, zero checkpoints,
and less than 1 MiB new output. Finalization job 411193 is running on `gruenau` with empty stderr.
Recheck in approximately five minutes; do not submit a duplicate.
Finalization job 411193 completed with empty stderr and all five checksum entries verified `OK`.
The Turkish Wikipedia bridge corpus is now frozen: 494,253 train documents and 10,034 validation
documents, with final manifest SHA-256
`108c72375bb253742831da3fafb9e4b4b7b736974cb3cf6ef13f9b0f167502f7`. Document 110 is the compact
result/freeze record. Phase 109A is not wholly complete: next freeze the localized answer/alias
contract, Qwen/SmolLM eligible and shared fact sets, and exact tokenizer-specific low/full dose
budgets plus output estimates. Do not start bridge training until those are validated.

The remaining Phase 109A contract work is now implemented locally as append-only `contracts/v2`
and frozen in Document 111. It supersedes the numerically useful but path-stale V1 contract,
normalizes both model/tokenizer manifests to scratch, freezes canonical-only localized answers and
relation distractors, reconstructs Qwen/SmolLM2 eligibility and shared intersections, and
materializes the same frozen raw-document dose with tokenizer-specific 32/128-step block audits.
The CLM trainer now honors a manifest tokenizer-source fallback required by the Qwen update-50
checkpoint. The full available suite passes 178 tests with four optional skips. Next: narrow
commit/push, exact HU sync/test, one contract-family preflight, and one dependent materialization
job. Bridge training remains HOLD until the V2 manifest and storage estimate are reviewed.

Contract-v2 commit `5ed176d` is pushed and synchronized on HU; the authoritative 44-test subset
passed. Preflight 411194 passed with HU home approximately 7.91 GiB, approximately 115 TiB free and
3% inode use on `/vol/tmp2`, zero checkpoints, and every relevant path on scratch. Dependent
materialization job 411195 is running on `gruenau3` with empty initial stderr. Recheck after
approximately 5--10 minutes and do not submit a duplicate. Training remains HOLD until its V2
manifest is reviewed.

Contract materialization 411195 completed with its terminal ready marker and all gates passed.
Document 112 freezes manifest hash `f3248f07...39e5e`, Qwen/SmolLM2 eligibility 497/359, shared
eligibility 357, shared strict 196, a common 1,000-document source pool, 6,215/8,392 model-specific
blocks, nonzero validation blocks, and a 110.72 GB training-family reserve. Post-run home remains
approximately 8.0 GiB and all new artifacts are on scratch. Stderr contained one recorded benign
long-document tokenizer warning, not a traceback or training failure. Phase 109A is complete. Next
implement/test one dedicated two-model GPU launcher and run a fresh combined training preflight;
only if it passes may Qwen and SmolLM2 bridge training start in parallel. M2/M3 and scale-up remain
HOLD.

Seed-43 preflight 411323, training 411324, and audit 411325 completed. Training reached 252/252
updates in 2:00:27 with exit 0:0, all 11 checkpoints, a 98-GiB scratch tree, and no error signature.
Home remained approximately 7.91 GiB and no large home artifact appeared. Commit
`da0ca665ec20a583bff82ba29f95a1d863620bb4` freezes the all-checkpoint replication evaluation
and passed 63 relevant tests locally and on HU. Evaluation chain 411329 -> 411330 ->
411331_[0-10%3] -> 411332 plus audit 411333 was submitted once. Preparation 411329 entered RUNNING
on `gruenau` with empty initial stderr and every downstream dependency was verified. Do not
duplicate. The 500-subject gate remains HOLD until the seed-43 summary passes.

The seed-43 evaluation wave, summary 411332, and audit 411333 are now complete. Document 120 records
the frozen decision `seed43_replication_failed`. No checkpoint passes all corrected gates. Step 50
has PPL ratio 1.1869 and passes exact, A/B, robust, and integrity gates, but minimum C/D is 72% due
to profession/Form-C at 72% direct and 78% QA. Step 75 reaches minimum C/D 81% and passes the
factual/robustness gates, but PPL ratio has risen to 2.755. All 11 checkpoints have zero lexical-
empty output and zero synthetic intrusion; there are no evaluation error signatures. Audit passed
with home approximately 7.91 GiB and the entire seed-43 family approximately 98 GiB on scratch.
Under the frozen contract, no third seed, coefficient sweep, 500-subject run, M2, or M3 opens
automatically. The next action requires an explicit new scientific decision.

Document 113 now freezes the Phase 109B two-model training launch. The local implementation uses
one combined storage/hash preflight, a parallel Qwen/SmolLM2 A100 array, per-task orphan GPU-process
rejection before model load, and one family post-run audit. Every high-volume path is under the
Turkish-bridge `/vol/tmp2` namespace; the required family reserve is 110,721,074,308 bytes. Local
shell/whitespace checks and the full available suite pass (179 tests, four optional skips). Next:
commit/push, exact HU sync/test, submit the dependent wave once, and verify startup. Evaluation is
a separate later wave; M2/M3 and scale-up remain HOLD.

Parallel-training commit `a1a0286` is pushed and synchronized exactly on HU; the authoritative
45-test subset passed, output roots were absent, and the queue was empty. The single wave is now
submitted: preflight 411196 is running on `gruenau` with empty stderr, training array
411197_[0-1%2] is pending on its `afterok` dependency, and post-run audit 411198 is pending on
`afterany` of the array. The preflight was still in the quiet bounded home-usage measurement at the
40-second check; do not submit a duplicate. Recheck in approximately 3--5 minutes and inspect both
GPU-process guards when training begins.

Preflight 411196 passed, but both 411197 array tasks safely aborted before model load on
`gruenau9`: their distinct allocated A100s each contained another user's 31,490 MiB Python compute
process despite Slurm reporting the node idle. No output root, checkpoint, or training result was
created. Post-audit 411198 passed with empty stderr, home approximately 8.0 GiB, `/vol/tmp2`
approximately 115 TiB free and 3% inode use. A single fresh retry is permitted because this is a
verified node-local infrastructure condition. The launcher now supports a validated recorded node
exclusion; retry will exclude `gruenau9`, retain the A100 request and all frozen scientific
settings, rerun the complete preflight, and still abort if the new GPU guard sees any process.

Retry-support commit `b596c48` is pushed and synchronized exactly on HU; tests passed and both
output roots remained absent. Fresh preflight 411200 is running with empty stderr. Retry array
411201_[0-1%2] is dependency-gated and Slurm records `ExcNodeList=gruenau9`; post-audit 411202 is
pending on the complete array. Recheck in approximately 3--5 minutes and verify both tasks report
`gruenau10` plus `gpu_preflight=clean`. Do not submit a third wave.

Fresh preflight 411200 passed. Retry task 411201_1 (SmolLM2) obtained a clean `gruenau10` A100 and
is running with empty stderr; at approximately five minutes it had produced checkpoints 32 and 64
in a roughly 20 GiB scratch tree. Retry task 411201_0 (Qwen) safely aborted before model load
because its separate A100 contained a foreign VLLM process using 74,166 MiB plus an 87 MiB Firefox
process; no Qwen output root exists. Audit 411202 remains pending until SmolLM2 completes. Do not
interrupt SmolLM2 or submit another Qwen job now. Recheck in approximately 5--10 minutes, close the
family audit, then consider a separate Qwen-only retry on a verified clean allocation.

SmolLM2 task 411201_1 completed successfully in approximately 7m59s wall time (Trainer runtime
350.095s), with train loss 2.237035, final validation loss 2.242527, checkpoints 32/64/96/128, a
final model, and a 42 GiB scratch tree. Its 86,555-byte stderr contains only normal tqdm/model-write
progress, with no traceback, OOM, NaN, or failed assertion. Post-audit 411202 passed with empty
stderr; home remains approximately 8.0 GiB and `/vol/tmp2` approximately 115 TiB free at 3% inode
use. Qwen remains an infrastructure-blocked non-run with no output root. Preserve every SmolLM2
checkpoint pending evaluation. Next prepare a separate fresh Qwen-only preflight/launcher; do not
reuse the two-model preflight because SmolLM2 now has a valid canonical output root.

Document 114 freezes a Qwen-only clean-GPU infrastructure recovery. It preserves the complete
SmolLM2 tree and all scientific settings, validates a Qwen-only 52,527,160,826-byte reserve, then
temporarily allocates two `gruenau10` A100s and exposes exactly one process-free GPU UUID to the
single-GPU Qwen trainer. If neither allocated GPU is clean, it stops before output creation. Local
shell/whitespace checks and the full available suite pass (180 tests, four optional skips). Next:
narrow commit/push, exact HU sync/test, one fresh Qwen preflight/recovery/audit wave, and immediate
GPU-selection verification.

Qwen recovery commit `4d709a9` is pushed and synchronized exactly on HU; tests passed. Fresh
Qwen-only preflight 411204 passed with home approximately 7.91 GiB, approximately 115 TiB free and
3% inode use on `/vol/tmp2`, Qwen root absent, SmolLM2 complete, and a 52.53 GB reserve. Recovery
411205 is running on `gruenau10`: of two allocated A100s, the launcher rejected the known 74.3 GiB
foreign-VLLM device and selected the clean 17 MiB-baseline UUID as Qwen's sole visible training GPU.
It printed `gpu_preflight=clean`, stderr was initially empty, and the initial manifest exists.
Post-audit 411206 is dependency-gated. Recheck after approximately 8--10 minutes and do not submit
a duplicate.

Qwen recovery 411205 completed successfully in approximately 6m33s wall time (Trainer runtime
320.963s), with train loss 2.467925, final validation loss 2.592992, checkpoints 32/64/96/128, a
final model, and a 38 GiB scratch tree. Its 66,212-byte stderr contains only ordinary progress and
model-write output, with no traceback, OOM, NaN, or failed assertion. Post-audit 411206 passed with
empty stderr; home remains approximately 8.0 GiB and `/vol/tmp2` approximately 115 TiB free at 3%
inode use. SmolLM2 remains complete at approximately 42 GiB. Both models are now ready for the
separately frozen M0/M1/low/full bilingual bridge and English/Turkish PPL evaluation wave. Preserve
all four scientific endpoints until that wave selects and hashes the retained artifacts. M2/M3
and scale-up remain HOLD.

Document 115 freezes the post-training bridge evaluation before result inspection. Both Qwen and
SmolLM2 will be scored at M0, frozen M1, update-32, and update-128 on all 1,500 EN->EN/TR->EN/TR->TR
candidate probes plus the same frozen English WikiText-2 and Turkish validation PPL corpora. The
primary classifier uses each model's pre-frozen eligible facts; all-fact, model-strict, shared-
eligible, and shared-strict results are mandatory sensitivities. Implementation commit `e032fb2`
is pushed and synchronized exactly on HU. Wave 411248 -> 411249_[0-1%2] -> 411250 was submitted
once. Preflight 411248 is running with empty initial stderr; both RTX-3090 model tasks and the common
post-audit remain dependency-gated. No result exists yet and M2/M3/scale-up remain HOLD.

Preflight 411248 subsequently passed: home 8,298,040 KiB, approximately 115 TiB free and 3% inode
use on `/vol/tmp2`, all paths on approved scratch, zero new checkpoints, and frozen evaluation-
manifest SHA-256 `785eff7d...626f12`. Tasks 411249_0 (Qwen) and 411249_1 (SmolLM2) are running on
distinct clean RTX 3090 devices on `guppi8`, both with zero-byte stderr. At 4m36s they had completed
respectively 700/1,500 and 550/1,500 M0 bridge probes. Audit 411250 remains dependency-gated. Leave
the jobs running and recheck in approximately 10--15 minutes; no duplicate is authorized.

At 16m21s, both M0 bridge/PPL evaluations were complete and SmolLM2 had also completed its 1,500-
probe M1 bridge suite. SmolLM2 continues normally. Qwen task 411249_0 stopped on its first M1
candidate group with `No answer tokens detected for the prompt/candidate boundary`. This is a
manifest-construction bug: Qwen M0 correctly used the pinned base tokenizer, while Qwen M1/low/full
manifests replaced Contract V2's explicit base-tokenizer fallback with the tokenizer-incomplete
checkpoint directory. Qwen M0 evidence remains valid; Qwen M1/low/full are unavailable, not failed
scientific outcomes. Preserve V1 unchanged, let SmolLM2 and audit 411250 finish, then prepare an
append-only Qwen-only tokenizer-corrected recovery that reuses hashed M0 and evaluates only the
three missing states. M2/M3/scale-up remain HOLD.

SmolLM2 task 411249_1 and audit 411250 are now complete. On 359 frozen model-eligible facts,
English top-1 remained 96.66% M1 -> 96.10% full and English PPL improved from ratio 1.080 at M1 to
1.033 at full. Turkish PPL improved 10.778 -> 9.426 (ratio approximately 0.875), proving that the
adaptation dose had a real language-model effect. However TR->EN top-1 moved 20.61% M1 -> 20.06%
low -> 16.99% full; low paired change was +0.0010 with CI crossing zero, and full change was
-0.0335 with CI [-0.0703, +0.0008]. Absolute access, positive margin, M0-adjusted access, relation
breadth, and adaptation-gain/preserved-open gates failed. SmolLM2 is therefore
`not_viable_under_frozen_pilot` on the primary set and all four sensitivity sets. Audit: home 8.0
GiB, approximately 115 TiB free and 3% inode use on `/vol/tmp2`, 4.2 MiB evaluation tree, empty
audit stderr. Next: tokenizer-corrected append-only Qwen M1/low/full recovery; M0 is reused.

Document 116 freezes that append-only Qwen recovery. Valid V1 M0 bridge/PPL files are individually
hashed and reused read-only; the local-manifest helper now preserves Contract V2's explicit base-
tokenizer fallback, and the new CPU preflight exhaustively repeats answer-token boundary detection
for every frozen prompt/candidate pair before any model load. Commit `fbdedff` is pushed and exact
on HU; targeted HU tests pass. Wave 411256 -> 411257 -> 411258 was submitted once. Preflight 411256
is running on `gruenau3` with home 8,298,172 KiB, approximately 115 TiB free and 3% inode use on
`/vol/tmp2`, a 5 GiB reserve, and empty initial stderr. Evaluation/audit remain dependency-gated;
do not duplicate. M2/M3/scale-up remain HOLD.

Qwen recovery is complete. Preflight 411256 passed all frozen hashes and 168,000 exhaustive
prompt/candidate tokenizer-boundary checks. Job 411257 completed M1/low/full in approximately 22
minutes with all bridge suites at 1,500/1,500 and no traceback/OOM; audit 411258 passed. Home is
8.0 GiB, `/vol/tmp2` has approximately 115 TiB free at 3% inode use, and the recovery tree is 2.5
MiB. On 497 eligible facts, Qwen retained 100% EN->EN at every acquired/adapted state and Turkish
PPL improved 22.007 M1 -> 13.378 full; English PPL ratio improved 1.455 M1 -> 1.114 full. However
TR->EN fell from an already-open 66.20% at M1 to 52.31% low and 46.48% full. Paired changes were
-0.1400 (CI [-0.1765, -0.1060]) and -0.1985 (CI [-0.2410, -0.1570]); full margin became negative.
The adaptation-gain/preserved-open gate failed, so Qwen is `not_viable_under_frozen_pilot` on the
primary and every sensitivity population. Combined decision: neither Qwen nor SmolLM2 passes the
frozen bridge promotion rule. Do not automatically open retention intervention, scale-up, M2, or
M3. The bridge recipe is a valid negative feasibility result pending an explicit new scientific
decision.

### 23 July 2026 - Document 117 explicitly opens bounded M1 retention remediation

The user has made the explicit scientific decision that a passing 500-subject/2,500-fact M1 is a
mandatory gate before later causal adaptation. Document 117 therefore supersedes only Document
109's condition that Qwen retention remediation required a positive bridge classification. The
negative Documents 115--116 bridge result remains unchanged. The new order is: matched seed-42
Qwen factual control versus one precommitted clean-English replay condition; unchanged factual and
PPL gates; seed-43 replication of a fully passing treatment; then the mandatory 500-subject scale
control. M2, M3, 1,000 subjects, and 5,000 subjects remain HOLD. No new HU job is authorized until
Document 117 implementation, tests, exact-commit synchronization, and storage/path preflight pass.

Document 117 implementation commits `e5d8685` and `ff4170d` are now pushed and exact on HU. Local
and HU targeted training tests pass (38 each). Coordinated wave 411273 -> 411274 -> 411275_[0-1%2]
-> 411276 was submitted once: family preflight, frozen WikiText-2 train/validation anchor
materialization, parallel matched Qwen control/replay seed-42 training, and post-run audit. The
preflight initially entered RUNNING on `gruenau` with dependent jobs correctly held. All large
destinations are under `/vol/tmp2/yesildau/m1_retention_v1`; the recorded family reserve is 500
GiB. Do not duplicate. Seed 43, 500-subject scale-up, M2, and M3 remain HOLD pending the frozen
seed-42 evaluation gates.

Wave 411273 failed safely in preflight before any training because the checker incorrectly required
Qwen's optional `tokenizer_source_path_absolute` manifest field. Its unreachable dependent jobs
411274--411276 were cancelled. Commit `87a9ed8` now uses the training core's frozen fallback to the
model directory and is pushed/exact on HU. Corrected wave 411277 -> 411278 -> 411279_[0-1%2] ->
411280 was submitted once; preflight entered RUNNING on `gruenau` with empty initial stderr and all
other tasks dependency-held. Do not duplicate. All scientific gates and storage destinations are
unchanged.

Corrected preflight 411277 and anchor 411278 passed. Frozen anchors contain 3,500 train/500
validation rows, zero synthetic-subject surface occurrences, and hashed outputs under scratch.
Both seed-42 tasks 411279_0/1 are RUNNING on distinct A100-80GB devices on `gruenau9`; stderr is
empty and control has produced checkpoint-25. Unrelated `TextJEPA` processes were already resident
on both allocated GPUs, but current combined use leaves approximately 21--25 GiB headroom and no
OOM has occurred. Leave the demonstrated-progress jobs running; compute contention may extend
replay to approximately 90--140 minutes. Audit 411280 remains dependency-held. Do not duplicate.

At 44m28s, control reached checkpoint-150/252 and replay checkpoint-75/252 with zero-byte stderr.
Measured intervals are approximately 6.6 and 12.6 minutes per 25 updates. Expected remaining time
is 30--35 minutes for control and 90--100 minutes for replay; replay should fit the 2h30 limit by an
estimated 10--15 minute margin. Continue the existing jobs and recheck in approximately 25--30
minutes; do not duplicate while checkpoint progress remains stable.

Seed-42 retention training is complete: control 411279_0 and replay 411279_1 both reached 252/252
with 11 checkpoints plus final model, complete manifests, and no traceback/OOM/runtime-error/NaN/
Inf signature. Runtimes were 67.7 and 125.6 minutes. Each run tree is approximately 98 GiB and each
final model weight is 3,087,467,144 bytes. Replay recorded mean factual/anchor losses 0.2773/0.7600
at coefficient 0.5. Do not interpret aggregate Trainer loss as the gate. Audit 411280 verified home
at approximately 7.91 GiB, no new >500 MiB home file, `/vol/tmp2` at approximately 115 TiB free and
3% inode use, then failed only at the cluster-broken `sacct` call. Next: accounting-tolerant compact
recovery audit and frozen evaluation of every retained checkpoint. Seed 43, 500 subjects, M2, and
M3 remain HOLD.

Document 117 now freezes the 22-task checkpoint evaluation before outcome inspection: 11 control
and 11 replay checkpoints, throttle three, `gruenau9,gruenau10` excluded, 50 GiB compact-output
reserve, unchanged exact/held-out/robust/PPL/integrity gates, and earliest-all-gates-pass selection
within condition. Seed 43 opens only for a fully passing replay checkpoint. Implementation and HU
preflight must pass before submission; 500 subjects, M2, and M3 remain HOLD.

The first evaluation submission stopped before any evaluation task because excluding both
`gruenau9,gruenau10` excludes the full A100 inventory. Recovery audit 411287 and preparation 411288
were retained; pending preflight 411289 was cancelled. Read-only inspection found all gruenau10
A100s occupied by untracked VLLM/TextJEPA memory (approximately 74.2/42.3/38.1 GiB). Before any
outcome exists, the operational contract is amended to the previously validated RTX3090 BF16 pool,
excluding allocated guppi6/7; scientific evaluation inputs, batching, gates, and selection remain
unchanged. Resume from the prepared wave after code/test/HU synchronization.

Recovery audit 411287 passed with the accounting-tolerant fallback and unchanged safe storage.
Preparation 411288 remained active at 4m33s while hashing 22 checkpoint manifests, with empty
stdout/stderr; leave it running under the five-minute monitoring rule. Commit `13bafe6` switches
only evaluation hardware to the available RTX3090 pool, excludes guppi6/7, adds prepared-wave
resume, and passes local tests. Pull it on HU after 411288 completes, then submit fresh preflight +
22-task evaluation + summary + audit. No evaluation result exists and no duplicate is authorized.

Preparation 411288 completed and froze all 22 tasks with registry SHA-256
`66d8864cac30b6422148ebbe956849f2040c538f4d6556d146687ae6416a0e54`; no result namespace existed.
Commit `13bafe6` is now exact on HU and targeted tests pass. RTX3090 `--test-only` selected clean
node guppi5. Wave 411297 -> 411298_[0-21%3] -> 411299 plus audit 411300 was submitted once;
preflight entered RUNNING with empty stderr and all other jobs dependency-held. Expected wall time
after GPU start is approximately 2--4 hours. Do not duplicate; seed 43 and 500 subjects remain
HOLD pending the frozen summary.

Evaluation preflight 411297 passed: home approximately 7.91 GiB, `/vol/tmp2` approximately 114.3
TiB free, task count 22, throttle three, RTX3090 routing. Tasks 411298_0/_1 started on guppi5 and
_2 on guppi8 with zero-byte initial stderr; remaining tasks are throttle-held. Summary 411299 and
audit 411300 remain dependency-held. Leave running and do not duplicate.

### 24 July 2026 - Seed-42 retention evaluation result

The complete 22-checkpoint evaluation, summary 411299, and audit 411300 have finished. The literal
frozen decision is `retention_remediation_failed`. Control reaches the factual gates at step 50 but
has PPL ratio 1.455. Replay step 50 is the unique joint Pareto point: 99.8% exact, 99% minimum exact
relation, 100% minimum A/B, 91% minimum C/D, 98% robust global, 91% robust minimum relation, and
PPL ratio 1.24684. Its sole failed gate is a length-only integrity heuristic: the correct one-word
answer `navigation` plus EOS is mechanically marked near-empty because it contains at most two
token IDs. Synthetic intrusion is zero and generic-completion top-1 is 96.67%.

Document 118 is now the authority for this outcome. It preserves the original automatic failure
and opens only a narrow evaluator correction plus deterministic re-summary. Formal promotion and
seed-43 remain HOLD until that correction is frozen; 500 subjects remain HOLD until seed-43 passes;
M2/M3 remain HOLD. Post-run storage is safe: HU home approximately 7.91 GiB, `/vol/tmp2`
approximately 115 TiB free at 3% inode use, and no new large home artifact.

### 24 July 2026 - Adjudication complete; seed-43 replication opened

Commit `7e90018` passed 22 targeted tests locally and on HU and produced a separate adjudicated
artifact without overwriting the original frozen summary. Original SHA-256 is
`78a2f440faede734e7480c6ab3c32b0b60f181d90895d136c6e4b413429e0487`; adjudicated SHA-256 is
`e7d52bfc0bfa9c0adda02f641ea6b0d8bc0620d33ecdf4599c8fa778270899a6`. The original decision
remains failure; the corrected decision is `replicate_replay_seed43`. Control has no corrected
passing checkpoint and replay step 50 is the sole pass. Document 119 freezes the seed-43 contract:
same population, rows, anchors, coefficient, budget, checkpoints, and thresholds; only model/data
seeds and run identity change to 43. The dedicated root is
`/vol/tmp2/yesildau/m1_retention_seed43_v1`. Seed-43 implementation, tests, exact-commit sync, and
mandatory family preflight precede one training submission. The 500-subject gate and M2/M3 remain
HOLD.

Commit `b60eed18c78c274d6849e2bc98ee35bd86a0126e` implements the frozen seed-43
replication and passed 62 relevant tests locally and on HU. The family was submitted once as
preflight 411323 -> training 411324 -> audit 411325. Preflight entered RUNNING on `gruenau` with
empty initial stdout/stderr; training and audit were correctly dependency-held. The first direct
launcher invocation had stopped at a local executable-bit permission error before creating any
job and is not a duplicate run. All destinations are under
`/vol/tmp2/yesildau/m1_retention_seed43_v1`; do not duplicate the active chain.

### 3 August 2026 — Post-M2/M3 completion correction and current authority

This append-only correction supersedes the stale pre-M2 HOLD language above for the completed
2,500-fact Qwen M2/M3 family; it does not rewrite or invalidate historical decisions that were
correct when recorded. The family described by Documents 133--136 has now completed:

- all pre-M2/M3 readiness packages, including the bilingual/PPL baseline, frozen four-cycle
  contract, matched M2-clean/M3-fact materialization, smoke/resume checks, and storage/device
  preflight;
- all four principal endpoint training runs at fixed `checkpoint-128`;
- all 96/96 endpoint evaluation slices, including the controlled retry of only the 13 missing
  M3 seed-43 slices;
- strict assembly, 2,000 subject-bootstrap analysis, and frozen gate application.

The final operational validity gate and EN-to-EN retention guardrail passed. The primary
Branch-B-specific TR-to-EN interaction passed for seed 43 but failed for seed 42 because its 95%
bootstrap interval crossed zero. The frozen overall decision is
`primary_success_criterion_not_met`. This is a valid negative/inconclusive scientific outcome,
not an infrastructure failure. No pre-M2/M3 task remains.

For the current post-M2/M3 state, use Document 136 for the operational/result ledger, Document
138 for the scientific milestone interpretation, and Document 139 for the only currently
authorized work: independent read-only review, clearly labeled exploratory analysis, documentation
alignment, and artifact-lifecycle closure after review. Do not automatically launch a new training
family, third seed, M3-lexical arm, factual-dose change, checkpoint search, gate relaxation, or
25,000-fact run.

### 3 August 2026 — Exploratory follow-through completed

The authorized post-M2/M3 exploratory analysis was completed from the frozen aggregate outputs
without new training or evaluation. The reproducible scratch output is
`/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/exploratory_20260803T063406Z`, generated at
repository commit `f021dc69b5331c115c9f129dfcd3af27463035de`. Document 142 records the
descriptive seed, relation, direction, form, scaffold, branch, decline, and recovery findings.
The analysis confirms a broad Turkish-involving M2 decline and only modest descriptive M3
recovery; it does not alter the frozen primary decision or authorize a new experiment. The
independent external review and post-review endpoint artifact freeze remain pending.

### 3 August 2026 — Independent review and model-only retention closure

Document 140a completed the independent read-only evidence review with verdict
`PASS WITH CONCERNS`. It found no blocker or major issue and reproduced the frozen
`primary_success_criterion_not_met` decision. Its two minor concerns were the pre-execution
`frozen_ready_to_submit` label retained in the immutable evaluation input manifest and the HU
home `du` audit timeout.

Following that non-blocking review, Document 143 records the model-only retention freeze of all
four `checkpoint-128` endpoints under
`/vol/tmp2/yesildau/qwen_m2_m3_v1/retained_model_only_20260803T073244Z`. The manifest SHA-256 is
`195aae05d65a580da2d98d8beb192244ac3a2a7046107ba1740208988f1082fa`; all 24 retained files
passed source/retained SHA-256 verification. Optimizer, scheduler, RNG, trainer, and training
argument state were excluded, original run trees were preserved, and no cleanup occurred. The
post-freeze scratch/inode/path audit passed; the home `du` timeout remains explicitly recorded.
The completed evidence package is now ready for the next independent inspection. No new training
or evaluation is authorized by this closure.

### 6 August 2026 — Supervisor feedback and literature-first realignment

Documents 144 and 145 record the scientific realignment following the latest supervisor meeting.
This correction does not invalidate the completed Qwen result or rename immutable artifacts. The
historical `M2-clean` and `M3-fact` runs were already sibling arms from the same M1, not sequential
M2-to-M3 training; conceptually they correspond to M2-A-like general Turkish adaptation and
M2-B-like factual re-exposure. Their frozen `primary_success_criterion_not_met` conclusion remains
unchanged and should be described as the Qwen Wikipedia-only, approximately 1M-token pilot.

The next thesis experiment must not be opened by further score-driven recipe search. It first
requires: (1) a documented base-model provenance screen emphasizing English-only or Turkish-unseen
training evidence; (2) a bounded M1 usability screen, with Qwen retained as a multilingual positive
control; (3) an audited, broader Turkish corpus informed by CulturaX, `vngrs-web-corpus`, Kumru,
MODA, and cross-language adaptation literature; and (4) a frozen manipulation-check package that
shows genuine Turkish-language improvement using held-out Turkish PPL plus a base-compatible
capability measure while protecting English/M1 retention.

Only after those audits pass may a separate execution contract open parallel, equal-budget
M2-A/M2-B siblings from the same frozen M1. M2-A contains the general Turkish corpus without target
facts; M2-B replaces matched neutral Turkish tokens with precommitted Turkish target-fact rows. The
primary factual comparison is M2-B minus M2-A, with TR-to-EN as the main access direction. No new
training, 25,000-fact scale-up, or corpus download is authorized by this planning correction alone.

### 7 August 2026 — LUNA-Worker 2 research/audit handoff

Document 146 expands the 6 August realignment into a detailed WP0--WP5 handoff for a dedicated
research worker named `LUNA-Worker 2 — Model, Corpus & Literature Audit`. It provides the exact
historical reading chain and reserves Documents 147--151 for model provenance/M1 shortlist,
cross-lingual adaptation literature, Turkish corpus audit planning, Turkish capability
manipulation-check design, and a combined decision gate.

This handoff does not broaden authorization. The worker may browse primary sources, inspect local
evidence, and create append-only documentation. It may not connect to HU, submit Slurm work, train
or evaluate models, download large model/corpus artifacts, materialize a new corpus, mutate frozen
artifacts, or reactivate the 25,000-fact plan. Any execution contract after Document 151 requires a
new explicit user decision.

### 9 August 2026 — Literature/roadmap alignment and bounded route status

Document 151aw aligns the restored comprehensive literature map, the historical Document 60
roadmap, the current Document 145 scientific route and the bounded vngrs operational chain. This
append-only correction does not modify the completed Qwen pilot or any frozen 151-series result.

The model names now have explicit, non-equivalent roles: OLMo-2-0425-1B, Pythia-1.4B and
Falcon-RW-1B remain English-centric screening candidates; none is selected. Qwen2.5-1.5B remains
the completed multilingual positive control. Claims about zero Turkish exposure must be bounded
to what each exact model source actually documents.

The Turkish corpus names likewise have different evidence states. `vngrs-web-corpus` is only a
conditional primary materialization candidate; `trwiki-20260601` is the frozen cross-domain
control; CulturaX is `excluded_access_blocked`; Turkish OSCAR/mC4, HPLT, FineWeb2 and Bella Turca
remain literature/provenance candidates pending exact identity, license, access, quality,
contamination and overlap evidence. Their presence in the roadmap is not corpus selection.

Document 151at freezes the local zero-or-one-hop Hugging Face CDN redirect correction after the
first preservation-checked vngrs route request returned HTTP 302. Its SHA-256 is
`d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa`; the verified local
implementation is commit `de4a14e3370326173bdf04ce33356aae7826ddda`, which has not been pushed
or executed on HU. Any future bounded route wave must separately authorize ordinary non-force
publication, preservation-checked HU fast-forward, mandatory preflight and exactly one corrected
execution. A route PASS would close only the vngrs metadata/footer feasibility component.

The active scientific sequence is literature/provenance reconciliation, measurement freeze,
bounded M1 usability screening, corpus selection plus facts-free Turkish dose manipulation, and
only then equal-budget sibling M2-A/M2-B training from the same frozen M1. Transfer remains
`TR-to-EN(M2-A) - TR-to-EN(M1)` and factual re-exposure remains
`TR-to-EN(M2-B) - TR-to-EN(M2-A)`. The global gate is still
`blocked_by_measurement_design`, with `blocked_by_corpus_selection_or_materialization`
contributing; `ready_to_measure=false` and `ready_to_train=false`.

### 11 August 2026 — Completed three-model 500-fact M1 screen

The bounded English-centric 500-fact screen has now produced complete training and base/endpoint
evaluation results for OLMo-2-0425-1B, Falcon-RW-1B and Pythia-1.4B. Documents 153--155 preserve
the launch history and operational corrections; Documents 156--156c preserve the Pythia official
tokenizer, PAD-default, GPU relocation and BF16 compatibility contracts; Documents 157/158 are the
current Pythia result and combined three-model gate authorities.

All three endpoints reached 100% exact-prefix acquisition and approximately 97--98% aggregate
hard-suite accuracy. None passed the full frozen gate. Their worst robust cells were all in
`profession` held-out form-C: OLMo 59%, Falcon 37% and Pythia 65%, below the 70% robust minimum.
Generic WikiText-2 PPL ratios were OLMo 1.510x, Falcon 10.952x and Pythia 16.149x, all above the
1.25x retention limit. These are three valid scientific negative results, not infrastructure
failures and not evidence that the models cannot store facts.

The immediate inference is that the frozen `5e-5 / 36 epoch / 252 update` recipe is sufficiently
strong for exact factual storage but too aggressive for the joint robustness/retention objective.
There is no automatic primary English-centric model selection. Any LR/dose/checkpoint remediation
must be a separately pre-registered exploratory/remediation family and must preserve the current
negative results. The user-requested next major work item is the separate vngrs Turkish corpus
quality/materialization route; the completed M1 screen does not automatically authorize a Turkish
dose ladder or M2-A/M2-B training.

### 12 August 2026 — vngrs bounded metadata/footer retry result

The exact Document 151be HU-only connectivity/prewarm/single-retry wave was executed once.
Connectivity, live worktree preservation, exact-byte home usage (`14,691,028,992` bytes), the
large-file cache manifest, scratch-path checks, internal storage preflight, independent PyArrow
writer/parser validation and all 96 selected-shard metadata/footer requests passed. The final
immutable README/license request returned HTTP 307 rather than the frozen 151at vocabulary's
validated 302 hop. The executor stopped fail-closed at logical attempt 97 / HTTP hop 193, wrote no
accepted artifact root and consumed the single invocation. Post-run storage and source-state
reconciliation passed. Documents 151bf/151bg record the result/gate with SHA-256 values
`e9a086f3be624ded0ac1271326ff57beefbd01b4a98dc936cb3ff6c135e1c9c5` and
`80ed93e937f9fc1eda74f9ae90df76823d957688e803f92bfd9df4c17aa86d75`.

This is a narrow redirect-semantics blocker, not evidence that the selected shard routes are
unavailable and not a corpus-quality PASS. vngrs remains a conditional materialization candidate;
the global gate remains `blocked_by_measurement_design`, with
`blocked_by_corpus_selection_or_materialization` contributing. Any retry requires a new frozen
license/README HTTP-307 contract and exact authorization.

The next local-only correction is frozen as Document 151bh, SHA-256
`57d8dbd0b84f5914e9b249b12d888cb1aa7c2ea6b6733197aaf117dbcb801853`. It permits only the exact
immutable README/license route to follow one same-origin HTTP 307 into the identity-preserving
Hugging Face `api/resolve-cache` path. Shard 302 behavior, zero-row policy and all bounded executor
limits remain unchanged. The implementation and tests are prepared locally; publication, HU/SSH
and the single new executor invocation still require exact SHA-bound authorization. The shared
unpushed implementation commit is `37a7d29a182f049054483915f4ceee5bc7fdd1d4`; the compatible
local suite passed 380/380.

### 12 August 2026 — OLMo BF16 dose/Pareto result and incomplete family gate

The exact Document 159b OLMo BF16 repair wave completed its compatibility preflight, optimizer
smoke, 252-update training and all six precommitted cheap checkpoint gates. Every OLMo checkpoint
reached 100% exact acquisition, but its WikiText-2 PPL ratios were 1.385--1.429 against the frozen
1.25 maximum. No hard suite opened and no OLMo checkpoint is eligible. This is a valid scientific
negative result, not an infrastructure failure. Document 160 records the execution and family
status (SHA-256 `9e995bc9cdff6ffa1da0e17194e050b590c2f7cbf8e2af0345672e6a425044de`).

The full three-model dose/Pareto family is not yet complete. Pythia has 6/6 cheap gates, while
Falcon has only 3/6: checkpoints 126, 210 and 252 stopped before scientific evaluation at the
free-VRAM guard. There are 15/18 required rows, so the frozen summary was not generated and no
primary model was selected. Document 161 is the current gate (SHA-256
`eea7227ef433506755da53699af9adf30e36aa574caec22fce48f9db30224579`). A separately frozen,
exactly authorized Falcon-only recovery would be required; seed-43, Turkish dose training,
M2-A/M2-B, deletion and cleanup remain closed.

The minimal family-completion correction is frozen as Document 162, SHA-256
`4ada146f01c777a2995d6bc4901e1cbaf9bae574b9d93263440fdfe9cca355fd`. It permits only Falcon
checkpoint `126/210/252` evaluation tasks (`2,4,5`) on a sequential guppi5 RTX3090 route with the
existing 20 GiB free-VRAM guard. The 18/18-row summary is dependency-closed behind successful
completion of all three tasks. Training, completed evaluations, thresholds, seeds and model
promotion remain unchanged and closed. Local implementation/tests are ready; HU/Slurm execution
requires separate exact SHA-bound authorization. The implementation is in the same unpushed
commit `37a7d29a182f049054483915f4ceee5bc7fdd1d4` and passed the 380/380 compatible suite.

### 12 August 2026 — Authorized vngrs HTTP-307 retry result

The exact Document 151bh wave was executed once. Commit
`37a7d29a182f049054483915f4ceee5bc7fdd1d4` was ordinary non-force pushed and
preservation-checked fast-forwarded on HU. Connectivity, exact-byte home/cache prewarm, storage,
no-home-write and PyArrow self-check gates passed. The HTTP-307 repair progressed beyond the prior
README/license source-request blocker, but the completed-package validator rejected unreconciled
trailer/footer `Content-Range` evidence. No accepted seven-output package was written and
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1` remains absent. The invocation is
consumed and automatic retry is closed. Documents 151bi/151bj are the current result/gate
authorities with SHA-256 values
`0060ef1002438488a184b9951ef12ce42e34c5eb755f6fda15a81c44bdc1d8fa` and
`3e9fc4a9b9dee26515fbed5d536e75895d9217c2ceb3e71dd14ab875bb793cb8`.

The narrow operational blocker is now `content_range_package_reconciliation`. vngrs remains only
a conditional primary materialization candidate. `blocked_by_measurement_design`,
`blocked_by_corpus_selection_or_materialization`, `ready_to_measure=false` and
`ready_to_train=false` remain unchanged. No 151ak/151ah, corpus row/full shard, materialization,
GPU/Slurm, training or cleanup work was authorized or performed.

### 12 August 2026 — Authorized Falcon recovery blocked before allocation

The exact Document 162 wave verified the frozen 15/18 family inventory twice. The first preflight
SHA-256 is `37d3d4471d504f9e3d506d48c4ab1f00c99ec2c49f09dd9a7a80e0342cac9b4f`.
The original launcher could not combine old partition `gpu` with frozen node `guppi5`; no job ID
was created. Read-only scheduler inspection showed `guppi5` under `wbimlgpu`. Since Document 162
freezes node/GRES but not the partition name and includes the Slurm/test files in its implementation
surface, the binding alone was corrected in commit
`2c1e49c86b92e116cae77857b31d77293a048564`. Node, RTX3090 selector, array `2,4,5%1`, runtime
guard and scientific recipe were unchanged; local and HU focused suites passed 100/100.

The fresh commit-bound preflight passed with SHA-256
`c49e3139427030d8f20c4e1a27e0b73197e99a064e84765fbf414e6ed2643d88`, but the corrected
submission was rejected before allocation with `User's group not permitted to use this partition`.
No evaluation array, summary job, GPU allocation or scientific evaluation was created. Falcon
checkpoint `126/210/252` and the summary root remain absent; the family remains 15/18 and no model
is selected. Documents 163/164 are the current result/gate authorities with SHA-256 values
`55c8a8c2c9565793e2656e1a8f94a195ee6956f119df919878b10a014f6bec4d` and
`b73f13c7beca9a967488d5af2702f2ff64806924a7bdc9739f6614ef4c9876d3`.

The current M1 blocker is `guppi5_partition_group_access_denied`; it is operational, not a Falcon
scientific result. Automatic retry, node/partition relocation, seed-43, Turkish dose work,
M2-A/M2-B and cleanup remain unauthorized. Any continuation requires a newly frozen contract and
exact SHA-bound authorization after either real `wbimlgpu` group access or an accessible clean
RTX3090 route is established.

### 13 August 2026 — Prepared vngrs Content-Range and Falcon RTX A6000 recoveries

Local inspection identified the vngrs validator mismatch exactly: request `Range` uses
`bytes=START-END`, while response `Content-Range` uses `bytes START-END/TOTAL`. The historical
positive fixture and validator incorrectly expected an equals sign in the response grammar.
Document 151bk freezes only this two-comparison protocol correction, strict rejection of the old
wrong form, final-audit SHA binding and one future bounded invocation. Its SHA-256 is
`18f9a3c65d7e006a29645bfcef2a26a3d48eb1224291bfe2ca122fafbfc6e4f8`.
The global measurement/corpus gates remain unchanged and no corpus rows are opened.

Live scheduler inspection also showed a local-cluster alternative to inaccessible
`guppi5/wbimlgpu`: `gruenau8` is visible under the accessible `gpu` partition with
`gpu:rtxa6000` capacity. Document 165 freezes only the three missing Falcon evaluations on exact
`gpu/gruenau8/gpu:rtxa6000:1`, preserving BF16, CC 8.6, compiled `sm_86`, all model/data/gate
identities and sequential `2,4,5%1`. It requires 40 GiB free VRAM before evaluator preparation
and a successful `sbatch --test-only` before the one real array; summary remains `afterok` and
18/18-closed. Its SHA-256 is
`e8e1d772ed7726e959f5ec5e24d81f1a4a3aeed2973f6aa3bbe5c22b078e9fda`.

The shared local implementation is commit
`68e5be9` (`Prepare vngrs range and Falcon A6000 recoveries`). Focused tests passed 102/102 and
the complete compatible suite passed 382/382. User-generated untracked artifacts remain
untouched. Neither contract has been published, synchronized to HU or executed. Exact SHA-bound
authorization is required before ordinary non-force push, preservation-checked HU fast-forward,
vngrs source access or Falcon Slurm/GPU work. Documents 151bl/151bm and 166/167 remain reserved
for execution result/gate records.

### 13 August 2026 — Authorized vngrs reconciliation passed; Falcon A6000 recovery blocked at runtime guard

The user authorized the exact Document 151bk and Document 165 waves. Commit
`68e5be9b1c15a86c8dc8071d55c5de2789600c75` was ordinary non-force pushed and
preservation-checked fast-forwarded on HU. The existing HU dirty state remained exactly 42 entries,
6,989 bytes, SHA-256 `71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9`;
local compatible tests passed 382/382 and HU focused tests passed 102/102.

The single Document 151bk executor invocation passed all fail-closed gates and produced the
accepted exact 32-shard metadata/footer package under
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1`. It completed 97 bounded logical
requests through 194 HTTP hops with zero retries, retrieved 17,047,078 response bytes and exactly
zero corpus rows, and passed the final package validator. The root contains 104 regular files /
18,025,945 regular-file bytes; its canonical relative-path-plus-size inventory SHA-256 is
`120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3`. Documents 151bl and
151bm record the result and gate with SHA-256 values
`ddc8a4cf0c57e977eeec2ab7cf5044730511d3220a3d8c24651185d845c89b6c` and
`a3f0ed973a7b8202f4b18910f247e12e849d026e1d258ddf2114f0a577a72896`.

This closes only exact vngrs metadata/footer feasibility. No corpus text, sample-quality gate or
materialization ran; vngrs is not yet selected or training-ready. The global gate remains
`blocked_by_measurement_design`, with `blocked_by_corpus_selection_or_materialization`
contributing. A separately frozen and authorized model-neutral bounded sample-calibration step is
required before materialization can be considered.

The Document 165 Falcon preflight passed at 15/18 family rows and `sbatch --test-only` succeeded.
Exactly one sequential recovery array `456414_[2,4,5%1]` and one `afterok` summary job `456415`
were submitted. All three tasks received exact `gruenau8/gpu/gpu:rtxa6000:1` allocations, but the
allocation-time guard observed only 3,142,844,416 free bytes against the frozen 42,949,672,960-byte
minimum. Each task stopped before evaluator preparation; no model evaluation, runtime manifest or
missing checkpoint root was created. The family therefore remains 15/18 and the summary remains
unrun with `DependencyNeverSatisfied`. Documents 166 and 167 record this operational NOT-RUN result
and gate with SHA-256 values
`8b208f3feac06134d6a8442c993fadb656db09029be3238aaeb6312cb5610729` and
`4e043e42a2167352e2679024d61cdaea1d376b94da45806fecd0c9525071c7e3`.

The Falcon result is an operational low-free-VRAM block, not a scientific model score. The one
array wave is consumed and no retry, cancellation, cleanup, seed-43, Turkish dose ladder or
M2-A/M2-B execution is authorized. Any family-completion attempt requires a new exact contract
limited to Falcon checkpoints 126/210/252 on an allocation whose per-device cleanliness is
verified inside the job.

### 13 August 2026 — Next bounded vngrs/Falcon preparations frozen locally

The next two fail-closed continuations are prepared locally but remain unexecuted. Document 151bn
freezes a zero-network, zero-corpus-row projection over the accepted 32-shard footer package. It
preserves Document 151ak's exact 10,000 row-count-weighted midpoint positions and computes which
Parquet row groups they touch, the contiguous row-group runs and a conservative compressed-byte
coverage projection. This avoids silently increasing the known-infeasible 100 `/rows` request
limit or changing the sampling estimand before source transport costs are quantified. Document
151bn SHA-256 is
`7716fcaf63a30feded65e617107ac3c088ce01a43ca08ac696aeec9936f42110`.

Document 168 freezes one further Falcon-only RTX A6000 recovery for missing checkpoints
`126/210/252`. It keeps the same scientific recipe and exact `gruenau8/gpu/gpu:rtxa6000:1` route,
adds Slurm node-exclusive allocation, and requires an in-job zero-compute-process, maximum 512 MiB
used-VRAM and minimum 40 GiB free-VRAM gate before evaluator namespace creation. It permits
reconciliation/cancellation only of dependency-dead summary job `456415`, followed by exactly one
`2,4,5%1` array and one `afterok` summary. Document 168 SHA-256 is
`6e57f90897db8202bcb338a84b6a3b99abb2bf3a887e1a2cdaefacdde08021c8`.

The shared local implementation is commit
`6589f6a` (`Prepare bounded vngrs projection and clean Falcon recovery`). Shell/Python syntax and
the focused related suite passed 105/105; the compatible repository suite passed 355/355 with the
three established collection exclusions. Existing user-generated untracked artifacts remained
untouched. The commit has not been pushed or synchronized to HU. Neither projection execution,
job cancellation, Slurm submission nor GPU work is authorized until the user supplies exact
SHA-bound authorization for the corresponding contract.

### 13 August 2026 — Authorized transport projection and exclusive Falcon recovery results

The exact Document 151bn wave ran once and produced one 31,554-byte, zero-network,
zero-corpus-row projection artifact with SHA-256
`c5f4d7a392870528bdd1f2f52da1bb83f6ec8381cb4bf5d095cf142219106ca2`. The exact 10,000
row-count-weighted midpoint schedule touches 5,664 of 5,696 row groups and projects
9,455,428,874 of 9,468,474,036 compressed bytes (`0.9986222529680706`). Thus the existing
100-request `/rows` route remains infeasible and row-group-granular Parquet extraction is
effectively full-selected-shard transport, not a bounded sample. Documents 151bo/151bp record the
result/gate with SHA-256 values
`53c8d401099d766c9688a9b9a2beb404b5da43fff1e7f6995ae5fdde522589ee` and
`dfdc05d11820576a2ca40ae50a78454a1d9167a3ec979488021a5d123afe9113`.

The exact Document 168 preflight and `sbatch --test-only` passed. Old dependency-dead summary job
`456415` was cancelled as explicitly allowed; exactly one array `456466_[2,4,5%1]` and one
`afterok` summary `456467` were submitted. Slurm node-exclusive semantics allocated all four
A6000 GPUs (`AllocTRES gres/gpu:rtxa6000=4`) although the request named one. All three tasks failed
at the first `torch.cuda.device_count() == 1` gate before process evidence, runtime manifests,
evaluator preparation or model load. No scientific evaluation ran, the three roots remain absent,
the family remains 15/18 and summary `456467` is dependency-never-satisfied. Documents 169/170
record the result/gate with SHA-256 values
`b6b01e968cc499f7529a37359986ed8aa52cd2d8f9117f885b745e54b867370e` and
`dfc1d792ef886d9e60782cb9700d172bb1bdd8ff2d586c1a4cc9b7cb03facce7`.

Both waves are consumed. No automatic retry, full-shard/sample retrieval, dead-summary
cancellation, seed-43, Turkish dose ladder, M2-A/M2-B, cleanup or deletion is authorized. The
corpus route needs a new precommitted sampling-design choice; Falcon needs either true single-GPU
isolation or a separately frozen deterministic UUID-selection rule over a fully audited exclusive
four-GPU allocation.

### 13 August 2026 — Clustered vngrs design and deterministic clean-UUID Falcon recovery prepared

Document 151bq replaces the transport-infeasible shard-wide midpoint sample with a clearly new
stratified clustered-window calibration estimand. The accepted 32 shards retain exact
row-count-proportional 10,000-record allocation; each shard is split into four integer row strata,
one deterministic seed-42 contiguous cluster is selected per stratum, and exact per-row
conditional inclusion probabilities/inverse weights are recorded. The resulting schedule has
exactly 128 windows, 78--79 rows per window and 10,000 rows total. Cluster-bootstrap uncertainty
is explicitly approximate and no release-wide representativeness claim is permitted. Document
151bq SHA-256 is
`a52b445c7b588e371df9876d7b4f65af5bef4f3b0531e89576c5af6ae38101d6`.

The clustered schedule implementation is locally complete, but vngrs execution remains
`PREPARATION_BLOCKED`: no exact immutable shard-bound `/rows` route or bounded Parquet
range/reconstruction adapter is yet frozen. Global Dataset Viewer offsets may not substitute for
selected-shard identity. No execution authorization should be requested for 151bq until that
transport evidence is appended without changing the 128-window schedule.
The official Dataset Viewer route audit confirms that `/rows` exposes only dataset/config/split,
split-global offset and length (maximum 100), without original immutable revision or shard-path
binding; `/parquet` lists auto-converted `refs/convert/parquet` artifacts whose identity cannot be
silently substituted for the frozen original shard set.

Document 171 freezes a Falcon-only deterministic clean-UUID recovery. Under the same exclusive
gruenau8 allocation, a pre-Torch selector requires the initial `CUDA_VISIBLE_DEVICES` set to match
exactly the four audited A6000 indices or UUIDs, records index/UUID/name/memory/process evidence for
all four devices, filters candidates with zero compute processes, at least 40 GiB free and at most
512 MiB used, and selects the lexicographically smallest clean UUID. Only then is
`CUDA_VISIBLE_DEVICES` narrowed and the existing one-device runtime validator run. The only
permitted dead-job cancellation is `456467`; missing tasks remain `2,4,5%1` and summary remains
afterok/18-of-18 closed. Document 171 SHA-256 is
`b54983a5638391fec575a47f3934b4d674b9e8d655de7c6b5e8818fabc69778e`.

The shared local implementation is commit
`8259edb` (`Prepare clustered vngrs design and clean GPU selection`). Syntax and the focused suite
passed 111/111; the compatible repository suite passed 363/363 with the established three
collection exclusions. Existing user-generated untracked artifacts remain untouched. The commit
has not been pushed or synchronized to HU, and no HU/Slurm/GPU/network/corpus execution occurred.
Document 171 requires exact SHA-bound authorization before publication or execution; Document
151bq remains preparation-blocked and is not yet eligible for such authorization.

### 13 August 2026 — Authorized deterministic clean-UUID Falcon recovery result

The exact Document 171 wave was executed once. Commit
`8259edb6aaa9de7c853af44e658b8c1d356db7ea` was ordinary non-force pushed and
preservation-checked fast-forwarded on HU; the focused HU suite passed 14/14. Fresh preflight
passed with SHA-256 `01ecab114349674598fe88b09afc5fcfb83419f8c598a7d1e5904f1e3cbe2bc7`,
the exact 15/18 inventory and missing Falcon checkpoints `126/210/252`. The authorized old
dependency-dead summary `456467` was cancelled, `sbatch --test-only` passed as `456500`, and
exactly one sequential evaluation array `456501_[2,4,5%1]` plus one `afterok` summary `456502`
were submitted.

All three evaluation tasks stopped before Torch/runtime validation, evaluator preparation or model
load because the pre-Torch selector found no UUID satisfying the frozen zero-compute-process,
minimum 40 GiB free and maximum 512 MiB used gates. No arbitrary device was selected and no
scientific evaluation ran. However, the implementation wrote its audit artifact only after a
successful candidate selection; therefore the no-candidate exception occurred before the required
four-device UUID/memory/process ledger was persisted. This is a fail-closed operational NOT-RUN
with a separate Document 171 failure-evidence persistence breach, not a Falcon score.

The missing evaluation/runtime/audit roots remain absent, family inventory remains 15/18, and
summary `456502` is `DependencyNeverSatisfied` with no summary root. Documents 172 and 173 record
the result and current blocked gate with SHA-256 values
`5730e84c55c663e6a243d95cb1de0c76fb0636fdb08359fe6b0b286bce6dfe42` and
`cdcd642cf6bb43ff48e2f1be1ef268820d82c448920733aebf12d481ca170d44`.
The one wave is consumed. No retry, new dead-summary cancellation, reroute, seed-43, recipe or
threshold change, Turkish dose ladder, M2-A/M2-B, cleanup or deletion is authorized. Any future
continuation requires a new exact contract that atomically persists the four-GPU ledger before
candidate selection on both PASS and FAIL paths.

### 13 August 2026 — Audit-persistent single-allocation Falcon recovery prepared locally

Document 174 freezes the next Falcon-only correction. It preserves the exact 15/18 family state,
training/checkpoints, BF16, seed 42, model/data/runtime identities, thresholds and evaluation
cascade. The pre-Torch selector now atomically writes the complete four-GPU UUID/memory/process
ledger on the no-candidate path with `BLOCKED_NO_CLEAN_CANDIDATE`, `selected_uuid=null` and exact
per-device rejection reasons before raising. PASS still selects only the lexicographically
smallest GPU satisfying zero compute processes, minimum 40 GiB free and maximum 512 MiB used.

To eliminate allocation-to-allocation device drift, the proposed wave uses exactly one exclusive
non-array job and keeps the selected physical UUID fixed while evaluating missing Falcon
checkpoints `126 -> 210 -> 252` sequentially. A failure stops the remaining steps; the single
summary remains `afterok` and 18/18 closed. Only dependency-dead summary `456502` may be
reconciled after fresh preflight PASS. Document 174 SHA-256 is
`75964edfdd4e3d792ac355ce9e966db9918e88b9aed59953daa2bf071fce0a3a`.

Local Python/shell syntax passed, the focused selector/M1 suite passed 16/16, and the compatible
repository suite passed 382/382 with the three established collection exclusions. Existing
user-generated untracked artifacts remain untouched. The local implementation is commit
`9314a02b7a6986d760602002648372d266d04227`. No push, HU synchronization, SSH, job
cancellation, Slurm/GPU or evaluation occurred. Exact SHA-bound user authorization is required
before the single Document 174 wave; Documents 175/176 are reserved for its result/gate.

### 13 August 2026 — Authorized audit-persistent Falcon recovery result

The exact Document 174 wave was executed once. Commit
`9314a02b7a6986d760602002648372d266d04227` was ordinary non-force pushed and
preservation-checked fast-forwarded on HU; the HU focused suite passed 16/16. Fresh preflight
passed with SHA-256 `32787e7f2271c4638c7eafefc665806f080bc83b9a8f3af20174cfc5176a519f`,
the exact 15/18 inventory and missing Falcon checkpoints `126/210/252`. The authorized old dead
summary `456502` was cancelled, test-only passed as `456593`, and exactly one non-array evaluation
job `456594` plus one `afterok` summary `456595` were submitted.

Job `456594` immediately obtained the exclusive four-A6000 allocation and failed closed before
Torch/runtime validation or model load because every GPU was occupied by one member of a foreign
`VLLM::Worker_TP0--TP3` tensor-parallel workload. Every device had 3,423,600,640 free bytes and
47,474,278,400 used bytes, so all four failed the frozen process, free-memory and used-memory
gates. The repaired audit path passed: the 2,522-byte `BLOCKED_NO_CLEAN_CANDIDATE` manifest was
atomically preserved with SHA-256
`68751ff26908b1555370e93806003b6c4a79cf857e64a38cb6aa35faf26487b3` and no selected UUID.

No runtime manifest, missing evaluation root, scientific row or family summary was created. The
family remains 15/18; summary `456595` is dependency-dead and was not cancelled. Documents 175
and 176 are the current result/gate authorities with SHA-256 values
`06fe7bad684183e9572dc3d8e7d7fd2824add0fb0ceac1606df1bf6668568b01` and
`6c7b506324e243d8dabe2fdbd660f4edf3eece8b2b93b4e108636c9d3308598c`.

The wave is consumed. The evidence now classifies the blocker as external clean-capacity/
ownership availability, not a deterministic selector defect. No blind same-route retry, foreign
process intervention, dead-summary cancellation, reroute, seed-43, recipe/threshold change,
Turkish dose ladder, M2-A/M2-B, cleanup or deletion is authorized. A future continuation requires
verified clean capacity or a separately frozen accessible clean GPU route.
