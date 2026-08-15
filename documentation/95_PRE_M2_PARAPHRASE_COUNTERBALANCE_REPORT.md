# 95 - Pre-M2 Paraphrase Counterbalance Report

**Date:** 2026-07-18  
**Status:** WP1B completed; crossed-form robustness gate failed  
**Parent plan:** `93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md`  
**Previous wave:** `94_PRE_M2_FROZEN_HARD_EVALUATION_REPORT.md`

## 1. Scope And Decision

This wave ran the precommitted WP1B subject-form counterbalance experiment on SmolLM2-1.7B. It
tests whether a fact learned through one question form transfers to a different form for the same
subject. The original run assigned 50 subjects to Form A and 50 to Form B. The swap replication
kept the same facts and subjects but reversed every A/B assignment.

The result is a **WP1B HOLD**:

- both models reach 100% top-1 on the form seen for each subject;
- crossed held-out performance is only 39.0% in the original condition and 38.8% in the swap
  condition when direct and QA scaffolds are combined;
- the required A/B four-cell robust intersection is 28.0% and 28.4%, far below the frozen 70%
  threshold; and
- the swap replication reproduces the same large seen-over-crossed gap.

This is not a failed run. It is controlled evidence that the recipe stores the facts strongly but
does not make their retrieval independent of the subject-specific training form. M2 remains
blocked. WP3 and WP5 still answer separate supervisor questions and remain required.

## 2. Frozen Design And Integrity

The Phase 0 contract from report 94 was retained without post-result changes:

- 100 subjects and five relations per subject: 500 facts;
- original assignment: 50 subjects Form A, 50 subjects Form B;
- swap assignment: all 100 subject-form assignments reversed;
- seven acquisition rows per fact and 3,500 rows per condition;
- identical scaffold sequence per fact: four direct and three QA exposures;
- identical fact graph, row budget, optimizer settings, objective, and 252 optimizer updates;
- answer-only loss with supervised EOS;
- all subjects evaluated under Form A, Form B, and novel Form C, each under direct and QA
  scaffolds: 3,000 probes per model;
- 2,000 paired bootstrap samples, seed `20260717`, plus exact McNemar tests.

Integrity evidence:

| Item | Value |
|---|---|
| Original train rows | 3,500 |
| Swap train rows | 3,500 |
| Rows per fact | 7 |
| A/B rows per condition | 1,750 / 1,750 |
| Unique training prompts per condition | 1,000 |
| Shared original/swap subject-form training prompts | 0 |
| Dataset manifest SHA-256 | `b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752` |
| Probe registry SHA-256 | `2cf9bf4a61f7ef3771e71caf61f03a3e59d22707ef4d5367a6ef6184a18f664b` |
| Original assignment SHA-256 | `9658ca5902c0d1734cb27405a4b614216575f944e27a95ecf8df191894b8ce37` |
| Swap assignment SHA-256 | `9d7dfc43ab89805cf4134e5244efe7e3771aa88a8ad771d5f071c59b068978ac` |
| Base weights SHA-256 | `1193528982f4ac0c0b707ce36fd7dc03a0ef6f3e1a432deb886dce2e90c300c0` |

The final models were live-hashed rather than inheriting the base manifest's file hashes:

| Condition | Final `model.safetensors` SHA-256 | Bytes |
|---|---|---:|
| Original | `844aadb4f4714864498b0bed9bbb1f7cd4b7461832a953019c90f49d243dc9d2` | 3,422,777,952 |
| Swap | `5f98b4fdcd3b89d4ef5cc3221cba170182e0e0cac875d78eaf64e046434f1529` | 3,422,777,952 |

The distinct hashes confirm that the two evaluations used distinct trained weights.

## 3. Implementation And HU Execution

Implementation commits on `corpus-update`:

- `ebc8aad`: WP1B datasets, configs, integrity checks, launch manifests, GPU smoke, and scratch-safe
  Slurm launcher;
- `f7073b2`: local model manifests hash the live final-model files;
- `214bbda`: manifest-test artifact isolation;
- `f0cbb05`: condition-aware seen/crossed/novel analysis, paired statistics, and robust gates.

HU jobs:

