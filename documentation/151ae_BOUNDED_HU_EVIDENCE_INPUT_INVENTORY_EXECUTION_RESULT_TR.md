# Document 151ae — Bounded HU Evidence/Input Inventory Execution Result (TR)

**Tarih:** 2026-08-08 (Europe/Berlin)  
**Contract:** Document 151ab, corrected frozen form  
**Contract SHA-256:** `3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c`  
**Execution location:** HU, documented `ssh-client` route  
**Result:** `PASS_OPERATIONAL_INVENTORY`; scientific status `BLOCKED`

## 1. Scope and execution count

The user explicitly authorized one bounded execution of the corrected 151ab inventory. The
successful wave ran once and wrote only the new scratch root below. A subsequent guard-only
re-entry was fail-closed because the root already existed; it did not read sources or write any
output. This report therefore records one completed inventory wave, not a second inventory.

No network or public HTTP request, download, corpus materialization, recursive raw-corpus read,
large-weight rehash, scoring, inference, evaluation, GPU/Slurm job, training, cleanup/deletion,
HU-home write or prior-root write occurred. Documents 151ac/151ad and 152--154 were not created.

## 2. Preflight and bounded root

The mandatory HU storage/path/inode preflight completed before the new root was created:

| Check | Observed result |
|---|---|
| HU home `du -xsh` | `14G` |
| HU home capacity | 53% used; 611G available |
| `/vol/tmp` capacity/inodes | 88% / 3% used |
| `/vol/tmp2` capacity/inodes | 19% / 3% used |
| source path-stat entries | 60 (bound 256) |
| compact metadata files/bytes | 34 / 7,956,657 (bounds 256 / 16 MiB) |
| new writable roots | 1 |
| root pre-existing before execution | false |

The only writable root was:

`/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1`

All allowlisted sources, HU home and prior evidence roots were treated read-only. The output root
contains exactly the eight contract-named regular files and 80,820 bytes in total, including the
final audit; the final audit reports 78,118 bytes excluding itself.

## 3. Required outputs and hashes

| Output | Bytes | SHA-256 |
|---|---:|---|
| `inventory_preflight_manifest.json` | 1,867 | `afbc40aedbafde4f837acb29a8fdaf03831b53968f96ba0ab224f691fd414f49` |
| `source_allowlist_ledger.jsonl` | 51,879 | `ba2680ebcd7c76a16899673a446dba5b2dc1f60889b4d45d52776744b4e62827` |
| `model_tokenizer_inventory.jsonl` | 4,142 | `cb67300fc08460d51ea7b92ccd2db1f897983216d6e8dcc3df872dc082fabbec` |
| `evaluation_input_inventory.jsonl` | 2,938 | `db1652a284c8bae33ca8159329c93311bc1c3784e3123fa2c8072a987ed16eab` |
| `c1_reconciliation.jsonl` | 12,885 | `c8d5968bde15cdfd11dbd9db5d62186a5aaba9fded07e5711db305194385d3c8` |
| `inventory_report.json` | 3,004 | `b7b5661a8ac14476ac3d156d95baa9ebf709c6f13d5212bff5cc20c62fc2d08b` |
| `post_inventory_storage_audit.json` | 1,403 | `3de948681c136417f95a3c1fa6adcd036bed5586d1af613b82056183c2c784fa` |
| `final_inventory_audit.json` | 2,702 | `23ef2d0929a7b97ce3b9cf33c2108e39e335552678f63df4492c472a548cb503` |

`final_inventory_audit.json` was written last, hashes the seven earlier outputs only, and records
`self_hash_embedded=false`, `self_reference_excluded=true`, `written_last=true` and
`output_file_count_after_write=8`.

## 4. Inventory findings

- The two selected Qwen M1 metadata manifests were verified: `Qwen/Qwen2.5-1.5B`, seed 42
  step 75 and seed 43 step 50. The HU durability-fallback archive manifest was also verified.
  Tokenizer bytes read and large-weight rehash bytes were both zero.
- OLMo and Falcon were not inferred absent. Their artifacts were outside the closed allowlist and
  acquisition was not attempted.
- WikiText-2 and `trwiki-20260601` were inventoried stat-only. `trwiki-20260601` remains a
  cross-domain control, not the primary in-domain Turkish split.
- Existing compact vngrs/registry/reconciliation evidence was inspected only within the allowlist;
  C1 support is limited to identity, revision/stage when reported, and status/blocker when
  reported. No raw payload was exported.
- No selected adaptation-corpus artifact was present in the closed allowlist. Candidate paths were
  inventoried without recursive raw-text reads. No primary in-domain split was selected or
  materialized, and no split hash was fabricated.

## 5. Operational and scientific interpretation

The bounded operational inventory passed: all frozen zero-network, read-only-source, one-root,
output-count/byte, metadata-count/byte, and final-audit requirements were satisfied. The required
post-run storage audit reports `PASS`, `changed_source_paths=[]`, `source_roots_unchanged=true`,
`final_audit_self_reference=false`, and no HU-home write claim.

This is not a measurement result and does not authorize scoring, baseline evaluation, corpus
construction, training, or `ready_to_train`. The scientific inventory remains `BLOCKED` with
primary gate `blocked_by_measurement_design` and contributing blocker
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure=false` and
`ready_to_train=false`.
