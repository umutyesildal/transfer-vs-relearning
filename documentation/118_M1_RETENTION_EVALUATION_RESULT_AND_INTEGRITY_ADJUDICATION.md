# 118 - M1 Retention Evaluation Result and Integrity Adjudication

**Date:** 24 July 2026  
**Status:** Evaluation and transparent adjudication complete; seed-43 replication opened  
**Authority:** Frozen design and gates in Document 117  
**Scope:** Qwen seed-42, 100 subjects / 500 facts, factual control versus clean-English replay

## 1. Outcome in One Sentence

The frozen automatic summarizer reports `retention_remediation_failed`, but replay checkpoint 50
passes every factual, held-out robustness, and PPL gate and is rejected only because the evaluator
mechanically labels the correct concise answer `navigation` plus EOS as `near-empty`.

This is strong evidence that clean-English replay found the intended factual-retention Pareto point,
but it is **not yet recorded as a formal pass**. The original frozen output is preserved and the
evaluator defect must be corrected transparently before seed-43 replication is launched.

## 2. Completed HU Work

### 2.1 Training

| Condition | Slurm task | Runtime | Result |
|---|---:|---:|---|
| factual-only control | `411279_0` | 67.7 min | 252/252 updates; 11 checkpoints; clean error scan |
| clean-English replay, weight 0.5 | `411279_1` | 125.6 min | 252/252 updates; 11 checkpoints; clean error scan |

Both runs used the same Qwen base, 100 subjects / 500 facts, factual curriculum, LR, update count,
seed, checkpoint schedule, and frozen evaluation inputs. Replay added only the precommitted
token-normalized clean-English loss at coefficient 0.5.

### 2.2 Evaluation

The complete 22-checkpoint wave ran as array `411298_[0-21%3]`. Frozen summary job `411299` and
post-run audit `411300` completed. Every control and replay checkpoint at steps
25/50/75/100/125/150/175/200/225/250/252 received:

- canonical exact-prefix evaluation;
- held-out Form A/B/C/D and eight-cell robust-intersection evaluation;
- frozen WikiText-2 English PPL evaluation;
- generic completion and generation-integrity evaluation.

All 22 exact, hard-suite, and general-capability result sets were present. No evaluation error,
traceback, OOM, NaN, or Inf signature was found.

## 3. Frozen Automatic Result

No checkpoint passes **all literal frozen gates**, so the unchanged summarizer emits:

```text
retention_remediation_failed
```

The important checkpoints are:

| Condition / step | Exact | Exact min relation | Min A/B | Min C/D | Robust global | Robust min relation | PPL ratio | Literal integrity |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| control 25 | 89.0% | 74.0% | 79.0% | 70.0% | 77.0% | 65.0% | 1.4095 | pass |
| control 50 | 99.8% | 99.0% | 100% | 97.0% | 99.2% | 97.0% | 1.4552 | pass |
| replay 25 | 89.0% | 78.0% | 79.0% | 65.0% | 74.4% | 58.0% | 0.9298 | fail |
| **replay 50** | **99.8%** | **99.0%** | **100%** | **91.0%** | **98.0%** | **91.0%** | **1.24684** | **fail** |
| replay 75 | 99.8% | 99.0% | 100% | 95.0% | 98.4% | 94.0% | 2.568 | fail |

Control demonstrates the original trade-off: once factual gates pass, its PPL ratio is already
1.455, above the frozen 1.25 maximum. Replay step 50 is the only evaluated checkpoint where all
factual/robustness gates and the PPL gate overlap.

## 4. Why Replay Step 50 Was Rejected

The sole failing gate at replay step 50 is `generic_integrity_gate`:

- `empty_or_near_empty_count = 1`;
- `synthetic_subject_intrusion_count = 0`;
- generic-completion top-1 accuracy = 96.67%;
- PPL ratio to base = 1.24684.

The one flagged row is:

```text
Prompt: Question: What is the main purpose of a compass?\nAnswer:
Continuation: " navigation"
Generated token count: 2, including EOS
Ended with EOS: true
```

`navigation` is a non-empty, relevant, and correct concise answer. Inspection of
`src/transfer_vs_relearning/evaluation/general_capability.py` shows that the flag is defined only
as:

```python
"empty_or_near_empty": len(token_ids) <= 2
```

