# 111 - Turkish Bridge Contract V2 And Execution Gate

**Date:** 2026-07-21  
**Status:** IMPLEMENTED LOCALLY; HU materialization pending. Bridge training remains HOLD.

## 1. Purpose

This document freezes the remaining Phase 109A contracts required before the Qwen and SmolLM2
Turkish bridge pilot. The corpus itself is already final under Document 110. This step does not
train either model; it creates compact, hash-bound registries and exact training inputs from the
frozen evidence.

The earlier scratch `contracts/v1` tree is preserved as historical evidence but is superseded.
Its eligibility content was numerically valid, while some provenance paths still named their old
HU-home locations after the large artifacts had been migrated to scratch. V2 is append-only,
refuses overwrite, resolves every large input to approved scratch, and writes normalized model and
tokenizer manifests into the new contract.

## 2. Frozen Model Endpoints

| Label | Frozen M1 endpoint | Pre-adaptation English evidence |
|---|---|---|
| Qwen | Qwen2.5-1.5B update 50 | checkpoint-Pareto hard suite |
| SmolLM2 | selected Document 104 final model | canonical-form-diversity hard suite |

The Qwen checkpoint does not itself contain tokenizer files. Training and contract construction
therefore use its frozen manifest's `tokenizer_source_path_absolute` fallback. The generic CLM
trainer is corrected to honor the same fallback already used by evaluation code.

## 3. Localization And Candidate Contract

V2 freezes, before Turkish adaptation outcomes are observed:

- one canonical English and one canonical Turkish surface per object ID;
- a canonical-only accepted-alias policy for this pilot, with no post-outcome alias expansion;
- project normalization plus NFC-normalized comparison surfaces;
- per-model English and Turkish answer token lengths;
- a failure if any canonical answer tokenizes to zero tokens;
- relation-specific candidate families and the rule that every other object ID in the correct
  relation family is a distractor;
- 1,500 immutable probes: 100 subjects × 5 relations × EN→EN, TR→EN, and TR→TR.

The canonical-only choice is deliberately conservative. Free-generation alias expansion can be
added only in a separately versioned exploratory analysis, not after seeing pilot outcomes.

## 4. Frozen Eligibility Contract

Eligibility is computed only from pre-adaptation English hard-suite evidence:

- eligible fact: correct rank 1 and positive correct-vs-distractor margin in at least 3 of the 4
  held-out Form C/D cells;
- strict fact: the same condition in all 8 required Form A/B/C/D × scaffold cells;
- subject sensitivity set: at least 4 of its 5 facts are eligible;
- shared set: fact-ID intersection across the Qwen and SmolLM2 eligible sets.

The expected frozen counts, to be asserted on HU, are:

| Set | Eligible facts | Strict facts |
|---|---:|---:|
| Qwen update 50 | 497 | 496 |
| SmolLM2 selected endpoint | 359 | 198 |
| shared eligible intersection | 357 | materialized separately |

These sets are analysis strata; they do not alter the Turkish adaptation documents.

## 5. Matched Low/Full Dose Contract

Both models consume the same ordered raw-document prefix from the frozen Turkish Wikipedia train
JSONL. Tokenization necessarily differs by model, so V2 records tokenizer-specific token and
grouped-block counts while preserving identical raw documents.

| Quantity | Frozen value |
|---|---:|
| block size | 512 model tokens |
| per-device batch | 2 blocks |
| gradient accumulation | 8 |
| world size | 1 |
| effective exposure per optimizer step | 8,192 model tokens |
| low endpoint | step 32 = 262,144 model tokens |
| full endpoint | step 128 = 1,048,576 model tokens |
| checkpoint interval | 32 steps |
| seed / data seed | 42 / 42 |
| loss | full-sequence CLM |
| learning rate | 1e-5 |

Raw rows are accumulated in the same 1,000-document mapping batches used by the Hugging Face
dataset pipeline until both tokenizers yield at least 2,048 complete 512-token blocks. No data
cycling is permitted before step 128. The same frozen 256 validation documents are materialized
for both models, with nonzero tokenizer-specific validation block counts asserted.

