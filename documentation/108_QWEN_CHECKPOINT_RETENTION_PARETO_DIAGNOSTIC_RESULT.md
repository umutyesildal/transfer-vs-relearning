# 108 - Qwen Checkpoint Retention Pareto Diagnostic Result

**Date:** 2026-07-19  
**Status:** Complete; no retained checkpoint passes every frozen gate. No checkpoint is nominated.
Seed 43, scale-up, final M1, M2, and M3 remain **HOLD**.

**Parent plan:** `107_QWEN_CHECKPOINT_RETENTION_PARETO_DIAGNOSTIC_PLAN.md`

## 1. Decision

The frozen exploratory checkpoint diagnostic is **FAIL / no endpoint nomination**. Qwen's generic
PPL drift is already above the hard limit at update 25, before factual acquisition passes all
gates. At update 50 the factual and prompt-robustness gates pass, but PPL ratio is already 1.455.
There is no retained early-stopping checkpoint that combines required factual robustness with PPL
ratio at or below 1.25.

This rules out checkpoint selection as the solution to Qwen's retention problem; it does not
invalidate Qwen's unusually strong prompt robustness. The next admissible work is a separately
frozen Qwen retention intervention. No threshold relaxation or seed-43 run is authorized.

## 2. Frozen design and execution

The diagnostic evaluated the completed Document 106 Qwen seed-42 run at updates
`25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252`. Every checkpoint received the same 500
exact-prefix probes, 4,000 Form A/B/C/D probes, true eight-cell intersection, relation-binding
checks, frozen WikiText-2 PPL, and 30 generic controls.

- Final implementation/HU commit: `826ebb352203ae5cae3fa5d6c23d4abbd145ba5e`.
- Authoritative HU test suite: 172/172 passed.
- Passing family preflight: `410128`.
- Completed evaluation array: `410129_[0-10%3]`, maximum three concurrent tasks.
- GPU: one NVIDIA A100 80GB PCIe per task; `gruenau10` was excluded. Tasks 0--2 were directly
  verified on `gruenau9`; later task-node history was unavailable after completion because SlurmDBD
  remained unavailable.
- Evaluator-manifest task durations: approximately 18m09s--18m59s.
- Family evaluator window: 15:37:29--16:53:09 UTC, approximately 75m40s.

All eleven tasks produced complete hard, exact, and general-capability summaries. Their stderr
files contain model-loading progress and a Transformers `torch_dtype` deprecation warning, not a
fatal scientific/runtime error. Slurm accounting could not be queried because HU's Munge/SlurmDBD
service returned its known authentication error; completion is established by absence from
`squeue`, 11/11 expected result triples, and completed evaluator manifests.

## 3. Corrected frozen results

“Robust global/min” is the true eight-cell intersection from `all_cell_intersections.csv`: a fact
must be correct under all four forms and both scaffolds. An initial compact summarizer version used
the per-scaffold four-form file; commit `826ebb3` corrected this before the result was accepted and
added a regression test.

| Update | Exact | Min A/B | Min C/D | Robust global/min | PPL | PPL ratio | All gates |
|---:|---:|---:|---:|---:|---:|---:|---|
| 25 | 88.6% | 79% | 68% | 76.2% / 63% | 20.715 | 1.409 | FAIL |
| 50 | 99.8% | 100% | 97% | 99.2% / 97% | 21.384 | 1.455 | FAIL PPL |
| 75 | 100% | 100% | 99% | 99.4% / 98% | 21.424 | 1.458 | FAIL PPL |
| 100 | 100% | 100% | 99% | 99.6% / 99% | 21.434 | 1.458 | FAIL PPL |
| 125 | 100% | 100% | 99% | 99.6% / 99% | 21.443 | 1.459 | FAIL PPL |
| 150 | 100% | 100% | 99% | 99.6% / 99% | 21.451 | 1.459 | FAIL PPL |
| 175 | 100% | 100% | 99% | 99.6% / 99% | 21.455 | 1.460 | FAIL PPL |
| 200 | 100% | 100% | 99% | 99.6% / 99% | 21.461 | 1.460 | FAIL PPL |
| 225 | 100% | 100% | 99% | 99.6% / 99% | 21.469 | 1.461 | FAIL PPL |
| 250 | 100% | 100% | 99% | 99.6% / 99% | 21.475 | 1.461 | FAIL PPL |
| 252 | 100% | 100% | 99% | 99.6% / 99% | 21.472 | 1.461 | FAIL PPL |

