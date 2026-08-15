# Document 151u — Minimal 151q Registry-Completion Retry Execution Result (TR)

**Execution date:** 2026-08-07 (Europe/Berlin; evidence timestamps are UTC)  
**Contract:** Document 151t  
**Document 151t SHA-256:** `63951ba5543c2c803e8466d0c43e0aace9637ca1239164dc1d9f5e49ea75f46b`  
**Execution root:** `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1`  
**Result:** **PASS — bounded registry-completion retry only**

## 1. Scope and authorization

Under the user's single explicit authorization, corrected Document 151t was executed exactly
once. The execution was limited to the four frozen logical requests, first-wave read-only
reconciliation, new retry-root evidence, and the mandatory post-run storage audit. Documents
151q, 151r, 151s and the first execution root were not overwritten or modified.

The following were not performed: benchmark scoring, inference, model/tokenizer weight or
snapshot access, corpus materialization, GPU/Slurm work, training, cleanup, deletion, migration,
HU-home writes, or Documents 151k/151l/152--154 work.

## 2. Preflight and immutable-root reconciliation

The mandatory HU preflight completed before creating the retry root:

| Check | Observed result |
|---|---|
| `du -xsh /vol/fob-vol6/mi25/yesildau` | `14G` |
| `/vol/tmp2` capacity | `140T` total, `27T` used, `113T` available, `19%` |
| `/vol/tmp2` inode use | `3%` |
| home capacity/inode use | `53%` |
| old root resolved path | `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1` |
| retry root before execution | absent |
| old-root files/bytes | `91` / `13,063,617` |
| old-root inventory SHA-256 | `4e06a47ddf58a81a3d6a86e4dc0dee75c0d123ff6b38dbda6d76e7be51daf3ad` |

The old-root inventory hash exactly matched the frozen 151t reference before and after the
wave. The retry root resolved under `/vol/tmp2`; no first-wave bytes were copied. The
91-record `reconciliation/first_wave_reuse_ledger.jsonl` is a read-only ledger of the original
files and hashes.

## 3. Frozen request execution

The four logical requests were issued in the exact precomputed order. Redirects count as HTTP
requests and are retained in the request ledger; they are not retries.

| Logical request | HTTP evidence | Retained result |
|---|---|---|
| `retry-0001` EXAMS | `200`, no redirect, retry `0` | `38,208,781` bytes; SHA-256 `96960451dd4c41f208ee5ab3bdbce8ea06ecd3506faa830e3ce61d316222c2f3` |
| `retry-0002` OLMo README | `307` then `200`, retry `0` | `12,892` bytes; SHA-256 `8e09b3ce741d945b340e51530dd95f49c646a210d0342b1a831a19e36928758b` |
| `retry-0003` Falcon README | `307` then `200`, retry `0` | `7,596` bytes; SHA-256 `a82d599ab4c07663931273f23463ebb6030426a911b95230a42201e0b4954b63` |
| `retry-0004` Qwen README | `307` then `200`, retry `0` | `3,850` bytes; SHA-256 `84cc3bdbfd781149913126b70981cf1e341176fe4bc9d878601a83f18b035ddf` |

The model-card responses had `text/plain; charset=utf-8` content type. Their final response URLs,
ordered redirect chains, content types, transferred bytes and response SHA-256 values are recorded
in `requests/retry_request_ledger.jsonl` and `manifests/retry_hash_ledger.jsonl`. The redirects
resolved to Hugging Face `api/resolve-cache` paths retaining the requested repository and frozen
revision; the retained bytes were raw README bytes, not HTML presentation pages.

The exact EXAMS archive was retained without extraction or materialization. Its frozen commit and
path are recorded in the request and file manifests.

## 4. Bound and manifest verification

| Metric | Observed | Frozen limit | Decision |
|---|---:|---:|---|
| HTTP requests, including redirects | 7 | 8 | PASS |
| retries | 0 | 4 | PASS |
| response-transferred bytes | 38,233,119 | 67,108,864 | PASS |
| regular files before final audit file | 15 | 64 | PASS |
| retry-root bytes before final audit file | 38,313,488 | 134,217,728 | PASS |
| wall-clock time reported by execution script | 2.937 s | 900 s | PASS |

The required request ledger contains 7 attempt rows. The required record-level file manifest
contains 4 newly retained artifacts; the hash ledger contains the matching 4 hashes. The retry
benchmark registry contains TurBLiMP, TurkishMMLU and EXAMS rows; the retry source-model registry
contains all three model-card rows; the coverage matrix contains 6 required coverage rows. No
duplicate source row/document ID, response-dependent selection, failed-page replacement, bound
violation or unauthorized write was observed.

## 5. Post-run storage audit

The post-run audit was written to
`reports/retry_post_run_storage_audit.json` after the evidence/report files were generated.

- HU home remained `14G`; the audit found 5 regular files over 500 MiB, but this wave had no
  home-write scope and created no home artifact.
- `/vol/tmp2` remained at `19%` capacity and `3%` inode use in the post-run `df`/`df -i` output.
- The first execution root remained `91` files, `13,063,617` bytes and the same inventory SHA-256.
- The retry root remained under `/vol/tmp2`; its final post-audit inventory contained 16 regular
  files totaling `38,315,850` bytes. The audit's pre-audit-file inventory was 15 files and
  `38,313,488` bytes with inventory SHA-256
  `7c62e12dc51d9784bb3a261ce757a12947104ae1b7d91dd834363b99c0a92d20`.
- No cleanup, deletion, overwrite or migration was performed.

## 6. Result and remaining gates

The 151t retry result is **PASS**. The narrow registry-completion operational blocker from 151s
is closed for the exact EXAMS/model-metadata scope covered here. This does not rewrite 151r/151s;
they remain chronological records of the earlier 151q execution and its fail-closed gate.

The global scientific gate remains `blocked_by_measurement_design`. Outside this retry's scope are
benchmark overlap/contamination definitions, the remaining 713-versus-829 measurement scope,
the missing pattern/alias inventory, benchmark scoring/evaluator execution, and Turkish-capability
measurement. `ready_to_train` remains `false`; this successful metadata retry does not authorize
training or Documents 152--154.

**Evidence locations:**

- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/contracts/retry_preflight_manifest.json`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/requests/retry_request_plan.json`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/requests/retry_request_ledger.jsonl`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/manifests/retry_file_manifest.jsonl`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/manifests/retry_hash_ledger.jsonl`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reconciliation/first_wave_reuse_ledger.jsonl`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_benchmark_registry.jsonl`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_source_model_registry.jsonl`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_coverage_matrix.jsonl`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reports/retry_registry_completion_report.json`
- `/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reports/retry_post_run_storage_audit.json`