| Job | Purpose | Result | Runtime evidence |
|---:|---|---|---:|
| `406918` | one-batch forward/backward smoke | passed; loss `5.9583`, 218 gradient tensors | about 00:01:40 |
| `406919` | original counterbalanced training | completed, 252 updates | train runtime 00:52:06 |
| `406920` | A/B-swap training | completed, 252 updates | train runtime 00:51:50 |
| `406921` | original frozen 3,000-probe evaluation | completed | 00:09:31 |
| `406922` | swap frozen 3,000-probe evaluation | completed | 00:09:35 |

Training used commit `ebc8aadcfed863469c1720c9d361aeaaa1e371b8`. The smoke and both
training jobs ran on A100 80 GB GPUs. The smoke peak allocation was 7.29 GB. Evaluation stderr
contained only a non-fatal Transformers `torch_dtype` deprecation and weight-loading progress; no
exception occurred.

Storage remained compliant:

- HU home usage was `8.0G` before and after the wave;
- all datasets, checkpoints, final models, caches, logs, and raw evaluations stayed on scratch;
- original training retained approximately `109G` and swap training approximately `109G`, each
  including 11 resumable checkpoints and the final model;
- each evaluation retained approximately `12M`; the comparison retained `3.2M`.

Intermediate checkpoints and optimizer state are reproducible scratch cleanup candidates after
the selected final models and compact evidence are retained. No checkpoint cleanup was performed
during this report.

## 4. Training Outcome

Both conditions fit their assigned training forms almost perfectly:

| Condition | Final monitoring eval loss | Train loss reported over full run |
|---|---:|---:|
| Original | 0.0003502 | 0.2459 |
| Swap | 0.0003813 | 0.2451 |

These low losses verify optimization success on the acquisition distribution. They do not by
themselves establish prompt-robust retrieval, which is measured by the frozen crossed cells below.

## 5. Seen, Crossed, And Novel-Form Results

### Aggregate by scaffold

| Condition | Scaffold | Seen | Crossed held-out | Novel Form C |
|---|---|---:|---:|---:|
| Original | direct | 500/500 (100.0%) | 161/500 (32.2%) | 234/500 (46.8%) |
| Original | QA | 500/500 (100.0%) | 229/500 (45.8%) | 229/500 (45.8%) |
| Swap | direct | 500/500 (100.0%) | 163/500 (32.6%) | 229/500 (45.8%) |
| Swap | QA | 500/500 (100.0%) | 225/500 (45.0%) | 249/500 (49.8%) |

Combined across the two scaffolds:

| Condition | Seen | Crossed held-out | Novel Form C | All 3,000 probes |
|---|---:|---:|---:|---:|
| Original | 1,000/1,000 | 390/1,000 (39.0%) | 463/1,000 (46.3%) | 1,853/3,000 (61.8%) |
| Swap | 1,000/1,000 | 388/1,000 (38.8%) | 478/1,000 (47.8%) | 1,866/3,000 (62.2%) |

### Crossed and novel performance by relation

Direct and QA scaffolds are combined here; every cell has `n=200`.

| Relation | Original crossed | Swap crossed | Original novel | Swap novel |
|---|---:|---:|---:|---:|
| `profession` | 39.0% | 48.5% | 11.5% | 21.0% |
| `born_in` | 13.5% | 28.5% | 37.0% | 50.0% |
| `lives_in` | 51.5% | 41.5% | 60.0% | 54.0% |
| `field_of_study` | 30.0% | 25.5% | 55.0% | 53.5% |
| `works_in_industry` | 61.0% | 50.0% | 68.0% | 60.5% |

The crossed failure is broad rather than confined to one relation. `born_in` is the weakest
crossed relation in the original assignment, while `works_in_industry` is the strongest; neither
condition approaches the required 80% crossed target.

## 6. Directional Generalization Gaps

The seen-minus-crossed gaps are large in both assignment directions and reproduce after the swap:

| Condition | Scaffold | Training group | Seen | Crossed | Gap | 95% paired bootstrap CI | McNemar p |
|---|---|---|---:|---:|---:|---|---:|
| Original | direct | A | 250/250 | 82/250 | +67.2 points | [+61.6,+72.8] | `5.35e-51` |
| Original | direct | B | 250/250 | 79/250 | +68.4 points | [+62.4,+74.4] | `6.68e-52` |
| Original | QA | A | 250/250 | 102/250 | +59.2 points | [+53.2,+65.2] | `5.61e-45` |
| Original | QA | B | 250/250 | 127/250 | +49.2 points | [+43.2,+55.2] | `1.88e-37` |
| Swap | direct | A | 250/250 | 83/250 | +66.8 points | [+60.8,+72.4] | `1.07e-50` |
| Swap | direct | B | 250/250 | 80/250 | +68.0 points | [+62.0,+74.0] | `1.34e-51` |
| Swap | QA | A | 250/250 | 102/250 | +59.2 points | [+53.2,+65.2] | `5.61e-45` |
| Swap | QA | B | 250/250 | 123/250 | +50.8 points | [+44.8,+56.8] | `1.18e-38` |