## 6. Storage And Retention Contract

All contract data, model inputs, caches, temporary files, Slurm logs, checkpoints, and evaluation
outputs stay under `/vol/tmp2/yesildau/turkish_bridge_v1`. HU home contains only source, Git data,
small configuration, and compact documentation.

The materializer estimates each model's checkpoint from frozen model-weight bytes as three times
model weights plus 64 MiB for optimizer/trainer overhead, expects four step checkpoints plus one
final model per model, and adds a 30% family reserve. The later training-family preflight must
compare this computed reserve against current capacity and inodes and enumerate both output roots.

During training, resumable state remains on scratch. After evaluation, retain model-only low
step-32 and full step-128 endpoints plus configs, tokenizer, compact metrics, manifests, and
SHA-256 hashes. Intermediate optimizer/trainer state is eligible for cleanup only after selected
artifacts and evidence are verified.

## 7. Implementation And Verification

The implementation adds:

- `scripts/prepare_turkish_bridge_contract_v2.py`;
- a dedicated contract-v2 storage/path preflight;
- a dependent CPU materialization launcher;
- tokenizer-manifest fallback support in the CLM trainer;
- reusable localization distractor and shared-dose utilities with tests.

The materializer preserves a failed partial contract under a job-specific scratch failure path,
rather than silently deleting evidence or blocking a corrected retry at the canonical V2 path.
Local verification passes the full available suite: 178 passed and 4 optional environment tests
skipped, with clean Python compilation, shell syntax, and Git whitespace checks.

## 8. Execution Order And Gate

1. Commit and push the narrow implementation.
2. Fast-forward HU to the exact commit and run authoritative tests.
3. Submit one fresh contract-family preflight.
4. Submit one materialization job with `afterok` dependency.
5. Inspect the generated V2 manifest, hashes, counts, tokenizer lengths, dose counts, validation
   blocks, model paths, and computed storage reserve.
6. Record the job IDs, final states, stderr, artifact hash, and post-run audit.
7. Only if all checks pass, prepare a separate two-model training-family preflight and submit the
   Qwen and SmolLM2 bridge jobs in parallel.

M2, M3, seed 43, retention intervention, 500-subject scale-up, and any final-scale training remain
HOLD. A V2 contract failure authorizes correction and a new append-only version or retry; it does
not authorize relaxing gates after seeing an outcome.

## 9. HU Submission Record - 2026-07-21

The implementation was committed and pushed as `5ed176d`, then HU was fast-forwarded to exact
commit `5ed176d472712dc496efad9e67c93760ecd5c3d6`. The authoritative 44-test contract/training/model-
manifest suite passed. Historical artifact deletions and the `artifacts`/`runs` symlink migration
state were left untouched.

One dependent contract wave was submitted:

| Job | Role | Observed state |
|---:|---|---|
| 411194 | home/capacity/inode/path and frozen-input preflight | PASS; stderr empty |
| 411195 | append-only V2 materialization | RUNNING on `gruenau3`; initial stderr 0 bytes |

Preflight 411194 recorded HU home at 8,297,732 KiB (approximately 7.91 GiB), `/vol/tmp2` with
123,131,924,480 KiB available (approximately 115 TiB) and 3% inode use, zero checkpoints for this
CPU-only step, and less than 1 GiB new output. `artifacts`, `runs`, and the V2 destination all
resolved to approved scratch. The next action is to inspect 411195 after approximately 5--10
minutes. Do not submit a duplicate. Bridge training remains HOLD.

Job 411195 subsequently completed and wrote `status=contract_v2_ready`; the complete result,
artifact hashes, eligibility counts, dose counts, warning classification, storage estimate, and
next decision are frozen in Document 112. Phase 109A is PASS. A separate two-model training-family
preflight is now permitted, but no training job has yet been submitted.
