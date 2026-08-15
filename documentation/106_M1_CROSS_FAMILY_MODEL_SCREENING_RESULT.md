# 106 - M1 Cross-Family Model Screening Result

**Date:** 2026-07-19  
**Status:** Screening complete; no candidate passed every frozen gate. Seed 43, scale-up, final M1,
M2, and M3 remain **HOLD**.

## 1. Frozen question and decision rule

Document 105 asked whether changing the pretrained model family, while retaining the 100-subject /
500-fact, 3,500-row, answer-only, EOS-false, seed-42, update-252 acquisition contract, could solve
the prompt-robustness failure without unacceptable generic-capability drift. The frozen gates were:

| Gate | Requirement |
|---|---:|
| Canonical exact-prefix | >=90% |
| Every trained A/B form/scaffold cell, globally and per relation | >=80% |
| Every held-out C/D form/scaffold cell, globally and per relation | >=80% |
| Eight-cell robust intersection, globally and per relation | >=70% |
| Trained/base generic PPL ratio | <=1.25; preferred <1.10 |
| Integrity/generic behavior | No leakage, relation collapse, empty collapse, or synthetic intrusion |

If no new candidate passed every gate, Document 105 prohibited seed-43 replication, scale-up, or
selection by rank-ordering failed models.

## 2. Valid endpoints

All four pinned families ultimately produced finite update-252 endpoints. StableLM required the
precommitted single-variable BF16-load remediation described in Document 105; its native-FP16 run
is retained as failed numerical evidence and is not evaluated.

| Candidate | Training result | Final train loss | Final eval loss | Endpoint size |
|---|---|---:|---:|---:|
| Qwen2.5-1.5B | Complete; `409429_0`, 01:06:42 | 0.272806 | 0.000153679 | 2.9 GiB |
| Gemma-2-2B | Complete; `409429_2`, about 90.9 min | 0.291064 | 0.000014856 | 9.8 GiB |
| StableLM2-1.6B BF16 remediation | Complete; `410103_1`, 00:53:48 | 0.262179 | 0.000176431 | 3.1 GiB |
| Llama-3.2-1B | Complete retry; `410103_3`, 00:41:01 | 0.242027 | 0.000138720 | 2.4 GiB |

## 3. Frozen evaluation results

Percentages below use the immutable Document 105 evaluators. “Min A/B” and “Min C/D” are the
minimum relation-by-scaffold cell accuracies, not global averages. “Robust global/min” reports the
global eight-cell intersection followed by the minimum per-relation intersection.

| Candidate | Exact | Hard top-1 | Min A/B | Min C/D | Robust global/min | PPL base -> trained (ratio) | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| SmolLM2-1.7B Doc. 104 reference | 100% | 87.50% | 100% | below gate | 39.6% / 21% | 15.924 -> 17.198 (1.080) | FAIL robustness |
| Qwen2.5-1.5B | 100% | 99.925% | 100% | 99% | 99.6% / 99% | 14.699 -> 21.472 (**1.461**) | FAIL PPL only |
| Gemma-2-2B | 97.8% | 93.875% | 85% | **7%** | 78.0% / **7%** | 151.376 -> 106,701.115 (**704.873**) | FAIL C/D, per-relation robustness, PPL |
| StableLM2-1.6B BF16 | 100% | 98.750% | 100% | **69%** | 93.8% / **69%** | 12.586 -> 18.594 (**1.477**) | FAIL C/D, per-relation robustness, PPL |
| Llama-3.2-1B | 100% | 95.425% | 100% | **8%** | 81.4% / **7%** | 15.024 -> 58.023 (**3.862**) | FAIL C/D, per-relation robustness, PPL |

Relation-swapped forced choice was 99.875% for Qwen and 100% for Gemma, StableLM, and Llama.
Qwen's hard-suite failure taxonomy contained only one prompt-form failure and two same-subject
relation swaps. Qwen generic-completion top-1 improved from 27/30 to 29/30, but WikiText-2 PPL and
generation repetition worsened; this does not override the frozen PPL-ratio failure.

## 4. Decision

**No new model passes every frozen gate. No model is promoted.** In particular:

- Qwen is the only new family that passes every factual-storage and prompt-robustness gate, but its
  PPL ratio 1.461 exceeds the hard 1.25 limit.
