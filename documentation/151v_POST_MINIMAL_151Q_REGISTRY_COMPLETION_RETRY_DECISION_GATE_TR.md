# Document 151v — Post-151t Registry-Completion Retry Decision Gate (TR)

**Upstream contract:** Document 151t  
**Execution result:** Document 151u  
**151t SHA-256:** `63951ba5543c2c803e8466d0c43e0aace9637ca1239164dc1d9f5e49ea75f46b`  
**Decision:** **PASS — scoped registry completion**

## 1. Gate decision

Document 151t was executed once within its frozen limits. Document 151u records a complete
request-level ledger, exact raw artifact/file manifests, hashes, read-only first-wave
reconciliation, benchmark/model coverage registry and post-run storage audit. The exact EXAMS
missing artifact and all three corrected immutable Hugging Face model-card routes completed.

The 151t retry gate is therefore **PASS**. The narrow operational-access blocker for this
registry-completion component is closed. Documents 151r and 151s remain preserved historical
records of the earlier 151q execution; this gate does not silently rewrite them.

## 2. PASS checklist

| Contract requirement | Evidence | Decision |
|---|---|---|
| 151t hash verified before execution | local SHA `63951ba5543c2c803e8466d0c43e0aace9637ca1239164dc1d9f5e49ea75f46b` | PASS |
| HU storage/path/inode preflight | 151u preflight and storage audit | PASS |
| old root immutable | 91 files, 13,063,617 bytes, inventory SHA `4e06a47ddf58a81a3d6a86e4dc0dee75c0d123ff6b38dbda6d76e7be51daf3ad` before/after | PASS |
| exact EXAMS artifact | 38,208,781 bytes; SHA `96960451dd4c41f208ee5ab3bdbce8ea06ecd3506faa830e3ce61d316222c2f3` | PASS |
| three raw model-card rows | 3/3 complete, raw `text/plain` README bytes, final URLs/redirect chains recorded | PASS |
| request/retry/redirect bounds | 7 requests, 0 retries, 38,233,119 response bytes | PASS |
| manifests and coverage | 4 file/hash rows, 3 benchmark rows, 3 model rows, 6 coverage rows | PASS |
| post-run storage | retry root under `/vol/tmp2`; home-write scope none; bounds pass | PASS |

## 3. Current scientific state

This PASS is limited to the bounded metadata-registry completion described by 151t. It does not
close the global `blocked_by_measurement_design` gate. The following remain unresolved or outside
151t:

- benchmark overlap and contamination definitions;
- the remaining 713-versus-829 measurement scope and exact downstream interpretation;
- missing pattern/alias inventory;
- benchmark scoring and evaluator execution;
- Turkish-capability measurement and its precommitted decision thresholds.

No benchmark score, inference, model/tokenizer weight or snapshot access, corpus materialization,
GPU/Slurm work, training, cleanup or deletion occurred. `ready_to_train` is **false**. Documents
152--154 remain unauthorized and uncreated.

## 4. Authority transition

151t is no longer unexecuted: it has one completed bounded execution, recorded in 151u. Document
151v is the current post-retry decision gate for this narrow registry component. The first-wave
root remains immutable/read-only, and the retry root is retained as the new evidence location;
neither permits later overwrite or cleanup without a separate authorization. CulturaX remains
`excluded_access_blocked`, and no CulturaX--vngrs comparative selection is available.

The next scientific action requires a separately frozen measurement-design authority and explicit
authorization. This gate does not authorize Documents 151k/151l, 152--154, training, scoring or
any model/corpus execution.
