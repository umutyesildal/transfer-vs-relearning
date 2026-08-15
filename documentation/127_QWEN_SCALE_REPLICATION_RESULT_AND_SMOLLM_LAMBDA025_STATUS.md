# 127 — Qwen Scale Replication Result and SmolLM Lambda-0.25 Status

**Date:** 29 July 2026  
**Status:** Qwen 2,500-fact replay result replicated across seed 42 and 43; SmolLM lambda-0.25 training complete, held-out evaluation pending recovery.

## 1. Decision

Qwen2.5-1.5B clean-English replay has now passed the full factual-robustness/PPL/integrity gate in two independent 500-subject / 2,500-fact runs. The frozen per-run rule is to choose the earliest checkpoint passing every gate. It selects seed-42 step 75 and seed-43 step 50. This is a replicated intermediate-scale M1 candidate, subject to selected-artifact manifest/SHA-256 freezing and the project’s remaining causal-stage authorization.

SmolLM lambda-0.25 is an exploratory remediation, not a competing selected model yet. Training completed and produced separate LM/ranking loss aggregates; its frozen held-out evaluation must be recovered before interpretation.

## 2. Frozen evaluation completeness

The Qwen seed-43 array `437144_[0-10%3]` completed its 11 checkpoint tasks. Each checkpoint has:

- 2,500 exact-prefix probes;
- 20,000 A/B/C/D × direct/QA hard probes;
- per-relation eight-cell intersections and same-subject binding forced choice;
- matched WikiText-2 test PPL and 30 generic completions.

The frozen WikiText token-stream hash is identical to the seed-42/base protocol:
`be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f`.

## 3. Selected-checkpoint comparison

Base Qwen PPL is 14.699 under this protocol. Corrected primary integrity treats decoded output with a Unicode letter or number as non-empty; the old <=2-token diagnostic remains reported as a sensitivity.

| Metric | Seed-42 selected step 75 | Seed-43 selected step 50 |
|---|---:|---:|
| Exact primary top-1 | 99.96% | 99.68% |
| Hard top-1 | 19,858/20,000 (99.29%) | 19,845/20,000 (99.225%) |
| Eight-cell robust | 2,402/2,500 (96.08%) | 2,405/2,500 (96.20%) |
| Minimum robust relation | profession 441/500 (88.2%) | profession 451/500 (90.2%) |
| Minimum relation-form cell | profession / C / direct 442/500 (88.4%) | all-cell minimum remains above 80%; robust minimum 90.2% |
| Relation forced choice | 7,961/8,000 (99.51%) | 7,965/8,000 (99.56%) |
| WikiText-2 PPL | 15.909 | 15.169 |
| PPL/base ratio | 1.082 | 1.032 |
| Synthetic-subject intrusion | 0/30 | 0/30 |
| Length-only near-empty sensitivity | 2/30 | 2/30 |
| Generic-completion top-1 | 29/30 | 29/30 |

Seed-43 step 75 also passes all principal factual and PPL gates (exact 99.96%, hard 99.36%, robust 96.28%, PPL 15.475 / ratio 1.053), but is not selected because the frozen rule chooses step 50 first. Seed-43 step 50 passes exact, all cell, robust, binding, PPL, and corrected-integrity requirements. The two length-flagged short answers require no new threshold: under the pre-existing corrected rule they are lexical rather than empty outputs.

## 4. Interpretation

This answers the scale question: the Qwen replay recipe is not merely a seed-42 anomaly. At 2,500 facts it reproduces near-ceiling exact acquisition, prompt-robust retrieval, same-subject relation binding, and low PPL drift in seed 43. The selected checkpoint varies by seed (75 versus 50), which is expected under the per-run earliest-passing rule and does not constitute post-hoc selection.

This result does not license claiming that the Turkish transfer-versus-relearning question is answered. It supplies the replicated English M1 candidate that the later controlled Turkish stages require. Before M2/M3, freeze the two selected model-only artifacts with manifests/SHA-256 and document their retention decision.

## 5. SmolLM lambda-0.25 training result

Job `437152` completed 36 epochs / 252 updates on A100-80GB. It uses the same matched 100-subject/500-fact dataset hashes as the prior treatment/control and changes only the exploratory ranking coefficient from 0.10 to 0.25.

| Training diagnostic | Value |
|---|---:|
| Runtime | 35,439.26 s (9 h 50 m 39 s) |
| Final validation loss | 0.0002092 |
| Aggregate Trainer loss | 46.4815 |
| Mean factual LM loss | 0.772417 |
| Mean ranking loss | 0.628855 |
| Contrastive coefficient | 0.25 |
| Train batches | 12,600 |

The separate loss file validates the new logger. Aggregate training loss remains unsuitable for cross-objective model selection. The held-out final-model evaluation was not submitted successfully in its first attempt: no evaluation root or Slurm job was created, so no partial result or artifact exists to interpret. The next operation is a narrow launcher/preflight diagnosis followed by exactly one recovered evaluation submission, expected 60–90 minutes after A100 allocation.

