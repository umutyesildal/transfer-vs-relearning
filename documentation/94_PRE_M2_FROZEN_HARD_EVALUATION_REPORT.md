# 94 - Pre-M2 Frozen Hard Evaluation Report

**Date:** 2026-07-17  
**Status:** WP1A, WP2, and the frozen-checkpoint part of WP4 completed  
**Parent plan:** `93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md`

## 1. Scope

This wave tested the unchanged base SmolLM2-1.7B and both selected Relation V2 M1 checkpoints
without retraining. It answers three questions:

1. how the frozen models behave under three new paraphrase families and two scaffold formats;
2. how gold-answer and EOS likelihood evolve under teacher forcing; and
3. whether the two M1 runs remain strong under harder prompt and same-subject city-swap controls.

This report does **not** complete WP1B subject-form counterbalanced training, WP3 joint-relation
training, or WP5 LR/EOS ablations. M2 remains blocked by the parent plan.

## 2. Phase 0 And Integrity

The default interpretation was frozen:

- 100 subjects and 500 facts, not 500 people;
- 50 subjects assigned prospectively to Form A and 50 to Form B for WP1B;
- assignment seed `20260717`;
- maximum A/B difference across branch, name type, name rarity, popularity, and every relation's
  frequency bucket: `1`;
- three new form families per relation and separate direct/QA scaffolds;
- 3,000 probes per model: `500 facts x 3 forms x 2 scaffolds`;
- normalized prompt overlap with canonical M1 training rows: `0`;
- candidate inventories: profession `200`, city `130`, field `50`, industry `50`;
- dataset manifest SHA-256:
  `b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752`;
- probe registry SHA-256:
  `2cf9bf4a61f7ef3771e71caf61f03a3e59d22707ef4d5367a6ef6184a18f664b`;
- tokenizer fingerprint SHA-256:
  `06e5fa9e7c85ffd9d295305b963cc3b41f60f23440ec344f914da928584a5edd`.

The one-probe base-model smoke and the full base run produced an identical canonical per-fact
row hash. The repeatability audit passed.

### Frozen-weight hash correction

The two existing frozen M1 manifests incorrectly declare the base-model weight hash for their
`model.safetensors` files. The files themselves are distinct and were live-hashed before result
acceptance:

| Model | Live `model.safetensors` SHA-256 | Existing manifest hash matches live |
|---|---|:---:|
| Base | `1193528982f4ac0c0b707ce36fd7dc03a0ef6f3e1a432deb886dce2e90c300c0` | yes |
| Seed 42, checkpoint 200 | `f1ef3557fec811c00e75615761cb69846928f35d9c69b46174cc736de7c73142` | no |
| Seed/data 43, checkpoint 75 | `65ec7bfc908e1332bdaf7de4c0bef4adb7a8cb53d41f18028986244f255714a3` | no |

The new `pre_m2_followup_v1` provenance manifest records the live paths, sizes, hashes, and the
mismatch explicitly. The old frozen manifests were not overwritten. This wave used the actual
distinct weight files above.

## 3. Execution

Implementation commits on `corpus-update`:

- `5c30813`: Phase 0 contract, probe registry, evaluator, tests, and HU launcher;
- `e529095` through `9a1365d`: paired statistics, robust intersections, live hash audit,
  repeatability audit, and final-answer EOS summaries.

HU jobs:

| Job | Purpose | State | Runtime |
|---:|---|---|---:|
| `405895` | storage preflight | completed, exit 0 | 00:00:19 |
| `405896` | one-probe base GPU smoke | completed, exit 0 | 00:02:30 |
| `405897` | full base frozen suite | completed, exit 0 | 00:12:26 |
| `405898` | seed-42 checkpoint-200 suite | completed, exit 0 | 00:11:48 |
| `405899` | seed/data-43 checkpoint-75 suite | completed, exit 0 | 00:14:03 |
| `405900` | hashes, paired statistics, repeatability, storage audit | completed, exit 0 | 00:02:47 |
| `405901` | final-answer EOS compact summary | completed, exit 0 | 00:00:20 |

All high-volume output remained under `/vol/tmp2/yesildau/pre_m2_followup_v1`. HU home usage was
`8.0G` before and after the wave. The GPU-job stderr files contained only non-fatal Transformers
deprecation and weight-loading progress output; no runtime exception occurred.

## 4. WP1A - Frozen Multi-Paraphrase Result

### Aggregate top-1

| Model | All 3,000 | Form A | Form B | Form C | Direct | QA scaffold |
|---|---:|---:|---:|---:|---:|---:|
| Base | 38 | 12/1,000 | 11/1,000 | 15/1,000 | 17/1,500 | 21/1,500 |
| Seed 42 cp200 | 2,882 | 975/1,000 | 977/1,000 | 930/1,000 | 1,428/1,500 | 1,454/1,500 |
| Seed/data 43 cp75 | 2,807 | 978/1,000 | 963/1,000 | 866/1,000 | 1,387/1,500 | 1,420/1,500 |

Form A and Form B are effectively tied for seed 42. Form C is reliably harder:

- seed 42 direct: A-C `+4.8` points, 95% paired bootstrap CI `[+2.2,+7.6]`, exact McNemar
  `p=0.000536`;
- seed 42 QA: A-C `+4.2` points, CI `[+2.0,+6.4]`, `p=0.000508`;
- seed 43 direct: A-C `+11.6` points, CI `[+8.4,+14.8]`, `p=1.81e-12`;
- seed 43 QA: A-C `+10.8` points, CI `[+7.8,+13.8]`, `p=2.59e-13`.

