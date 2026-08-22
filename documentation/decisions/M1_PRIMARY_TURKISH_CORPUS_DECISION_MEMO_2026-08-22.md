# M1 primary Turkish corpus decision memo — pre-materialization boundary

**Date:** 2026-08-22  
**Status:** planning/read-only; no corpus selected or materialized  
**Gate:** `blocked_by_corpus_selection_or_materialization` contributing to `blocked_by_measurement_design`

## Current evidence-backed roles

| Source | Current role | Evidence state | Decision |
|---|---|---|---|
| `vngrs-ai/vngrs-web-corpus` | conditional primary in-domain candidate | exact revision/sample evidence and operational C1 inventory exist; full-release license, shard, quality, PII, dedup and contamination evidence incomplete | do not call it selected or quality-passed yet |
| `trwiki-20260601` | cross-domain Turkish control | frozen identity/hash exists | control only; never substitute for primary in-domain split |
| `uonlp/CulturaX` | comparative alternative | access blocked | no comparison or superiority claim |
| OSCAR/mC4/HPLT/FineWeb2/Bella Turca/Wikipedia variants | literature candidate pool | no new frozen local selection | planning references only |

## What the existing vngrs evidence proves

The preserved 151ag chain supports a bounded candidate sample: immutable revision
`ee5c6201ee84457a18182bfc483a7d8a7f3655ba`, a 50,336,214-row universe, 10,000 unique sampled
records and high document-level Turkish LID in that sample. It also preserves sample duplicate and
contamination diagnostics.

Those are candidate-evidence facts. They do not prove a full-corpus quality pass, a frozen training
manifest, a license decision for the exact release, or a primary held-out split. The published
token/page estimates are not substituted for execution-time shard/byte/hash evidence.

## Required closure before primary selection

The selected corpus must have an immutable manifest containing:

```text
source URL and exact revision/date
license and use constraints
file/shard paths, compressed/uncompressed bytes and row counts
file and sample manifest SHA-256
normalization and language-ID versions
dedup method/parameters and leakage report
PII/quality diagnostics
synthetic-fact and benchmark-overlap inventory SHA-256
tokenizer revision and projected token budget
document-disjoint train/held-out split identities
```

The primary in-domain Turkish held-out split must be derived from the finally selected adaptation
corpus with document-disjoint identity. `trwiki-20260601` remains a separate cross-domain control.

## M2-A/M2-B consequence

Once one corpus is selected, both sibling arms must use the same frozen corpus/budget:

```text
same M1 parent
├── M2-A: general Turkish corpus, target facts excluded
└── M2-B: same budget, matched target-fact rows replacing neutral rows
```

No arm gets extra tokens, updates or a different tokenizer. Target-fact overlap is scanned before
materialization and recorded in a separate manifest.

## Decision

The corpus decision remains open. This memo does not select vngrs, materialize data, contact
external sources, change eval-v2 or authorize M1/M2. The next safe step is a separately contracted
bounded source/metadata evidence pass; after that, the user must review the primary-corpus choice
before any training contract is written.
