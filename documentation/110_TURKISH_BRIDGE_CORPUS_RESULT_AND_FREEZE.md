# 110 - Turkish Bridge Corpus Result And Freeze

**Date:** 2026-07-21  
**Status:** PASS — corpus finalized and frozen; bridge training remains HOLD pending the remaining
Phase 109A contracts.

## 1. Result

The dated Turkish Wikipedia source `trwiki-20260601-pages-articles.xml.bz2` was downloaded,
officially checksum-verified, extracted, normalized, audited, filtered, exactly deduplicated,
contamination-scanned, deterministically split, manually reviewed, and append-only finalized.
All high-volume data, logs, caches, temporary files, and manifests are under:

```text
/vol/tmp2/yesildau/turkish_bridge_v1
```

No corpus, checkpoint, cache, or evaluation artifact was written to HU home.

## 2. Frozen Counts

| Metric | Count |
|---|---:|
| extracted documents | 684,703 |
| filtered documents | 505,100 |
| deduplicated documents | 505,016 |
| exact duplicates removed | 84 |
| clean retained documents | 504,287 |
| conservative contamination removals | 729 |
| retained flag-only documents | 285,303 |
| total match records | 1,550,180 |
| train documents | 494,253 |
| validation documents | 10,034 |
| verified retained synthetic full-name matches | 0 |

The 729 removals are approximately 0.14% of the deduplicated corpus. Manual review shows that many
are real-world name collisions with frozen synthetic full-name surfaces. Their removal is an
intentional conservative contamination policy, not evidence that the Turkish corpus states the
synthetic target facts.

## 3. Contamination Inventory And Review

The corrected Relation V2 inventory contains:

| Inventory item | Count |
|---|---:|
| total patterns | 65,717 |
| aggregated canonical-object surfaces | 713 |
| synthetic subjects | 5,000 |
| synthetic facts | 25,000 |
| exact declared training sentences | 20,000 |

The deterministic seed-42 review sampled 20 removed, 20 retained flag-only, and 20 clean documents.
The decisive-first review passed:

- 20/20 removed samples contained a visible decisive removal match and full-name rule;
- 20/20 flag-only samples contained no decisive match and only object-only visible rules;
- 20/20 clean samples contained no match;
- all documents had stable IDs and were bound to the frozen scan hashes.

Review artifact SHA-256:

```text
5a1ced0b691cd5849ce0a7fa017e0f1832f3338d8ad177787e0de597f7154a6b
```

Review decision SHA-256:

```text
993a6d0cd9b3c9cd52c96d5f2deba6d13957b3f73a61d56d10b3819915d2c6a5
```

## 4. Final Frozen Hashes

```text
d06ec3b129c040ca98d3a9bf72871fa6117d5cd7102bf6c29eae5b20a834f87d  train_documents.jsonl
15480c1f543acf6df7aac1b2a2ee15fdcb3a544814f0063a181bd7a9cb0ca4f8  validation_documents.jsonl
5a1ced0b691cd5849ce0a7fa017e0f1832f3338d8ad177787e0de597f7154a6b  contamination_review_sample_seed42.json
993a6d0cd9b3c9cd52c96d5f2deba6d13957b3f73a61d56d10b3819915d2c6a5  contamination_review_decision_seed42.json
108c72375bb253742831da3fafb9e4b4b7b736974cb3cf6ef13f9b0f167502f7  corpus_manifest_final.json
```

The finalization is append-only. Historical candidate manifests and checksum files were not
overwritten. The final manifest records `finalized: true`, `completion_status: finalized`, and Git
commit `8fe6bd5a5b9bb445962707c86ea3249efc4ba281`.

## 5. Job Evidence

| Job | Outcome |
|---:|---|
| 410148 | source through dedup completed; stopped at legacy Relation V1 contamination schema |
| 411178 | cancelled after shared-object match explosion; incomplete scratch temporaries removed |
| 411180 | corrected aggregation scan/split/report completed |
| 411181 / 411183 | post-run storage and large-home-file audits passed |
| 411188 / 411189 | corrected provenance and first deterministic review completed |
| 411190 / 411191 | decisive-first review refresh completed |
| 411192 | append-only finalization preflight passed |
| 411193 | finalization and all checksum validations passed; stderr empty |

The failed and corrected runs are retained in Documents 109 and 100 as scientific and operational
evidence. No failed partial scan was promoted into the frozen corpus.

## 6. Storage Closure

The final audit reported:

- HU home: approximately 8.0 GiB;
- `/vol/tmp2`: approximately 115 TiB free;
- `/vol/tmp2` inode usage: 3%;
- corpus tree: approximately 17 GiB on scratch;
- large home files: only three previously documented Conda/PyTorch/CUDA runtime libraries.

There is no new home-resident experiment artifact.

## 7. Decision And Next Work

The Turkish corpus component of Phase 109A is complete. This does not authorize bridge training by
itself. Before Phase 109B starts, freeze and validate:

1. the English/Turkish canonical-answer and alias mapping with relation-specific distractors;
2. Qwen-specific, SmolLM-specific, strict, and shared-intersection eligible fact sets from frozen
   pre-adaptation English evidence;
3. exact low/full adaptation documents, raw bytes, tokenizer-specific token counts, update counts,
   optimizer exposure, checkpoint schedule, and no-cycling policy;
4. absolute scratch output/cache/log/tmp paths, expected checkpoint sizes, combined family storage,
   and retention policy.

Only after these contracts pass may the Qwen update-50 and selected SmolLM M1 bridge jobs be
submitted. M2, M3, seed 43, retention intervention, and scale-up remain HOLD.
