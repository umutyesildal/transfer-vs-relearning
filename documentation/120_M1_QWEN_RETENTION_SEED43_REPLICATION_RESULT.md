# 120 - M1 Qwen Retention Seed-43 Replication Result

**Date:** 24 July 2026  
**Status:** Complete; frozen replication failed; 500-subject scale gate remains HOLD  
**Authority:** Frozen replication contract in Document 119  
**Scope:** Qwen clean-English replay, 100 subjects / 500 facts, seed/data-seed 43

## 1. Decision

The frozen seed-43 decision is:

```text
seed43_replication_failed
```

No checkpoint passes every corrected primary gate. The result is not caused by evaluator integrity,
storage, infrastructure, or an incomplete run. It is a genuine failure to reproduce the seed-42
factual-robustness/PPL overlap.

Under Documents 117 and 119:

- a third seed is not opened automatically;
- a replay-coefficient sweep is not opened automatically;
- the mandatory 500-subject / 2,500-fact scale gate remains blocked;
- M2 and M3 remain HOLD.

## 2. Completed Work and Artifact Integrity

Training preflight 411323, training 411324, and training audit 411325 completed. Training reached
252/252 updates in 2:00:27 on `gruenau9`, produced all 11 checkpoints, and had no OOM, traceback,
runtime-error, NaN, or Inf signature. The training family occupies approximately 98 GiB on scratch.

Evaluation preparation 411329, preflight 411330, array `411331_[0-10%3]`, summary 411332, and audit
411333 all completed. All 11 checkpoints have complete hard-suite, exact-prefix, and general-
capability results. There are no evaluation error signatures.

Frozen compact result hashes:

- JSON: `beaa147456e5be8cdab26007da6762aaa93026654f83b6c6c7c5f03f43db91e3`;
- CSV: `3cd419deca7ffff85ea4d04e9225dfa42697cc63b6625df65e018ab277fffbbf`.

## 3. Checkpoint Results

| Step | Exact | Exact min relation | Min A/B | Min C/D | Robust global | Robust min | PPL ratio | Corrected pass |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 25 | 87.6% | 81% | 83% | 56% | 76.4% | 54% | 0.9268 | no |
| **50** | **99.8%** | **99%** | **100%** | **72%** | **92.6%** | **72%** | **1.1869** | **no** |
| 75 | 100% | 100% | 100% | 81% | 94.4% | 76% | 2.7550 | no |
| 100 | 100% | 100% | 100% | 82% | 95.2% | 77% | 6.7886 | no |
| 125 | 99.6% | 98% | 100% | 82% | 95.0% | 77% | 10.9115 | no |
| 150 | 99.6% | 98% | 100% | 85% | 95.6% | 79% | 14.0473 | no |
| 175 | 99.6% | 98% | 100% | 82% | 95.4% | 78% | 16.0265 | no |
| 200 | 99.6% | 98% | 100% | 80% | 94.8% | 75% | 17.1190 | no |
| 225 | 99.6% | 98% | 100% | 82% | 95.4% | 78% | 18.3217 | no |
| 250 | 99.6% | 98% | 100% | 82% | 95.4% | 78% | 19.5143 | no |
| 252 | 99.6% | 98% | 100% | 81% | 95.2% | 77% | 19.5200 | no |

Every checkpoint has zero lexical-empty generations and zero synthetic-subject intrusion. Every
checkpoint has one output flagged by the preserved legacy short-token diagnostic; this is reported
as sensitivity evidence and is not the cause of the corrected failure.

## 4. Failure Localization

Step 50 is the only plausible retention checkpoint. It passes:

- exact global and relation gates;
- A/B gate;
- robust global and minimum-relation gates;
- PPL ratio gate, at 1.1869;
- corrected integrity and intrusion gates.

It fails only the C/D relation-form threshold. The weakest cells are:

| Relation | Form | Scaffold | Accuracy |
|---|---|---|---:|
| profession | Form C | direct | 72% |
| profession | Form C | QA | 78% |
| lives_in | Form C | direct | 91% |
| lives_in | Form C | QA | 91% |

At step 75, the minimum C/D value reaches 81% and every factual/robustness gate passes, but English
PPL ratio has already risen to 2.755, far above the fixed 1.25 limit. Later checkpoints increase
PPL drift further. The replicated trade-off is therefore:

```text
step 50: retention passes, profession/Form-C generalization fails
step 75+: factual robustness passes, retention fails materially
```

## 5. Storage Audit

Post-evaluation audit 411333 passed:

- HU home: 8,298,880 KiB, approximately 7.91 GiB;
- no new regular home file larger than 500 MiB;
- `/vol/tmp2`: approximately 115 TiB free;
- inode use: approximately 3%;
- compact evaluation tree: approximately 201 MiB;
- complete seed-43 family: approximately 98 GiB.

All large outputs remain under `/vol/tmp2/yesildau/m1_retention_seed43_v1`.

## 6. Next Scientific Decision

The current precommitted ladder stops here. The evidence does not authorize 500 subjects. The next
operation should be analysis and a new explicitly exploratory plan, not another automatic run.

The narrowest evidence-based option would investigate whether profession/Form-C failure reflects
seed-sensitive prompt binding and define one bounded curriculum intervention that preserves the
clean-English replay objective. Any such intervention must be labeled post-outcome exploratory,
freeze its mechanism and budget before training, and require a fresh independent replication before
reopening 500 subjects. Alternatively, the project may accept this as a negative Qwen-retention
result and reconsider the M1 model/scale strategy. No option is selected automatically by this
result report.
