# M1 Completion Update

**Supervisor briefing note**  
**Date:** 13 July 2026  
**Project:** Transfer vs. Relearning in Cross-Lingual Factual Adaptation

Dear Max,

I prepared this note to summarize an important result from M1, the English factual-acquisition
stage of the project. For a long time, our central difficulty was that the model could memorize
synthetic facts in the training format but could not retrieve them reliably under new English
question formulations. The latest controlled experiments have almost completely resolved this
problem in the 500-fact development condition.

The short version is:

> SmolLM2-1.7B learned 500 independently assigned synthetic facts in English and retrieved them
> with more than 99% robust accuracy both in an exact-prefix format close to training and in two
> held-out question formats, across two independent training orders. The precommitted M1 gate was
> exceeded by a large margin in both runs. We therefore consider M1 complete for the 500-fact
> Relation V2 setting and are ready to proceed to the M2/M3 Turkish adaptation experiments.

## 1. Why Is M1 Critical to the Thesis?

The main thesis question is whether an English-learned fact becoming accessible in Turkish after
Turkish adaptation constitutes genuine cross-lingual transfer or relearning from Turkish data.

To answer that question, one prerequisite must be satisfied:

> Before M2 and M3 begin, the fact must genuinely have been learned in English and must be
> reliably accessible across different English prompt formulations.

If a fact was not learned during M1, failure to answer it in Turkish after M2 provides no
meaningful negative evidence about transfer. M1 is therefore not merely a preparation stage; it
is a validity condition for the subsequent causal analysis.

## 2. Experimental Setting

The current Relation V2 development set has the following structure:

- 100 synthetic subjects;
- 5 facts per subject;
- 500 facts in total;
- 5 relations: `profession`, `born_in`, `lives_in`, `field_of_study`, and `works_in_industry`;
- 7 English acquisition rows per fact;
- 3,500 training rows in total;
- independent and balanced subject-relation-object assignments;
- a chance-level M0 result supporting that the target facts were not already known by the base model.

`field_of_study` and `works_in_industry` replaced the earlier proper-name-heavy `studied_at` and
`works_at` relations. This change reduced collapse toward a few dominant institution names while
preserving the thesis's subject-relation-object binding question.

## 3. How Do We Measure Success?

We evaluate the model through a frozen relation-specific candidate inventory rather than open
generation. Every candidate is scored under the same prompt, and the rank of the correct object
is calculated.

We use three complementary views:

1. **Exact-prefix:** A completion closest to the training scaffold. This strongly tests whether
   the fact has been stored.
2. **Held-out direct:** A direct English question that does not occur verbatim in training.
3. **Held-out QA-matched:** The same held-out question inside a `Question: ... Answer:` scaffold.

The main robust metric is:

```text
direct rank 1 AND QA rank 1
```

The `Triple` metric additionally requires exact-prefix rank 1.

The M1 gate was defined before the results were inspected:

| Metric | Gate |
|---|---:|
| Exact | at least 450/500 |
| Direct | at least 400/500 |
| QA | at least 400/500 |
| Direct/QA overlap | at least 350/500 |

These thresholds were not changed after seeing the results.

## 4. The Previous Bottleneck

In the SmolLM2-360M Relation V2 500-fact experiment, exact storage was perfect, but held-out
retrieval narrowly missed the gate:

| Model | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| SmolLM2-360M | 500 | 378 | 377 | 329 |

This was an important result: the model was not losing the facts, but it struggled to access the
correct object through the relation and a new prompt.

In the exploratory 2,500-fact experiment, exact storage remained at 99.92%, while overlap fell to
38.32%. For the same nested first 500 facts, overlap declined from 329 to 188. This finding showed
that storage capacity and prompt-robust retrieval/binding capacity are distinct.

## 5. Controlled Capacity Experiment

In the new experiment, we increased only model capacity:

```text
SmolLM2-360M -> SmolLM2-1.7B
```

The following scientific variables were held constant:

- the same 500 facts and the same 3,500 rows;
- the same answer-only objective;
- the same learning rate: `1e-4`;
- the same 36 epochs;
- the same effective batch size: 500;
- the same 252 optimizer updates;
- the same scheduler, warmup, and weight decay;
- the same exact/direct/QA evaluator;
- the same precommitted gate.

Only the operational batch decomposition changed so that the 1.7B model would fit on the A100:
we used a micro-batch of 10 and gradient accumulation of 50. The effective batch size and
optimizer-step budget remained unchanged.