Seed 43 also shows a small directional A-over-B gap in direct format: `+2.6` points, CI
`[+0.4,+4.8]`, exact McNemar `p=0.04096`. The QA A/B gap is not distinguishable in this suite.

This is frozen-model prompt difficulty, not the causal effect of training on A versus B. That
causal question remains WP1B.

### Required A/B four-cell intersection

This stricter count requires each fact to be top-1 under Form A direct, Form A QA, Form B direct,
and Form B QA.

| Relation | Seed 42 | Seed/data 43 |
|---|---:|---:|
| `profession` | 94/100 | 83/100 |
| `born_in` | 88/100 | 91/100 |
| `lives_in` | 87/100 | 87/100 |
| `field_of_study` | 98/100 | 98/100 |
| `works_in_industry` | 99/100 | 98/100 |
| **All facts** | **466/500** | **457/500** |

Both frozen M1 runs remain above the precommitted 70% robust threshold globally and for every
relation across the two required A/B forms.

### Diagnostic A/B/C x direct/QA intersection

Form C is diagnostic in this first pilot. Requiring all six cells gives:

| Relation | Seed 42 | Seed/data 43 |
|---|---:|---:|
| `profession` | 80/100 | 55/100 |
| `born_in` | 88/100 | 90/100 |
| `lives_in` | 66/100 | 61/100 |
| `field_of_study` | 97/100 | 96/100 |
| `works_in_industry` | 98/100 | 94/100 |
| **All facts** | **429/500** | **396/500** |

The aggregate result remains strong, but the diagnostic exposes seed-sensitive weaknesses in
`profession` and persistent hard city binding in `lives_in`. These cells must not be hidden by
the global average.

## 5. WP4 - Hard-Failure Taxonomy

| Model | Correct | Same-subject relation swap | Other prompt-form failure | Early-EOS failure |
|---|---:|---:|---:|---:|
| Base | 38 | 21 | 830 | 2,111 |
| Seed 42 cp200 | 2,882 | 78 | 40 | 0 |
| Seed/data 43 cp75 | 2,807 | 95 | 93 | 5 |

For seed 42, 63 of 78 same-subject swaps occur on `lives_in`; for seed 43, 84 of 95 occur on
`lives_in`. Harder paraphrases therefore recover the same scientifically meaningful weak point
that was nearly invisible in the original direct/QA aggregate.

Both M1 runs survive the harder frozen suite on the required A/B forms. The seed-43 model is more
sensitive to the novel Form C syntax, especially for `profession`. WP1B crossed subject-form
cells do not yet exist and must not be claimed from this wave.

## 6. WP2 - Teacher-Forced Token Likelihood

The evaluator wrote one raw record per answer token and per EOS position for the gold candidate,
best incorrect candidate, and applicable same-subject city object. EOS is excluded from the
reported answer-NLL metric and recorded separately.

Gold-candidate aggregate:

| Model | First-answer-token NLL | Mean answer NLL | EOS-after-prompt NLL | Final EOS NLL |
|---|---:|---:|---:|---:|
| Base | 10.9412 | 9.0048 | 7.3285 | 5.2213 |
| Seed 42 cp200 | 0.1364 | 0.0877 | 12.9515 | 0.0006 |
| Seed/data 43 cp75 | 0.3416 | 0.2091 | 12.9157 | 0.0006 |

Interpretation:

- before the answer, both M1 models strongly prefer the gold answer token over immediate EOS;
- after the complete gold answer, both assign almost unit probability to EOS;
- this is direct likelihood evidence for the learned short-answer stopping policy;
- it does not by itself prove that EOS supervision caused all WikiText perplexity drift.

The causal attribution still requires WP5's `supervise_eos: true/false` ablation under a fixed LR
and training recipe.

## 7. Decision For The Next Wave

The frozen-checkpoint wave is accepted as complete:

- data, assignment, prompt-overlap, model-path, live-weight, tokenizer, and repeatability checks
  passed under the new provenance record;
- both selected M1 runs generalize strongly to required A/B paraphrases;
- Form C exposes a real seed-sensitive difficulty rather than a universal `497/500` story;
- same-subject `lives_in` swaps remain the dominant hard relation-binding failure;
- teacher-forced likelihood localizes the EOS effect to the end of short answers.

This is **not** a pre-M2 GO decision. Required next work remains:

1. WP1B counterbalanced A/B training and swap replication;
2. WP3 four-relation joint-capture fixture and 400-fact experiment;
3. WP5 controlled LR sweep and EOS-supervision ablation;
4. final GO / GO WITH LIMITATION / HOLD synthesis.

## 8. Artifacts

HU roots:

```text
/vol/tmp/yesildau/transfer-vs-relearning/artifacts/pre_m2_followup_v1/
/vol/tmp2/yesildau/pre_m2_followup_v1/
```

Key compact outputs:

```text
manifests/provenance.json
manifests/integrity_audit.json
evaluations/{base,seed42,seed43}/hard_suite_per_fact.csv
evaluations/{base,seed42,seed43}/teacher_forced_per_token.csv
comparison/accuracy_with_bootstrap_ci.csv
comparison/paired_form_comparisons.csv
comparison/robust_intersections.csv
comparison/token_likelihood_summary.csv
comparison/answer_sequence_likelihood_summary.csv
comparison/repeatability_audit.json
comparison/comparison_manifest.json
```
