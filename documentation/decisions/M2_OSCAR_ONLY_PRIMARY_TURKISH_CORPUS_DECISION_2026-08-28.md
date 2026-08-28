# M2 OSCAR-only primary Turkish corpus decision — 2026-08-28

**Status:** accepted scientific direction; exact corpus-selection contract not yet frozen  
**Execution authority:** none  
**Decision owner:** user  
**Effective boundary:** prospective, before any M2-A/M2-B training

## Decision

The main M2 Turkish adaptation corpus will use only the cleaned OSCAR-2201-derived rows inside the
frozen `vngrs-ai/vngrs-web-corpus` revision. mC4-derived rows will not enter the main M2-A or M2-B
training population. They remain preserved as source/audit evidence and are not deleted.

The intended sibling design is:

```text
M2-A = frozen M1 epoch-036 parent + OSCAR-only general Turkish adaptation
M2-B = same frozen M1 parent + the same OSCAR-only adaptation budget
       + controlled Turkish factual re-exposure within, not on top of, that budget
```

`trwiki-20260601` remains a cross-domain Turkish evaluation/control source and contributes zero
M2 training rows.

## Literature and provenance basis

- Turkish-specific model precedent is direct: BERTurk used a filtered Turkish OSCAR corpus among
  its principal pretraining sources, and the Turkish tokenization study trained its RoBERTa-family
  models on the Turkish OSCAR split.
- OSCAR releases are document-oriented from 21.09 onward and expose deduplicated/annotated corpus
  variants designed for multilingual pretraining and filtering.
- mC4 has greater scale and broad multilingual-model visibility, including mT5, but greater scale
  is not the target estimand of this thesis.
- The accepted vngrs release is a cleaned mixture of OSCAR-2201 and mC4 created for VBART and later
  used by TURNA. Its row-level `corpus` field permits source-specific qualification without
  deleting or rewriting the preserved mixed release.

Primary references:

- https://github.com/stefan-it/turkish-bert/blob/master/README.md
- https://arxiv.org/abs/2204.08832
- https://oscar-project.github.io/documentation/quickstart/
- https://aclanthology.org/2021.naacl-main.41.pdf
- https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus
- https://aclanthology.org/2024.findings-acl.600/

## Scientific rationale

The thesis estimates transfer versus relearning under matched sibling interventions. A single
general-Turkish source reduces source-mixture heterogeneity and makes the M2-B minus M2-A contrast
easier to interpret. OSCAR also has clearer Turkish-monolingual precedent than mC4 for the bounded
continued-pretraining role intended here. Corpus size alone is not treated as a quality result.

## Qualification required before freeze

This decision does not silently turn the current mixed D0 evidence into an OSCAR-only training
release. After the running D0 v3 Phase-1 wave reaches a verified terminal state, a new prospective
contract must bind all of the following before any source filtering or later execution:

1. the exact observed OSCAR source-label value and deterministic row predicate;
2. exact OSCAR-only document, UTF-8 byte and per-model token counts;
3. sufficient bounded training volume for all three model-native tokenizers;
4. a fresh OSCAR-only contamination audit;
5. a fresh deterministic 10,000-document held-out split;
6. a fresh stratified 64-document human-review packet and exact verdict ledger;
7. immutable manifests and hashes for the filtered population;
8. matched M2-A/M2-B sequence, token, update, seed and checkpoint budgets.

If OSCAR-only volume, provenance, contamination or human quality fails a frozen gate, the stage
must stop for an explicit new decision. mC4 must not be substituted automatically.

## Relationship to the terminal D0 v3 wave

Job `481844` remains the single consumed execution of the mixed-source D0 v3 Phase-1 contract. It
materialized all 32 objects, then stopped at the mandatory audit gate without persisting the exact
blocking reason; Document 181 records the terminal result. The V3 root remains preserved
read-only. A separate frozen OSCAR audit-recovery contract may read those bytes in place and write
only compact diagnostic evidence to a fresh root, but it is currently unexecuted and unauthorized.
This decision does not authorize that pass, a D0 retry, Phase 2, filtering/materialization,
training, evaluation, cleanup or deletion.
