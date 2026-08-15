# 112 - Turkish Bridge Contract V2 Result And Training Decision

**Date:** 2026-07-21  
**Status:** PASS — Phase 109A contracts are frozen; the separate training-family preflight is now
permitted, but no training job has yet been submitted.

## 1. Execution Result

Commit `5ed176d472712dc496efad9e67c93760ecd5c3d6` was pushed, synchronized exactly on HU, and passed
the authoritative 44-test contract/training/model-manifest subset.

| Job | Role | Result |
|---:|---|---|
| 411194 | contract-family capacity/inode/path/input preflight | PASS; stderr empty |
| 411195 | append-only contract V2 materialization and post-run audit | PASS; one benign tokenizer warning |

Job 411195 wrote its terminal `status=contract_v2_ready` marker after all assertions and the
post-run storage audit. The job had already left the queue at inspection time. Slurm accounting
was temporarily unavailable from the login node because of a Munge/SlurmDB authentication error;
therefore no unsupported `sacct` state is claimed. The terminal launcher marker, complete manifest,
all expected artifacts, empty queue, and successful final audit establish operational completion.

## 2. Frozen Contract Hashes

```text
f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e  manifest.json
57d3c753eea638b73c5e28d41968895451a8bbe58ba65abc42e64769e2eb4ee3  dose_manifest.json
6b965591eb2786f29e6a6ad883247860372b71199f7f5dcbf293d976b27aeabf  train_documents.jsonl
586e3fd343c8c04fddcd5e9cdfb4a82ae8df221c5ea764500c76e7adf94b8e52  validation_documents.jsonl
```

The complete contract is approximately 13 MiB at:

```text
/vol/tmp2/yesildau/turkish_bridge_v1/contracts/v2
```

The manifest binds 16 generated artifacts and the frozen corpus manifest hash from Document 110.

## 3. Localization And Probe Result

| Metric | Result |
|---|---:|
| localized object IDs | 430 |
| frozen probes | 1,500 |
| normalized EN ambiguities within candidate family | 0 |
| normalized TR ambiguities within candidate family | 0 |

The accepted-answer policy remains canonical-only. Token lengths are nonzero:

| Model | EN min/max | TR min/max |
|---|---:|---:|
| Qwen | 1 / 6 | 1 / 12 |
| SmolLM2 | 1 / 7 | 1 / 14 |

Relation-specific distractor inventories were generated from the correct candidate families.

## 4. Eligibility Result

Eligibility uses only frozen pre-adaptation English evidence.

| Model/set | Eligible facts | Strict facts |
|---|---:|---:|
| Qwen update 50 | 497 / 500 | 496 / 500 |
| SmolLM2 selected endpoint | 359 / 500 | 198 / 500 |
| shared intersection | 357 / 500 | 196 / 500 |

SmolLM2 eligibility remains most limited for profession (42/100) and strongest for
field-of-study (91/100). Qwen's only eligibility losses are three residence facts; one additional
industry fact misses strict 8/8 while remaining eligible. These are frozen analysis strata and do
not alter adaptation data.

## 5. Dose And No-Cycling Result

The shared source pool is the first 1,000 ordered documents from the frozen, contamination-clean
Turkish Wikipedia train split. Its JSONL is 10,358,422 bytes.

| Model | Tokens including document EOS | Complete 512-token blocks |
|---|---:|---:|
| Qwen | 3,182,118 | 6,215 |
| SmolLM2 | 4,296,816 | 8,392 |

The low and full endpoints require respectively 512 and 2,048 blocks at an effective 16 blocks
per optimizer update. Both model-specific tokenizations therefore exceed the full step-128 budget
without cycling. Both training configs freeze `max_steps=128` and `save_steps=32`.

The common 256-document validation subset also passed:

| Model | Validation tokens | Validation blocks |
|---|---:|---:|
| Qwen | 652,664 | 1,274 |
| SmolLM2 | 904,920 | 1,767 |

The models receive the same raw document pool and the same model-token/update budget. Because
their tokenizers produce different block boundaries, cross-family runs are not claimed to see
identical token sequences; within-model endpoint and later treatment comparisons retain exact
budget matching.

## 6. Warning Classification

Stderr was not empty. It contains one Transformers warning that a single document tokenized to
53,841 tokens, exceeding the tokenizer metadata maximum of 8,192. This materialization performs no
model forward pass and deliberately tokenizes full documents before grouping them into 512-token
blocks. There was no indexing operation, OOM, truncation, failed assertion, or traceback. The
warning is therefore recorded as benign for contract construction, not silently described as
clean stderr. Training consumes only the generated 512-token blocks.

## 7. Storage Result

| Model | Weights | Estimated checkpoint with optimizer | Four checkpoints + final |
|---|---:|---:|---:|
| Qwen | 3.087 GB | 9.330 GB | 40.406 GB |
| SmolLM2 | 3.423 GB | 10.335 GB | 44.765 GB |
| Combined | — | — | 85.170 GB |

The frozen training-family reserve including 30% headroom is 110,721,074,308 bytes, approximately
103.1 GiB. A fresh training-family preflight must compare this number with current scratch capacity
and inode state immediately before submission.

Post-run checks reported HU home at approximately 8.0 GiB, `/vol/tmp2` with approximately 115 TiB
free and 3% inode use, and the contract at approximately 13 MiB on scratch. The only home files
above 500 MB are the three previously documented Conda/PyTorch/CUDA runtime libraries. No new
experiment artifact was written into home.

## 8. Decision And Next Step

Phase 109A is complete. The next authorized step is not M2 or M3. It is one coordinated bridge
training family:

1. prepare and test a dedicated two-model GPU launcher;
2. perform one fresh family preflight enumerating Qwen and SmolLM2 outputs, four checkpoints plus
   final per model, caches/logs/tmp, and the 110.72 GB reserve;
3. if the preflight passes, submit Qwen and SmolLM2 training in parallel from their frozen M1
   endpoints;
4. inspect startup GPU ownership, memory, path resolution, and stderr;
5. evaluate M1, low step 32, and full step 128 in EN→EN, TR→EN, TR→TR plus English/Turkish PPL;
6. apply the frozen Document 109 promotion rule and record both failures and successes.

No seed 43, Qwen retention remediation, 500-subject scale-up, M2, or M3 is authorized by this
result alone.