The frozen base PPL is `14.698839`. Every checkpoint reproduced token-stream SHA-256
`be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f`. All checkpoints had
29/30 generic-completion top-1, zero empty/near-empty generations, and zero synthetic-subject
intrusions. The hard failure is specifically matched generic-language likelihood drift, not empty
generation or leakage.

Update 252 materially reproduces Document 106: exact 100%, hard top-1 99.925%, minimum C/D 99%,
robust global/min 99.6%/99%, and PPL ratio 1.460779. This closes the wave-integrity check.

## 4. Interpretation

The factual/retention curves do not cross inside the retained checkpoint grid:

- update 25 still fails exact, minimum A/B, minimum C/D, and minimum-relation robustness, while
  PPL has already exceeded 1.25 by a large margin;
- update 50 is the earliest checkpoint passing every factual and robustness gate, but its PPL ratio
  is 1.455;
- later exposure improves or saturates factual robustness without materially changing the already
  elevated PPL band.

Qwen's retention cost is an early optimization effect, not merely late overtraining. Early stopping
cannot repair it. A new controlled experiment must change the training objective or curriculum to
preserve base-language behavior while keeping fact exposure and evaluation fixed. General-language
replay and explicit base-retention regularization are admissible mechanisms to compare in the next
plan; their weights must be frozen before training.

## 5. Storage and artifact audit

The mandatory coordinated-family post-run audit recorded:

- HU home: 8.0 GiB;
- `/vol/tmp2`: 115 TiB available, 18% used, 3% inode use;
- `/vol/tmp`: 19 TiB available, 87% used, 3% inode use;
- result family: 198 MiB under `/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1`;
- `runs` and `artifacts` resolve to `/vol/tmp/yesildau/...`, and the diagnostic root resolves to
  `/vol/tmp2/yesildau/...`;
- no new experiment artifact above 500 MiB appeared in home; the three reported large files are
  known PyTorch/CUDA libraries in the Conda environment.

Current compact artifact SHA-256 values after corrected summarization are:

| Artifact | SHA-256 |
|---|---|
| `qwen_checkpoint_pareto_summary.csv` | `3a3c3c0ae36470d07589209ce9b112061b97528a0270d33e5eac2e82b90314eb` |
| `qwen_checkpoint_pareto_summary.json` | `2479eb560ee3c6575d371721ca386c2e2dd3c79c53abd479088b83d8e2e68264` |
| `checkpoint_registry.csv` | `52e63f7967d713486f820d9fa5abff5b303bc9fda3ed4acbc4ff0bbbc91907e2` |
| `wave_manifest.json` | `d8268cc30bb847e72008cc571c3e2285f3854ede129bca50c5fefb75e905f5b0` |

No checkpoint or selected/frozen artifact was deleted. The Document 106 Qwen endpoint and StableLM
backup remain preserved. Intermediate Qwen checkpoints remain cleanup candidates only after the
next retention plan no longer needs them and retained evidence is reverified.

## 6. Next decision

Create Document 109 as a controlled, matched Qwen retention-intervention plan. It must precommit:

1. one primary retention mechanism and, if scientifically justified, one bounded comparator;
2. unchanged 100-subject/500-fact population and hybrid factual curriculum;
3. matched factual exposure, optimizer/update budget, endpoint rule, and frozen evaluators;
4. the generic replay corpus or retention-anchor set, contamination audit, token budget, and
   mechanism coefficient before training;
5. unchanged factual and PPL gates, with seed 42 discovery before seed 43 replication.

Until that plan is frozen and passes implementation/preflight gates, no new training is authorized.