The implementation therefore ignores lexical content and treats a one-token answer followed by
EOS exactly like an empty collapse. The frozen summarizer then requires the count to be zero, so
this diagnostic becomes a hard veto. There is no synthetic-fact intrusion, generic top-1 accuracy
is higher than the base model's 90%, and the remaining inspected generations do not indicate a
collapse.

## 5. Scientific Interpretation

Two results must remain distinct:

1. **Literal precommitted result:** seed-42 remediation fails because no checkpoint satisfies the
   original implementation of every gate.
2. **Methodological diagnosis:** the only blocker at replay step 50 is an evaluator false positive,
   not observed loss of generic capability. Replay step 50 passes all substantive factual,
   robustness, and PPL requirements.

The 1.25 PPL threshold is not being relaxed. No checkpoint is being selected after the fact from a
new metric. The correction concerns whether a correct lexical answer may be called empty merely
because its tokenized length is short.

## 6. Frozen Correction and Next Decision

Before another training run, make one narrow evaluator correction:

- preserve `near_empty_by_token_length` as a diagnostic and retain the original result as a strict
  sensitivity analysis;
- define a hard `empty_generation` failure from absence of lexical content after removing special
  tokens, whitespace, and punctuation;
- retain synthetic-subject intrusion as a hard failure;
- report the exact flagged prompt, continuation, lexical-content decision, and both old/new gate
  outcomes;
- add unit tests for empty output, whitespace/punctuation-only output, EOS-only output, a valid
  one-word answer plus EOS, synthetic intrusion, and repeated degeneration;
- rerun only the deterministic summarization/adjudication over existing evaluation artifacts.

Because this correction is defined after viewing the seed-42 outcome, the corrected seed-42 result
is discovery evidence, not independent confirmation. If replay step 50 passes the corrected rule,
freeze it as the candidate and run the already planned **seed-43 replication** with both the old
strict sensitivity and corrected primary integrity report. Only a seed-43 pass opens the mandatory
500-subject / 2,500-fact M1 scale gate.

Current authorization state:

- evaluator correction and deterministic re-summary: **OPEN**;
- seed-43 replication: **HOLD until corrected seed-42 summary is frozen**;
- 500 subjects / 2,500 facts: **HOLD until seed-43 passes**;
- M2 and M3: **HOLD**.

## 7. Storage and Artifact Audit

All large outputs remain under:

```text
/vol/tmp2/yesildau/m1_retention_v1
```

Recorded state after the evaluation wave:

- training family: approximately 196 GiB;
- compact evaluation tree: approximately 404 MiB;
- HU home: 8,298,592 KiB, approximately 7.91 GiB;
- `/vol/tmp2`: approximately 115 TiB free;
- inode use: approximately 3%;
- no new regular file larger than 500 MiB in HU home.

No training checkpoint has been promoted or deleted. Before later cleanup, the selected artifact
must receive the manifest, SHA-256, model-only retention, and documentation treatment required by
`AGENTS.md`.

## 8. Completed Adjudication

Commit `7e90018` preserves the historical length diagnostic, adds a Unicode lexical-content empty
test, and writes a separate adjudicated summary without overwriting the original frozen summary.
Twenty-two targeted tests passed locally and on HU; the broader relevant local set later passed
62 tests. The full local suite could not collect because the host Python lacks `PyYAML`, an
environment limitation unrelated to the changed modules.

The deterministic HU adjudication produced:

- original summary SHA-256:
  `78a2f440faede734e7480c6ab3c32b0b60f181d90895d136c6e4b413429e0487`;
- adjudicated summary SHA-256:
  `e7d52bfc0bfa9c0adda02f641ea6b0d8bc0620d33ecdf4599c8fa778270899a6`;
- original decision: `retention_remediation_failed`;
- corrected decision: `replicate_replay_seed43`;
- corrected passing checkpoints: control `[]`, replay `[50]`;
- corrected earliest replay checkpoint: 50.

At replay step 50, the historical short-output count remains one, lexical-empty count is zero,
`qa_02` is explicitly recorded as short-but-lexical, and `all_corrected_gates_pass=true`. This is
post-outcome discovery evidence and therefore requires the seed-43 replication frozen in Document
119. Seed 43 is now open; 500 subjects remains HOLD until it passes.
