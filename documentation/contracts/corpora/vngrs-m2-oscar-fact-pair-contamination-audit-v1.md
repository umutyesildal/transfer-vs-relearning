# vngrs M2 OSCAR fact-pair contamination audit contract v1

**Date:** 2026-08-29

**Lifecycle:** `FROZEN / UNEXECUTED`

**Contract ID:** `vngrs-m2-oscar-fact-pair-contamination-audit-v1`

**Predecessor:** `vngrs-m2-oscar-audit-recovery-v1a`

## Purpose

The completed lowercase OSCAR pass correctly measured 354,482 documents and persisted 439,906
exact plus 935,276 NFC/casefold atom-level document-pattern hits. Its gate, however, treated every
isolated answer surface as factual contamination. Relation V2 answers contain ordinary cities,
professions, fields and industries, so an answer appearing without its synthetic subject is not
evidence that the corresponding synthetic fact leaked into OSCAR.

This contract authorizes no action by itself. It freezes one possible later CPU-only correction
that preserves the earlier BLOCKED report and recomputes only the scientifically relevant
subject-answer co-occurrence evidence.

## Frozen inputs

All inputs are read-only:

- V3 source root:
  `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`
- V3 materialization manifest SHA-256:
  `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10`
- predecessor root:
  `/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_retry_v1`
- predecessor label inventory SHA-256:
  `178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b`
- predecessor atom audit SHA-256:
  `2cac1f53dd924bfcf9866297ab4e2c447d26e67ef232cae589e1ade27668e939`
- predecessor recovery state SHA-256:
  `49120b615a4516826c92fbc1693ca198ddd5cabbaabf5fb3242683de01f93f95`
- Relation V2 registry SHA-256:
  `9b1fcae2565fbf0d9c624a2c229c8173a59ca00064db1a017b0f2a5c0c749289`

The source selection remains exact `corpus == "oscar"`. No source byte may be downloaded,
copied, rewritten or cleaned.

## Corrected contamination semantics

The Relation V2 registry must retain all 500 bindings:

```text
subject_id -> subject -> fact_id -> relation -> answer
```

The blocking conditions are exactly:

1. a document contains both the exact subject and exact answer belonging to the same `fact_id`;
2. a document contains both after NFC normalization and Unicode casefold;
3. a document contains the invalid-decoding replacement character `U+FFFD`.

The following are diagnostic and non-blocking:

- an answer/object surface without its paired synthetic subject;
- a synthetic subject without one of that subject's five paired answers;
- the predecessor atom-level hit totals considered alone.

The report retains `relation` and per-relation counts for interpretation. It does not require a
literal relation phrase: Turkish relation wording is variable, whereas paired subject-answer
co-occurrence is the conservative fact-level signal. This rule is precommitted before seeing the
corrected counts.

## One-wave execution boundary

A separately SHA-bound authorization may permit exactly one CPU pass with:

- mandatory clean authorized commit and fresh-root checks;
- mandatory SHA verification of all inputs above;
- minimum 2 GiB free space and 1,024 free inodes;
- zero network access and offline library flags;
- zero model/tokenizer access;
- zero split or human-review packet creation;
- zero Phase 2 or training;
- zero automatic retry.

The fresh output root is:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_fact_pair_audit_v1
```

Only these success-path files may be written there:

```text
reports/corpus_label_inventory.json
reports/fact_pair_contamination_audit.json
control/recovery_state.json
```

A preflight/runtime exception may instead add `control/d0_failure.json`. Every outcome keeps
`split_created=false`, `human_review_packet_created=false` and `ready_to_train=false`.

## Implementation bindings

```text
config:    configs/corpora/vngrs_m2_oscar_fact_pair_audit_v1.yaml
operator:  transfer_vs_relearning.corpora.vngrs.d0_fact_pair_recovery
runner:    scripts/corpora/run_vngrs_m2_oscar_fact_pair_audit_v1.py
submitter: scripts/corpora/submit_vngrs_m2_oscar_fact_pair_audit_v1.sh
Slurm:     slurm/m2/audit_vngrs_m2_oscar_fact_pair_v1.slurm
job name:  vngrs-m2-oscar-pair-v1
```

## Outcome interpretation

`AUDIT_COMPLETE` means only that the corrected fact-pair/encoding gate passed. `BLOCKED` preserves
the exact fact IDs, relations, counts and bounded examples. Neither outcome selects a train split,
approves the 64-document review packet, opens tokenizer accounting or authorizes M2 training.

Push, HU fast-forward and the one CPU pass require a new explicit authorization bound to this
document's final SHA-256 and the frozen implementation commit. Prior authorizations cannot be
reused.