## 6. Primary Result: Seed 42

In the first valid 1.7B run, checkpoint 200 was selected:

| Metric | Result | Rate |
|---|---:|---:|
| Exact | 500/500 | 100.0% |
| Direct | 499/500 | 99.8% |
| QA | 498/500 | 99.6% |
| Direct/QA overlap | 497/500 | 99.4% |
| Triple | 497/500 | 99.4% |

The precommitted gate was already passed at checkpoint 50. Performance was nearly saturated and
stable from checkpoint 75 onward.

Absolute change relative to the 360M reference:

| Metric | 360M | 1.7B | Change |
|---|---:|---:|---:|
| Exact | 500 | 500 | 0 |
| Direct | 378 | 499 | +121 |
| QA | 377 | 498 | +121 |
| Overlap | 329 | 497 | +168 |

Exact storage was already saturated in the 360M model. The main contribution of the 1.7B model
was therefore not memorizing more facts, but accessing stored subject-relation-object bindings
through held-out prompts.

## 7. Independent Training-Order Replication

We ran a second experiment to test whether the result depended on a single data order. The train
and validation files remained unchanged, and the split seed remained 42. The training seed and
data-order seed were changed to 43.

An important methodological control occurred at this point. In the first seed-43 attempt, the
training seed changed, but the data-order seed remained 42. Because attention dropout is zero in
SmolLM2-1.7B, this run deterministically reproduced the seed-42 weights. We detected this through
the loss curve and byte-level checkpoint comparison. We did not report that run as an independent
replication; it is recorded only as a reproducibility control.

We then added and tested explicit `data_seed` support independent of the split seed. The valid
replication used split seed 42, training seed 43, and data seed 43. Its loss curve diverged from
seed 42, confirming a genuinely different training path.

The selected seed-43 checkpoint 75 produced:

| Metric | Result | Rate |
|---|---:|---:|
| Exact | 500/500 | 100.0% |
| Direct | 500/500 | 100.0% |
| QA | 499/500 | 99.8% |
| Direct/QA overlap | 499/500 | 99.8% |
| Triple | 499/500 | 99.8% |

## 8. Combined Result Across Both Runs

| Run | Selected checkpoint | Exact | Direct | QA | Overlap | Triple |
|---|---:|---:|---:|---:|---:|---:|
| Seed 42 | 200 | 500 | 499 | 498 | 497 | 497 |
| Seed 43 / data seed 43 | 75 | 500 | 500 | 499 | 499 | 499 |
| Two-run mean | - | 500.0 | 499.5 | 498.5 | 498.0 | 498.0 |

Robust overlap:

```text
360M reference:  65.8%
1.7B seed 42:    99.4%
1.7B seed 43:    99.8%
```

The main capacity result is therefore not dependent on a single checkpoint or data order.

## 9. Remaining Reproducible Error

Only one non-triple fact remains at the selected seed-43 checkpoint:

```text
Meggy Melvin -> lives_in -> Omaha
```

- exact-prefix: correct, Omaha rank 1;
- held-out direct: correct, Omaha rank 1;
- QA-matched: Gaziantep rank 1, Omaha rank 2.

The same fact is one of the three errors at the seed-42 checkpoint. This points to a narrow and
reproducible QA prompt-binding hard case rather than broad stochastic instability. It is not a
reason to remove `lives_in`; the relation is scientifically valuable precisely because it shares
the same city inventory with `born_in`.

## 10. Scientific Interpretation

The result strongly supports the following claim:

> The 500-fact retrieval plateau observed in the 360M model was not a fundamental failure of the
> Relation V2 data or the answer-only acquisition objective. The bottleneck was largely the
> model's capacity to access stored bindings through different prompts. With the same data and
> optimization budget, the 1.7B model almost completely closed this gap.

This result does not invalidate the earlier 2,500-fact finding. Instead, it opens a new research
question: to what extent can the 1.7B model preserve the binding/retrieval performance achieved at
500 facts under greater fact density? This scaling question should not delay the transition to
M2/M3.

## 11. Is M1 Complete?

Yes, but the scope must be stated precisely:

> M1 is complete for the Relation V2 500-fact setting with SmolLM2-1.7B.

The completion criteria are:

