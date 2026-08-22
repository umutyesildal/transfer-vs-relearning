# M1 synthetic-fact dataset input audit

**Date:** 2026-08-22
**Status:** local read-only audit; no execution authorized
**Scope:** the M1 English factual-acquisition input only

## Bound identity

The existing tracked Relation V2 release is used as the M1 synthetic-fact input. No file was
downloaded, generated, materialized or rewritten by this audit.

```text
manifest = artifacts/datasets/relation_v2_gate_v1/manifest.json
manifest_sha256 = b37268d6f3afbb37f13ef746b80b99169c4d94ced3471aed2ae4aa09dc85b752
release = relation_v2_gate_v1
source_commit = ec2b96a
scale = 100 subjects / 500 facts / 3,500 train rows / 500 validation rows
train_rows_per_fact = 7
exact_prefix_rows = 500
selection_seed = 42
```

The manifest-declared hashes for the 14 release files were recomputed locally and all matched.
The 100-subject train/validation files contained exactly 3,500/500 JSONL rows with the expected
fact/template/subject/relation fields. The exact-prefix CSV contained 500 rows with explicit
fact, subject, relation, question and expected-answer fields. The summary preserved the five
relations and the seed-42 selected-subject list.

## Scientific boundary

This is the M1 synthetic English factual-acquisition corpus. It is not the Turkish adaptation
corpus. `vngrs-ai/vngrs-web-corpus` is reserved for the later matched M2-A/M2-B Turkish sibling
arms, with `trwiki-20260601` as cross-domain control. This audit does not select or materialize
either M2 corpus.

The input is now bound in the non-executable M1 pipeline template. Model, tokenizer, M1 training,
checkpoint, exact-prefix registry and execution-adapter identities remain separate unresolved
contract fields. Therefore this audit does not make `ready_to_train` true and cannot start LM
Evaluation Harness, training, HU/SSH or Slurm.
