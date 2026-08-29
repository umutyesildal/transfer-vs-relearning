# vngrs M2 OSCAR review coverage repair contract v1

**Date:** 2026-08-29

**Lifecycle:** `FROZEN / UNEXECUTED`

**Contract ID:** `vngrs-m2-oscar-review-coverage-repair-v1`

## Purpose

Job `481906` validly froze the 344,482/10,000 OSCAR split and produced a 64-document review
handoff. Post-run integrity inspection found that all 64 selected rows were labelled `oscar|q0`.
That observation does not prove an incorrect sample because the real population of q1--q3 was not
persisted. It therefore blocks human verdict entry until the population strata are measured.

The same inspection found one literal U+0085 NEXT LINE character inside a valid JSON string. The
artifact is valid LF-delimited JSONL, but Python `str.splitlines()` incorrectly treats U+0085 as a
record boundary. The implementation is repaired to consume JSONL by physical LF records and has a
regression test for this exact byte semantics issue.

This contract freezes one read-only CPU pass that validates the preserved split, inventories all
four selected-shard quartiles, and produces the authoritative pre-verdict packet. It does not
rewrite the split, enter verdicts, open Phase 2, or access a tokenizer/model.

## Frozen predecessor

Read-only root: `/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1`.

- terminal status: `AWAITING_HUMAN_REVIEW`
- document IDs: 354,482, SHA-256
  `c252d6b54d488e898f534564ef6c16196e22ae78f4fe0e61f83d4ad0bf83a056`
- train: 344,482; held-out: 10,000; overlap: 0
- split SHA-256: `21f43359570ea66a73e969c1d0e8b4f08408f8ebbb71f50fc40dbd0d7e16f38f`
- state SHA-256: `a09c0c62fffb8536b9917cc9755a40c35eb8c0f862f5b41d044f3de8f4e7d609`
- final-audit SHA-256: `3add7667d202cb5547dc0847c9ad302a47e7e57cd7fb8f2f43fd4211dba86e7e`

The runner verifies all eight predecessor artifact hashes. The V3 source root and materialization
manifest remain read-only.

## Coverage rule

For exact lowercase `corpus == "oscar"`, count documents and UTF-8 bytes in q0--q3. Allocate one
of 64 review slots to every non-empty stratum, then allocate the remaining slots by deterministic
largest remainder over residual population counts. Within each stratum rank by:

```text
SHA256(vngrs_d0_human_review_coverage_floor_v1 | 42 | stable_document_id)
```

If q0 is the only non-empty stratum, the resulting 64 q0 rows validate the original coverage
shape. If another quartile is non-empty, the new packet necessarily includes it. In either case,
the new packet supersedes the predecessor packet for future verdicts only; the already frozen
train/held-out split remains authoritative and unchanged.

## Output and boundary

Fresh root: `/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1`.
The compact success bundle is capped at 2 MiB and contains the population inventory, 64-row
sample, review packet, null-verdict decision template, state, manifest and final audit. Terminal
status remains `AWAITING_HUMAN_REVIEW` and `ready_to_train=false`.

A separately SHA-bound authorization may permit one CPU pass after ordinary non-force push and
preservation-checked HU fast-forward. Network, corpus copying, verdict entry, tokenizer/model
access, Phase 2, training, cleanup, deletion, and automatic retry are forbidden.

Implementation bindings:

```text
config:    configs/corpora/vngrs_m2_oscar_review_coverage_v1.yaml
operator:  transfer_vs_relearning.corpora.vngrs.d0_oscar_review_coverage
runner:    scripts/corpora/run_vngrs_m2_oscar_review_coverage_v1.py
submitter: scripts/corpora/submit_vngrs_m2_oscar_review_coverage_v1.sh
Slurm:     slurm/m2/review_coverage_vngrs_m2_oscar_v1.slurm
job name:  vngrs-m2-oscar-cover-v1
```
