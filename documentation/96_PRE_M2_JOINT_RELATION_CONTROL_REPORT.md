# 96 - Pre-M2 Joint Relation Control Report

**Date:** 2026-07-18  
**Status:** WP3 Stage A completed; relation distinction positive, prompt-robustness gate failed  
**Parent plan:** `93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md`  
**Previous wave:** `95_PRE_M2_PARAPHRASE_COUNTERBALANCE_REPORT.md`

## 1. Scope And Frozen Decision

WP3 asks whether one SmolLM2-1.7B model can learn both members of each education and employment
relation pair for the same subject. Stage A is frozen at 100 subjects with all four relations per
subject:

- `studied_at` versus `field_of_study`;
- `works_at` versus `works_in_industry`.

This gives 400 facts, 2,800 acquisition rows, 400 validation rows, and 2,400 evaluation probes.
Ordinary within-relation candidate ranking is supplemented by a same-subject relation-swapped
forced choice in both directions. The final interpretation must retain the limitation that the
four answer families have naturally different semantic types.

## 2. Fixture And Integrity Evidence

The precommitted 10-subject fixture was generated before the full Stage A launch. It contains 40
facts, 280 training rows, 40 validation rows, and 240 probes. Automated exhaustive inspection
checked all 560 generated records against the frozen semantic contract:

- every subject has each relation exactly once;
- every fact has seven exposures and six probes;
- every prompt, answer, exposure index, scaffold, and form matches its template;
- every hard negative is the paired relation's object for the same subject;
- the expected answer and hard negative never normalize to the same string;
- normalized train-prompt overlap occurs only in the predeclared seen-form cell; and
- probe IDs are unique.

Both the fixture and the full 100-subject dataset passed their integrity audits. The A/B assignment
has 50 subjects per group. The maximum absolute difference across branch, name, popularity, and
all four relation-frequency features is one.

Representative two-way hard pairs from the frozen fixture are:

| Prompt | Gold | Same-subject swapped negative |
|---|---|---|
| Where did Mumun Asıg study? | University of Surrey | computing |
| What did Mumun Asıg study? | computing | University of Surrey |
| Where does Mumun Asıg work? | Chipotle Mexican Grill | insurance |
| In which industry does Mumun Asıg work? | insurance | Chipotle Mexican Grill |

The complete local test suite passed with four expected skips. The targeted HU suite passed all
12 tests after regenerating the frozen datasets on scratch.

## 3. Frozen Training And Evaluation Contract

The implementation is commit `a5c2aa1` on branch `corpus-update`. The Stage A recipe retains the
WP1B 1.7B answer-only recipe while changing the fact graph and effective-batch decomposition:

| Item | Frozen value |
|---|---:|
| Subjects | 100 |
| Relations per subject | 4 |
| Facts | 400 |
| Train / validation rows | 2,800 / 400 |
| Epochs | 36 |
| Micro-batch / accumulation | 10 / 40 |
| Effective batch | 400 |
| Optimizer updates | 252 |
| Learning rate | `1e-4` |
| Objective | answer-only, supervised EOS |
| Checkpoint upper bound | 11 |
| Estimated retained run-family upper bound | 225 GB on scratch |

Frozen Stage A gates are 360/400 aggregate exact, 320/400 on each required held-out form, and
280/400 in the robust intersection. Each relation must be reported independently with thresholds
90/100 exact, 80/100 for each required held-out form, and 70/100 robust.

## 4. HU Storage Preflight And Active Jobs

Before corpus generation and submission:

- HU home usage was `8.0G`;
- `/vol/tmp2` had approximately `118T` available and 3% inode use;
- repository `runs` resolved to `/vol/tmp/yesildau/transfer-vs-relearning/runs`;
- repository `artifacts` resolved to `/vol/tmp/yesildau/transfer-vs-relearning/artifacts`;
- large outputs, model files, caches, logs, launch manifests, and evaluations were routed to
  `/vol/tmp2/yesildau/pre_m2_followup_v1` or the approved scratch-backed artifact symlink.

Completed integrity jobs:

| Job | Purpose | Result | Node |
|---:|---|---|---|
| `406923` | one-batch Stage A forward/backward smoke | passed; loss `5.4117`, 218 gradient tensors, 7.29 GB peak allocation | `gruenau9` |
| `406924` | four-relation base-model evaluator mechanics smoke | passed; 4/4 probes and forced-choice fields emitted | `gruenau9` |

The base model is physically stored on scratch: although an older manifest string contains the
repository path below HU home, `readlink -f` resolves the live weight file to
`/vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/.../model.safetensors`. Its verified
SHA-256 is `1193528982f4ac0c0b707ce36fd7dc03a0ef6f3e1a432deb886dce2e90c300c0`.

After both smoke gates passed, full 252-update Stage A training job `406925` completed on
`gruenau9` in 2,534 seconds (42 minutes 14 seconds). The final monitoring eval loss was
`0.0003241`; the reported run-level train loss was `0.1977`. The run retained approximately
`109G` on scratch, including resumable checkpoints and the final model. HU home remained `8.0G`.
Frozen input hashes include:

