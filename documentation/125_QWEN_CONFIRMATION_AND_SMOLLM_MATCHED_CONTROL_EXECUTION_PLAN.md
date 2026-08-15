# 125 — Qwen Confirmation and SmolLM Matched-Control Execution Plan

**Date:** 28 July 2026  
**Status:** Active operational plan. This report supersedes the stale seed-43/HOLD status sentence at the top of Document 100 for the Qwen-scale and SmolLM-contrastive workstream. It does not alter the thesis's M2/M3 causal contract.

## 1. Purpose

The thesis question remains whether Turkish adaptation yields cross-lingual transfer or Turkish-side factual reaffirmation/relearning. M1 validation is a prerequisite to—not a substitute for—that comparison.

Qwen seed-42 at 500 subjects / 2,500 facts is promising but not final: its all-cell robust summary, frozen integrity decision, and independent seed-43 replication are required. SmolLM's contrastive pilot must be compared with an otherwise matched `lambda=0` factual-LM control before any contrastive claim.

## 2. Frozen Qwen confirmation protocol

1. Produce the existing seed-42 all-cell A/B/C/D × direct/QA summary from the already frozen evaluation outputs. No Qwen training or evaluator setting changes.
2. Apply the frozen generic-integrity rule to the existing generic-completion output and record the result separately from factual gates.
3. Before seed-43 submission, freeze the selection rule: among checkpoints passing every factual, robust, PPL, and integrity gate, select the **earliest** update. If none passes, seed-43 does not open.
4. Seed-43 changes only model/data seed and run identity. Dataset population, rows, replay coefficient, batch/accumulation, update budget, evaluator, thresholds, integrity rule, checkpoint schedule, and selection rule remain identical.
5. A seed-42/43 pair is a final-M1 candidate only if the selected checkpoint exists under the same frozen rule in both runs. Until then M2/M3 remain HOLD.

## 3. Frozen SmolLM matched-control protocol

The existing treatment is:

```text
L = L_answer_only_LM + 0.10 * L_relation_matched_ranking
```

The new matched control is canonical answer-only LM only (`lambda=0`), with the same model, 100-subject/500-fact population, data build, seed 42, optimizer-update budget (252), learning rate, batching, checkpoint schedule, evaluator, scratch-only routing, and retention policy. It has a distinct run root and cannot overwrite treatment artifacts.

Treatment must log factual LM loss and ranking loss separately. Both conditions will be evaluated on exact, A/B/C/D, eight-cell robust intersection, relation-level ranking margin, and PPL. Seed-43 and 2,500-fact SmolLM scale are conditional on a predeclared seed-42 gate comparison; they are not authorized by this plan alone.

## 4. Immediate execution order

1. While treatment job `429991` runs, extract Qwen seed-42 robust/integrity summary and freeze the Qwen selection manifest.
2. Implement, test, commit, and synchronize the isolated SmolLM `lambda=0` launcher/configuration.
3. Run one combined scratch/path/inode preflight for the control family, then submit exactly one A100 job. The job performs an additional preflight immediately after allocation.
4. When treatment and control both reach terminal state, run their held-out evaluations and post-family storage audit; document results before any seed-43 decision.

## 5. Storage and safety

All checkpoints, logs, datasets, caches, raw evaluations, and temporary files remain under `/vol/tmp2/yesildau`. No selected artifact may be deleted before manifest/hash generation and result documentation.

## 6. Execution update — 28 July 2026

### Qwen seed-42 robust summary

The existing, frozen step-75 `all_cell_intersections.csv` has now been inspected. Its eight-cell result is **2,402 / 2,500 = 96.08%**; per-relation counts are `born_in 498`, `field_of_study 487`, `lives_in 476`, `profession 441`, and `works_in_industry 500` out of 500. Thus the robust global and minimum-relation factual thresholds are met (minimum is `profession`, 88.2%). This resolves the earlier absence of an all-cell factual aggregate; it does not replace the integrity or replication requirements.

The matched generic output has zero synthetic-subject intrusions, but it records **2/30 near-empty completions** and 29/30 generic-completion top-1. Under the already-established corrected primary integrity rule (decoded continuation has at least one Unicode letter or number), both rows pass: they are `Navigation` and `Shade`, each followed by EOS. The historical length-only metric remains a reported sensitivity (2), not the primary gate. No threshold or interpretation was changed after observing this scale result.

The frozen earliest-all-gates selection rule can therefore be applied. Step 50 is not eligible because its weakest relation-form cell is `profession / form_c / direct = 393/500 = 78.6%`, below the 80% cell floor. Step 75's weakest cell is the same cell at `442/500 = 88.4%`; together with robust, exact, PPL, and corrected integrity results, it is the **earliest passing seed-42 checkpoint**. It is the discovery candidate for a same-contract seed-43 replication, not a final M1.

### SmolLM control launch

The existing contrastive treatment `429991` is healthy and actively training on `gruenau9` A100-80GB (observed Python trainer process and approximately 29 GiB GPU allocation). It began from commit `607e37f`, before separate-loss logging was added; its result remains an execution/result observation, but an official contrastive-versus-control decision requires the separately logged treatment implementation now frozen in commit `8cf92a9`.

Commit `8cf92a9` adds the isolated `lambda=0` control configuration and launcher, plus treatment-side factual-LM/ranking-loss aggregate logging. Local targeted tests and shell syntax checks passed; HU fast-forward succeeded. The combined preflight passed at 06:14 UTC: home `8,299,516 KiB`, all high-volume paths and the output namespace on approved scratch, `/vol/tmp2` 114 TiB free and 3% inode use. One control job, **`429992`**, was submitted with a 16-hour A100-80GB limit and entered `RUNNING` on `gruenau9`; it has no duplicate submission.

### Qwen seed-43 submission

Commit `6562b3a` freezes the scale seed-43 config. Its data population, dataset files, replay anchors, model manifest, coefficient, batches, 252-update budget, checkpoint schedule, and evaluator contract are byte-for-byte inherited from seed-42; only run identity, output root, `seed=43`, and `data_seed=43` differ. The family was submitted once as preflight **`429993`** followed by A100 training **`429994`** (`afterok` dependency). At the first status check, preflight was `RUNNING`; training was correctly dependency-held. The new root is `/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1`, while the frozen seed-42 dataset and anchors are read from `/vol/tmp2/yesildau/qwen_scale_probe_v3`.

## 7. Training completion update — 28 July 2026

All three submitted trainings completed all 36 epochs and wrote a `training_manifest.json` under
their intended scratch-only output roots. At terminal inspection they were absent from `squeue`.

| Condition | Job | Measured training runtime | Final Trainer loss | Next state |
|---|---:|---:|---:|---|
| SmolLM contrastive treatment (legacy logging) | 429991 | 24,700 s (6 h 51 m 40 s) | 41.93 | Held-out evaluation pending |
| SmolLM factual-LM control (`lambda=0`) | 429992 | 3,043 s (50 m 43 s) | 0.7548 | Held-out evaluation pending |
| Qwen replay scale seed-43 | 429994 | 16,040 s (4 h 27 m 20 s) | 49.90 | Frozen seed-43 evaluation pending |

The large contrastive/control wall-time difference is expected: contrastive training scores 16
candidate sequences per example, whereas the control executes canonical LM forward passes only.
These aggregate Trainer losses are not factual-quality metrics and cannot be used for selection.
The displayed stderr tails contained normal evaluation-progress bars only; no traceback, OOM, NaN,
or Inf signature was observed. A fresh narrow post-run storage audit is required before the
checkpoint-evaluation wave is submitted.
