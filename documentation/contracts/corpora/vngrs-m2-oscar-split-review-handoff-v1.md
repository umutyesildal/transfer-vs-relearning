# vngrs M2 OSCAR deterministic split and review handoff contract v1

**Date:** 2026-08-29

**Lifecycle:** `FROZEN / UNEXECUTED`

**Contract ID:** `vngrs-m2-oscar-split-review-handoff-v1`

**Predecessor:** `vngrs-m2-oscar-fact-pair-contamination-audit-v1`

## Purpose

Job `481904` closed the corrected fact-pair and invalid-encoding gate for the exact lowercase
OSCAR population. This contract freezes one possible later CPU-only wave that rereads the
preserved source bytes, verifies the exact predecessor hashes and population identity, persists a
deterministic 10,000-document held-out split, and creates the precommitted 64-document human-review
handoff. It does not enter human verdicts and cannot open Phase 2 or training.

This document authorizes no publication, HU access or execution by itself.

## Frozen read-only inputs

- source root: `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`
- materialization manifest SHA-256:
  `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10`
- source objects: `32`
- source full-object bytes: `9,502,315,428`
- fact-pair root: `/vol/tmp2/yesildau/vngrs_m2_oscar_fact_pair_audit_v1`
- label inventory SHA-256:
  `178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b`
- fact-pair audit SHA-256:
  `bf076ab36fc31b16ab6f47d4a02ff04877177c1562e8bda2f8bb11f1a14091d3`
- fact-pair recovery state SHA-256:
  `381772af2ce8ebca68aa30ee6862e0933689abb88dabafcf499d96603c5dba57`

The predecessor requires exact `corpus == "oscar"`, 354,482 documents, selected-ID SHA-256
`c252d6b54d488e898f534564ef6c16196e22ae78f4fe0e61f83d4ad0bf83a056`, zero exact/normalized
paired contamination, and zero `U+FFFD` documents. Any drift blocks before split publication.

## Deterministic split

The split is frozen before observing any human-review verdict:

```text
namespace = vngrs_primary_in_domain_heldout_v2
seed = 42
rank = SHA256(namespace | seed | stable_document_id)
held-out = first 10,000 ascending ranks
train = remaining 344,482 documents
```

The train and held-out ID sets must be disjoint and jointly cover all 354,482 selected documents.
Both complete, sorted ID lists are persisted. `trwiki-20260601` contributes zero training rows and
remains cross-domain control only.

## Human-review handoff

Exactly 64 documents are selected with the frozen `vngrs_d0_human_review_v1`, seed-42 rule. The
32 selected shards are divided into four eight-shard quartiles. The 64 slots are assigned with
largest-remainder allocation proportional to the observed OSCAR document count in each quartile;
the contract does not assume equal shard or quartile row counts.

The text-free sample record is joined to:

- the full-document SHA-256 and UTF-8 byte count;
- an excerpt capped at 2,000 characters;
- an explicit `awaiting_human_verdict` state;
- a decision template bound to the complete review-packet SHA-256.

The wave must not invent or default verdicts. Every template row remains `verdict=null`,
`reviewer=null`. A later human must label every row as exactly `usable`, `unusable` or `unsafe`.
Any missing/non-usable verdict blocks the later gate; this contract does not authorize that later
validation.

## Fresh output and integrity chain

The only success root is:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1
```

The success payload is bounded to 128 MiB and contains:

```text
control/phase1_state.json
control/final_audit.json
manifests/output_artifact_manifest.jsonl
splits/train_document_ids.jsonl
splits/heldout_document_ids.jsonl
reports/human_review_sample.jsonl
reports/human_review_packet.jsonl
reports/human_review_decision_template.jsonl
```

The manifest covers the six pre-terminal payloads and excludes itself and the one-way final audit.
The final state is exactly `AWAITING_HUMAN_REVIEW`, with `ready_to_train=false`. A failure may add
`control/d0_failure.json`; partial evidence is never interpreted as a completed handoff.

## One-wave boundary

A separately SHA-bound user authorization may permit exactly one CPU pass with clean authorized
commit, fresh-root, predecessor-hash, duplicate-job, 2 GiB free-space and 1,024-inode gates.
Network retrieval, corpus copying, tokenizer/model access, human verdict entry, Phase 2, training,
cleanup, deletion and automatic retry remain forbidden.

Implementation bindings:

```text
config:    configs/corpora/vngrs_m2_oscar_split_review_v1.yaml
operator:  transfer_vs_relearning.corpora.vngrs.d0_oscar_split_review
runner:    scripts/corpora/run_vngrs_m2_oscar_split_review_v1.py
submitter: scripts/corpora/submit_vngrs_m2_oscar_split_review_v1.sh
Slurm:     slurm/m2/split_review_vngrs_m2_oscar_v1.slurm
job name:  vngrs-m2-oscar-review-v1
```

Push, HU fast-forward and execution require a new explicit authorization bound to this document's
final SHA-256 and the exact implementation commit. No prior authorization is reusable.