- the exact-storage gate passed;
- both held-out English retrieval gates passed;
- the robust-overlap gate passed;
- the result was reproduced under an independent data order;
- selected checkpoints were frozen as model-only artifacts;
- model manifests and SHA-256 hashes were generated;
- large artifacts are stored on scratch storage rather than the shared student home filesystem.

Frozen models:

- canonical primary trajectory: seed-42 checkpoint 200;
- replication/control trajectory: seed-43 checkpoint 75.

## 12. What Does This Result Not Mean?

It is important not to overgeneralize the result:

- We have not yet shown that English facts transfer into Turkish.
- We have not yet measured English retention after M2 generic Turkish adaptation.
- We have not yet measured the effect of M3 Branch-B Turkish repetition.
- The result applies to the controlled synthetic 500-fact condition and cannot be generalized directly to 25,000 facts.
- Candidate-ranking success is not equivalent to open-generation language quality.
- Our strong evidence currently concerns only the SmolLM2 family.

This result is therefore not the final answer to the thesis. It is the critical M1 closure that
allows us to begin the final causal experiment on reliable foundations.

## 13. Next Stage: M2 and M3

The proposed next path is:

### M2 - Generic Turkish Adaptation

- start from the canonical M1 seed-42 checkpoint 200;
- use a general Turkish corpus that has passed contamination control;
- do not expose the target synthetic facts in the Turkish adaptation data;
- measure English exact/direct/QA retention after adaptation;
- measure Turkish direct/QA access for the same facts.

An increase in Turkish retrieval after M2 could constitute evidence for cross-lingual access or
transfer because the target facts are absent from the Turkish corpus.

### M3 - Turkish Repetition / Relearning Condition

- start independently from the same frozen M1 checkpoint;
- match the M2 token and optimizer budgets;
- add Turkish repetitions of Branch-B facts as the single controlled difference;
- compare Branch A as transfer-only with Branch B as transfer-plus-relearning.

Main analysis:

```text
(M3 - M2 change, Branch B) - (M3 - M2 change, Branch A)
```

Seed-43 checkpoint 75 can serve as a parallel replication/control arm for the primary M2/M3
trajectory. To manage compute cost, I recommend first running the canonical seed-42 M2/M3 pilot
and then replicating the necessary selected checkpoints with seed 43.

## 14. Reproducibility and Operational Note

The following materials were created for both selected models:

- a model-only `model.safetensors` copy;
- configuration files;
- a local model manifest;
- source training-run and checkpoint metadata;
- a SHA-256 hash file.

After training and evaluation artifacts accidentally accumulated on the shared student home
fileserver, we corrected the storage lifecycle. Home usage was reduced from 474 GB to 7.88 GiB;
runs, models, datasets, caches, and evaluation outputs are now stored under `/vol/tmp` or
`/vol/tmp2`, while legacy repository paths are preserved through symlinks. Storage audits will be
mandatory before and after future scale-ups.

## 15. Decisions to Discuss with the Supervisor

1. Do we confirm seed-42 checkpoint 200 as the canonical M2/M3 primary trajectory?
2. In the first M2 pilot, should we report the full frozen 500-fact membership, or also a relation-stratified sensitivity subset?
3. Should the seed-43 replication arm be evaluated at every M2/M3 checkpoint or only at selected final checkpoints?
4. Should the 1.7B 2,500-fact scaling control run before M2/M3 or later as a secondary capacity analysis?
5. How prominently should the thesis present the 360M storage-versus-retrieval distinction and the 1.7B capacity resolution as a separate main finding?

## 16. One-Paragraph Summary

We first established that synthetic facts could be stored but not reliably retrieved under new
prompt formulations. With Relation V2 and direct-aware answer-only acquisition, the 360M model
stored all 500 facts exactly, but robust overlap remained at 65.8%. Holding data, objective,
exposure, and evaluation constant while increasing only the model to 1.7B raised overlap to 99.4%
for seed 42 and 99.8% in an independent data-order replication. Both runs exceeded the
precommitted M1 gate by a large margin, and the selected models were frozen with manifests and
hashes. We therefore consider M1 complete in the Relation V2 500-fact setting; the project is now
ready for the causal cross-lingual comparison between M2 generic Turkish adaptation and M3
Turkish repetition/relearning.

It is genuinely encouraging to be able to report this result. The long sequence of negative
experiments was not wasted. It clarified the failure mode we were measuring and created the
control structure that makes the present positive result credible.