Every interval excludes zero by a wide margin. Because reversing the A/B assignment preserves the
same qualitative and quantitative gap, the result is not explained by the original subject split.

## 7. Required A/B Robust Intersection

This precommitted gate requires top-1 success for Form A direct, Form A QA, Form B direct, and Form
B QA for the same fact.

| Relation | Original | Swap | Threshold |
|---|---:|---:|---:|
| `profession` | 23/100 | 32/100 | 70/100 |
| `born_in` | 8/100 | 23/100 | 70/100 |
| `lives_in` | 41/100 | 29/100 | 70/100 |
| `field_of_study` | 19/100 | 17/100 | 70/100 |
| `works_in_industry` | 49/100 | 41/100 | 70/100 |
| **All facts** | **140/500 (28.0%)** | **142/500 (28.4%)** | **350/500 (70%)** |

No relation passes the gate in either condition. This directly triggers WP1B HOLD.

## 8. Failure Taxonomy

| Condition | Correct | Prompt-form failure | Same-subject relation swap | Early-EOS preference |
|---|---:|---:|---:|---:|
| Original | 1,853 | 712 | 180 | 255 |
| Swap | 1,866 | 694 | 216 | 224 |

Prompt-form failure is the dominant error class. City relations retain binding errors: the
original run has 108 `born_in` and 72 `lives_in` same-subject swaps; the swap run has 107 and 109.
Early-EOS failures reappear under unseen forms even though seen-form acquisition loss is nearly
zero. WP5 remains necessary to separate EOS supervision from LR and prompt-distribution effects.

## 9. Interpretation And Next Decision

Report 94 showed that the canonical Relation V2 M1 checkpoints were robust across Forms A and B.
WP1B now shows that training each subject through only one of those forms produces near-perfect
seen retrieval but weak crossed retrieval. The defensible interpretation is:

1. the model can acquire and retrieve all 500 facts under the trained wording;
2. the learned retrieval path is strongly conditioned on the subject's acquisition form;
3. the canonical M1 robustness likely benefits from its diversified declarative, direct, and QA
   acquisition templates rather than proving fully prompt-independent storage; and
4. the swap replication makes subject-group imbalance an implausible explanation for the gap.

The evaluator, thresholds, candidate inventories, and form definitions remain frozen. The failed
gate must not be repaired post hoc by changing them. Any future attempt to improve paraphrase
transfer must be a new versioned training intervention.

The next pre-M2 wave is WP3:

1. build and manually inspect the 10-subject four-relation fixture;
2. run the relation-pair smoke only if every generated example and same-subject hard negative is
   correct;
3. then run the 100-subject/400-fact joint-relation diagnostic;
4. run WP5 LR/EOS controls after the WP3 gated wave; and
5. keep M2 on HOLD until the remaining supervisor questions and final synthesis are complete.

## 10. Artifacts

HU scratch roots:

```text
/vol/tmp2/yesildau/pre_m2_followup_v1/training/paraphrase_counterbalance/
/vol/tmp2/yesildau/pre_m2_followup_v1/evaluations/wp1b_original/
/vol/tmp2/yesildau/pre_m2_followup_v1/evaluations/wp1b_swap/
/vol/tmp2/yesildau/pre_m2_followup_v1/comparison/wp1b/
```

Key artifacts:

```text
manifests/wp1b_original_final_model.json
manifests/wp1b_swap_final_model.json
evaluations/wp1b_{original,swap}/hard_suite_per_fact.csv
evaluations/wp1b_{original,swap}/teacher_forced_per_token.csv
comparison/wp1b/per_fact_with_exposure_cell.csv
comparison/wp1b/accuracy_by_exposure_cell.csv
comparison/wp1b/directional_generalization_gaps.csv
comparison/wp1b/required_ab_robust_intersections.csv
comparison/wp1b/comparison_manifest.json
```

Compact copies used for local report verification are under the ignored workspace path
`transfer-vs-relearning/artifacts/pre_m2_followup_v1/remote/wp1b/`.
