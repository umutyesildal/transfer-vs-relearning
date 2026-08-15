# 102 - M1 Form-Generalization Remediation Result

**Date:** 2026-07-19

**Status:** Seed-42 discovery complete. Balanced A+B improves observed-form access but fails the frozen unseen-form, robust-intersection, and exact-prefix gates. M2 remains **HOLD**.

**Parent plan:** `101_M1_FORM_GENERALIZATION_REMEDIATION_PLAN.md`

## 1. Decision

The seed-42 discovery decision is **FAIL / do not replicate / do not scale**. Seed 43, the 500-subject scale control, final M1, M2, and M3 are not authorized.

This is scientific evidence, not an infrastructure failure. The initial evaluation wave completed hard-form and exact-prefix stages, then its generic-retention stage failed because a CRLF terminator from the CSV registry was included in the config path. Commit `1e1a397` strips that terminator. The generic-only retry completed without recomputing hard or exact outputs.

## 2. Frozen Design

Both conditions used the Relation V2 100-subject/500-fact population, SmolLM2-1.7B, answer-only loss, LR `5e-5`, `supervise_eos: false`, 36 epochs, effective batch 500, and 252 updates. Each had 3,500 training rows, 500 validation rows, seven rows per fact, and four direct plus three QA rows per fact.

| Condition | Curriculum | Training-form rows |
|---|---|---:|
| Control | One subject-assigned A or B form | A 1,750 / B 1,750 |
| Balanced A+B | Every fact sees A and B under both scaffolds | A 1,750 / B 1,750 |

The frozen factual suite contained Forms A/B/C/D under direct and QA scaffolds (4,000 probes). C and D never occurred in training. Exact-prefix retained 500 canonical English probes; generic retention used frozen WikiText-2 plus the 30 generic prompt/completion controls.

## 3. Execution And Storage Audit

Preflight job `408068` passed: HU home was 8,295,580 KiB (about 7.91 GiB, under the 10 GiB boundary), `/vol/tmp2` had 117 TB free and 3% inode usage, all high-volume paths resolved to scratch, and both output namespaces were absent.

| Job | Purpose | Node / GPU | Runtime or result |
|---:|---|---|---|
| 408069 | control training | gruenau9 / 1x A100 80 GB | 2,594 s (43m14s), manifest `complete` |
| 408070 | balanced A+B training | gruenau9 / 1x A100 80 GB | 2,622 s (43m42s), manifest `complete` |
| 408071_0,1 | hard + exact + initial generic | gruenau9 / 1x A100 each | hard/exact complete; generic path parsing failed |
| 408357_0,1 | generic-only retry | gruenau9 / 1x A100 each | completed |

All datasets, checkpoints, models, raw evaluation output, caches, and logs remained under `/vol/tmp2/yesildau/m1_form_generalization_v1` or an approved scratch symlink. Training post-run logs reported home at 8.0G; the only home files above 500 MB were known Conda libraries.

Final model-only SHA-256:

| Condition | SHA-256 |
|---|---|
| Control | `5bef2887090f508a920cf8570d52e75b46db05e99ab05ddfc5d125358f9c03dd` |
| Balanced A+B | `8ea7cee93ad38fc1d7056bffd909e051343c29f6903868633ad5f09ff239d770` |

## 4. Frozen Results

| Metric | Control | Balanced A+B | Required |
|---|---:|---:|---:|
| Four-form top-1 | 1,819/4,000 (45.5%) | 2,994/4,000 (74.9%) | — |
| Exact-prefix top-1 | 40/500 (8.0%) | 47/500 (9.4%) | ≥90% |
| Eight-cell robust intersection | 7/500 (1.4%) | 59/500 (11.8%) | ≥70% |
| Relation-swapped forced choice | 1,088/1,600 (68.0%) | 1,305/1,600 (81.6%) | diagnostic |

| Form/scaffold | Control | Balanced A+B |
|---|---:|---:|
| A direct | 58.6% | 100.0% |
| A QA | 65.6% | 100.0% |
| B direct | 62.8% | 100.0% |
| B QA | 65.4% | 100.0% |
| C direct (held out) | 26.2% | 46.6% |
| C QA (held out) | 29.8% | 52.2% |
| D direct (held out) | 19.6% | 37.6% |
| D QA (held out) | 35.8% | 62.4% |

Balanced A+B produces a +29.4-point aggregate four-form improvement and perfect A/B access, but no held-out C/D cell reaches 80%. The global eight-cell intersection is far below 70%, so no per-relation robust gate can pass.

## 5. Generic Retention

Base WikiText-2 PPL is 15.924. Both models remain inside the preferred PPL-ratio band and show no EOS/generation collapse.

| Metric | Control | Balanced A+B |
|---|---:|---:|
| WikiText-2 PPL | 16.535 | 16.581 |
| PPL ratio | 1.038 | 1.041 |
| Generic completion ranking | 30/30 | 30/30 |
| Generic EOS endings | 0/30 | 0/30 |
| Empty/near-empty generations | 0/30 | 0/30 |

## 6. Frozen Evidence Hashes

Evaluation registry: `bc8040b3520dbbd6d467a8e6302308713568902e972a0ab2fffe2ea1cfa62212`.
Evaluation manifest: `0f5b503b20e6ec191ff0a8e68b92634429ed91aa5ec717dafd578d978fa88d34`.

| Artifact | Control | Balanced A+B |
|---|---|---|
| Hard-suite summary | `e576ae6a4b3c6398857a8186b07e6aabfac6fbef8ed5a2cdb996a08708e21851` | `c7b4b86cd226c2e99c007002223c0dbedbf6ea091f0121f8bf88b0369001c281` |
| Eight-cell CSV | `65ceb6e427850fa6144a0cca833f6f65c317514f470f0b2e21aaf286a7a304ec` | `2e09e757a282a6c310097bfc1fa153dab798c073a54dd9bccb9f5903529d2d6e` |
| Exact summary | `5d71e987e10b7b198c984765c66fed50531a652522eddc5a2a099ab933e1f0da` | `70975d6283a4b22f0a6e83c52910ce88ccaa0c0981a8f2803a083d72e42f8222` |
| Generic summary | `056068a429990066a36d4d7af98a9cdba627a721f2ef4d120079ece8a37ba73e` | `f1f12637fafca2fdc18540820ba5227e6b239d43512ce2cf8858d56019f3f26e` |

## 7. Interpretation And Next Decision

Balanced A+B exposure removes the observed A/B access asymmetry but does not create a representation from which unseen C/D wording retrieves the fact. The weak exact-prefix result additionally shows that the current question-answer curriculum does not reproduce the canonical direct acquisition probes.

The next numbered plan must hold rows, answer-token exposure, updates, and generic-retention controls fixed while testing a genuinely different representation, objective, or broader matched prompt-diversity intervention. It must explicitly represent the exact-prefix probes during acquisition while retaining distinct unseen forms. Do not add repeated A/B exposure, run Seed 43, scale, or start M2/M3.