- StableLM BF16 remediation fixes its numerical failure and gives strong global robustness, but its
  weakest held-out/per-relation cell is 69%, one point below the 70% robust floor and eleven points
  below the 80% held-out-cell floor; its PPL ratio also fails.
- Gemma and Llama store canonical facts but show severe relation-specific held-out failures and
  large generic-language drift.
- SmolLM remains the opposite tradeoff: acceptable retention but inadequate prompt robustness.

The model-family screen therefore exposes a storage/robustness-versus-retention optimization
problem, not a model-access problem. Seed 43, the 500-subject intermediate run, final 5,000-subject
M1, M2, and M3 remain **HOLD**.

Qwen is the closest failed candidate and may be used only as the diagnostic base for a separately
frozen retention-preserving objective/curriculum experiment. This is not a retrospective promotion.
The next plan should not continue model-family fishing. It should precommit a controlled Qwen
comparison that changes one retention mechanism—such as frozen general-language replay or an
explicit base-model retention regularizer—while preserving fact exposure, update/checkpoint rules,
prompt curriculum, evaluators, and the same PPL/factual gates.

## 5. Operational record and failures

Important Slurm evidence retained by Document 105 includes:

- acquisition: failed preflight `409082`, canceled dependent `409083`, successful four-model array
  `409084_[0-3]`;
- first training wave: `409088` PASS, invalid array `409089` due shared blank-label config race;
- corrected training: `409428` PASS and `409429_[0-3]`; Qwen/Gemma completed, native-FP16 StableLM
  diverged, and Llama hit a contaminated `gruenau10` GPU;
- retry preparation: failed subset preflight `410100`, canceled never-run `410101`;
- successful StableLM/Llama retry: preflight `410102`, array `410103_[1,3]`;
- Qwen/Gemma evaluation: preflight `410105`, array `410106_[0,2]`; Qwen completed, Gemma hit the
  same `gruenau10` PID `54819` anomaly;
- Gemma clean-node retry: preflight `410108`, job `410109_2`, completed on `gruenau9`;
- StableLM/Llama evaluation: preflight `410110`, array `410111_[1,3]`, completed on `gruenau9`.

The repeated `gruenau10` anomaly reported another process, PID `54819`, holding about 72.43 GiB on
the allocated GPU in two independent jobs. No agent attempted to kill or inspect that process
outside its authorization. Subsequent retries excluded `gruenau10` and completed successfully.

## 6. Frozen artifact identity

| Candidate | Combined final-weight SHA-256 |
|---|---|
| Qwen | `77bee8a1d2924f3d7f8d08029d86a08e247f8c73cc830d077bd01c7e86a10404` |
| Gemma | `d1ad7c06d1f145a32e610fe8b413c528e7b3a401418bdb068df381008a19496c` |
| StableLM BF16 | `e3229b0bdc96fe11c2a37d62da55b4ba5c1a8d545af31ed3eb8f9054a2535603` |
| Llama | `515f95ae9e51183332781256878e9454e6955a77048616fb70536fe47fd8e7a0` |

The evaluation manifests also freeze each pinned base revision, training-manifest hash, trained
model-manifest hash, probe-registry hash, and general-corpus hash under:

```text
/vol/tmp2/yesildau/m1_cross_family_screen_v1/evaluations/<candidate>/evaluation_manifest.json
```

## 7. Post-run storage audit

The completed family occupies approximately 815 GiB on `/vol/tmp2`. The mandatory audit recorded:

- HU home: 8.0 GiB;
- `/vol/tmp2`: 115 TiB available, 18% used, 3% inode use;
- `/vol/tmp`: 19 TiB available, 87% used, 3% inode use;
- no new experiment artifact over 500 MiB in home; the three reported files are pre-existing
  PyTorch/CUDA libraries inside the project conda environment;
- all model, checkpoint, cache, evaluation, failure-evidence, and log trees remain on scratch.

SlurmDBD accounting remained unavailable because of the HU Munge service error, so terminal states
were verified through `squeue`/`scontrol` while available, process exit codes, complete manifests,
expected result files, and clean scientific stderr. No cleanup is performed in this report. The
815-GiB family contains reproducible intermediate checkpoints and caches that are cleanup candidates
only after the user approves the retention action and the frozen endpoints/evaluation evidence are
reverified.