| Artifact | SHA-256 |
|---|---|
| Config | `e8ada07c278ef6790811084e614820f6d0219be633242b785655d43edfb5dc37` |
| Stage A manifest | `39e47cb3cacd9283e3e5836f2cb1a5318ce18abbd361a9f46086a560d84b523d` |
| Train JSONL | `f6a04c9e1fbff6777f8657877306e726f5d1ec0799c2435a04e26df760958ac6` |
| Validation JSONL | `90203562c5f8021d1698dba2afde6cb6b6951a1a02ceeffa17db0ece34cc003e` |

The frozen final model is:

```text
/vol/tmp2/yesildau/pre_m2_followup_v1/training/joint_relation_capture/stage_a_100/
  20260718T073303Z_pre_m2_wp3_stage_a_smollm2_1_7b_a29b1e79/final_model
```

Its `model.safetensors` SHA-256 is
`e10f6d4ce0a59a4cccbadc5377f26ff52b1edb7f80d334e6f40ec3ff96621702`. The frozen
model-manifest SHA-256 is `7e02ea91fc2d581ceca4fe3b40a81023a35f6bb874639001ce01effbdf6f8f85`.
Evaluation job `406926` was submitted for all 2,400 probes; its expected duration is 10-15 minutes.

This report will be updated with final metrics, the post-evaluation storage audit, and the WP3
decision when job `406926` completes.

## 5. Frozen Evaluation Result

Evaluation job `406926` completed all 2,400 probes on `gruenau9` in 9 minutes 37 seconds. Stderr
contained only the non-fatal Transformers `torch_dtype` deprecation and model-loading progress.

Ordinary within-relation candidate ranking:

| Relation | Seen | Crossed subject-form | Novel Form C | All probes |
|---|---:|---:|---:|---:|
| `studied_at` | 200/200 | 90/200 | 130/200 | 420/600 |
| `field_of_study` | 200/200 | 95/200 | 112/200 | 407/600 |
| `works_at` | 195/200 | 91/200 | 134/200 | 420/600 |
| `works_in_industry` | 200/200 | 96/200 | 171/200 | 467/600 |
| **All** | **795/800 (99.4%)** | **372/800 (46.5%)** | **547/800 (68.4%)** | **1,714/2,400 (71.4%)** |

The required A/B four-cell robust intersection requires Form A direct, Form A QA, Form B direct,
and Form B QA to all succeed for the same fact:

| Relation | Robust intersection | Threshold |
|---|---:|---:|
| `studied_at` | 32/100 | 70/100 |
| `field_of_study` | 34/100 | 70/100 |
| `works_at` | 30/100 | 70/100 |
| `works_in_industry` | 34/100 | 70/100 |
| **All** | **130/400 (32.5%)** | **280/400 (70%)** |

No relation passes the frozen prompt-robustness gate. This reproduces WP1B's core finding under a
different four-relation fact graph: acquisition is nearly exact under the subject's training form,
but retrieval remains strongly coupled to that form.

Same-subject relation-swapped forced choice gives a different and important result:

| Relation | Forced-choice correct |
|---|---:|
| `studied_at` | 600/600 (100.0%) |
| `field_of_study` | 503/600 (83.8%) |
| `works_at` | 600/600 (100.0%) |
| `works_in_industry` | 545/600 (90.8%) |
| **All** | **2,248/2,400 (93.7%)** |

The model usually prefers the correct relation-specific object over the same subject's paired
object. This is evidence for relation distinction, but it is not evidence for fully robust
retrieval: institution versus field and employer versus industry have different semantic answer
types, which can make the forced choice easier. Surface-name controls remain outside the frozen
plan.

Failure taxonomy: 1,714 correct, 553 prompt-form failures, and 133 early-EOS failures.

## 6. Decision And Next Wave

Dataset, evaluator, GPU smoke, training, and storage integrity are **PASS**. Relation distinction
is positive under the required same-subject forced choice. The ordinary prompt-robustness gate is
**FAIL**, so WP3 does not remove the current pre-M2 HOLD.

Conditional Stage B is not activated. Stage A already answers the relation-pair question, while
adding three more relations would enlarge the fact graph without isolating the reproduced
subject-form failure. The next precommitted wave is WP5's controlled learning-rate sweep followed
by the EOS ablation.

## 7. Frozen Artifacts And Post-Run Audit

Evaluation output size is approximately `18M`; the training family retains approximately `109G`
on scratch. HU home remained `8.0G` after both jobs. `/vol/tmp2` retained approximately `118T`
available with 3% inode use.

| Artifact | SHA-256 |
|---|---|
| Final `model.safetensors` | `e10f6d4ce0a59a4cccbadc5377f26ff52b1edb7f80d334e6f40ec3ff96621702` |
| Frozen model manifest | `7e02ea91fc2d581ceca4fe3b40a81023a35f6bb874639001ce01effbdf6f8f85` |
| Probe registry | `c00a7298dc2c96eaf5bf51442789f5307f5ccb6f04ca5713e6b7e985b55dc479` |
| Per-fact CSV | `8b26ed966d5e25857d91e92e28eef50ff645715bc453028fbf69c8e4527e332d` |
| Per-token CSV | `590a05ba762060dea9c71c8419c0838919392f281031feeaffc0fdb63faa275d` |
| Summary JSON | `aeb4880f21748267a5b99da470b65167f9d045f81756acc43ba7ae6163c5af09` |
| Forced-choice CSV | `a594051905299f9463f52279275f13e306940701b4bab0a79eaec6564cd2416a` |