## 6. Next controlled actions

1. Create manifests and SHA-256 checksums for Qwen seed-42 step-75 and seed-43 step-50 selected model-only artifacts; retain them on scratch.
2. Repair and submit the missing SmolLM lambda-0.25 held-out evaluation. If it remains below the robust gate, end the SmolLM remediation branch rather than opening seed 43 or scale-up.
3. Update the master handoff before opening any M2/M3 work; M2/M3 remain HOLD until selected-artifact freezing is complete.

## 8. Selected Qwen artifacts frozen — 29 July 2026

The replicated selected checkpoints are now frozen as model-only artifact records on approved
scratch. No checkpoint tree was copied, overwritten, or deleted; the compact manifests bind the
selected checkpoint, training manifest, evaluation root, and hashes/sizes of model weights,
configuration, and tokenizer files.

| Seed / selected step | Manifest root | Manifest SHA-256 |
|---|---|---|
| Seed 42 / step 75 | `/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75` | `aed52ff8baeb01b89efef443caa560b707871dfe52fde6bcec1d8ae3e46fb032` |
| Seed 43 / step 50 | `/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50` | `af3569aae2bd8066f51bb0ff1fecd4eec13eb74b5ba794915eae565f13f8bd53` |

Each root contains `selected_artifact_manifest.json` plus its checksum sidecar. This completes the
selected-artifact freezing prerequisite. Retention remains scratch-only; cleanup of duplicate
optimizer/trainer checkpoints is a separate later decision and was not performed here.

### 8.1 Approved HU-home durability copy — 30 July 2026

The preceding scratch-only retention statement is superseded for the two selected Qwen models
only. Ralf Moritz confirmed in writing that current HU-home use below 30 GB is acceptable and
explicitly authorized copying the additional approximately 6.2 GB from `/vol/tmp2` into home.
He also confirmed that the temporary filesystems have no backup or retention guarantee.

Commit `81d45f6db1b87313927b87bb9c697b13d542cc63` adds a fail-closed archival procedure. CPU job
`439465` completed on `gruenau` in 9 minutes 39 seconds with exit code 0 and empty stderr. It
copied only the two selected full-model weights, their configs, the shared pinned tokenizer, and
compact source manifests; it did not copy optimizer/trainer state or any other checkpoint.

The verified durability copy is:

`/vol/fob-vol6/mi25/yesildau/frozen-models/qwen_m1_selected_v1`

Its `archive_manifest.json` has SHA-256
`29098e221dd1be47a68fecc35a430c6784acc807e4ff5a04b1eda7c95a2980d8`. The archive reports status
`frozen_home_backup_verified`, source payload 6,186,456,274 bytes, and the frozen seed-42 step-75
and seed-43 step-50 model hashes. The final tree occupies approximately 5.8 GiB; post-copy total
home use is approximately 14 GiB, below the explicitly approved 30-GB ceiling. No partial archive
directory remains. Scratch originals remain untouched and no cleanup is authorized by this copy.

## 7. SmolLM lambda-0.25 held-out result and branch decision — 29 July 2026

Recovery evaluation job `439147` completed successfully. Its stderr contains only three model-load
deprecation/progress sequences; there is no traceback, OOM, NaN, or Inf. All 500 exact probes and
all 4,000 hard probes completed. The result falsifies the working lambda-increase hypothesis:
increasing lambda from 0.10 to 0.25 improves same-subject forced choice slightly, but does not
improve prompt-robust retrieval and increases PPL slightly.

| Metric | `lambda=0` control | `lambda=0.10` | `lambda=0.25` |
|---|---:|---:|---:|
| Exact primary top-1 | 100.0% | 100.0% | 100.0% |
| Hard top-1 | 87.525% | **91.00%** | 90.975% |
| Eight-cell robust | 39.6% | **52.2%** | 50.4% |
| Same-subject forced choice | 89.4% | 93.1% | **94.1%** |
| Robust profession | 21% | **34%** | 32% |
| WikiText-2 PPL | 17.1980 | **17.5234** | 17.5521 |
| Empty / synthetic intrusion | 0 / 0 | 0 / 0 | 0 / 0 |

Lambda-0.25 relation-level robust counts are born-in 61, field-of-study 63, lives-in 52,
profession 32, and works-in-industry 44 out of 100; its hard failure taxonomy is 262 prompt-form
failures, 79 relation swaps, and 20 early-EOS preferences. It therefore remains well below the
70% robust gate, with profession Form-C-style access unresolved. The separate loss logger worked
as intended (mean factual LM loss 0.772417, mean ranking loss 0.628855 across 12,600 batches),
but this provides diagnosis rather than a model-selection benefit.

**Decision:** Stop the SmolLM contrastive remediation branch at this point. Do not run SmolLM seed
43 or 2,500-fact scale-up. Retain the lambda-0.10/control/lambda-0.25 compact evidence as negative
methodological evidence; Qwen is the sole replicated intermediate-scale M1 candidate pending
artifact freezing.
