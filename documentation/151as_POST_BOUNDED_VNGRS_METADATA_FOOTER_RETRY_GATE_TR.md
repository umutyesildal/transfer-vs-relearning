# Document 151as — Post-Bounded vngrs Metadata/Footer Retry Gate (TR)

**Date:** 2026-08-09 (Europe/Berlin)  
**Status:** `BLOCKED — ROUTE INTEGRITY`  
**Execution result:** Document 151ar

## 1. Decision scope

Document 151an was executed exactly once after the preserved dirty HU state was verified, the
reviewed code was fast-forwarded and all pre-source gates passed. Documents 151an, 151ao, 151ap
and 151aq remain unchanged. This gate does not authorize another execution, route repair, corpus
access or training.

## 2. Gate reconciliation

| Gate component | Result | Evidence |
|---|---|---|
| HU dirty-state preservation | PASS | 42 entries, 39 `.D` + 3 `?`; status SHA-256 unchanged at `71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9` |
| code publication | PASS | one `fetch origin corpus-update`; one `merge --ff-only`; HU HEAD `c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23` |
| path overlap safety | PASS | 0 overlap between preserved paths and 13 incoming paths |
| storage/path/inode preflight | PASS | home `15032385536` B < `32212254720` B; root absent; all commands exit 0 |
| independent PyArrow writer/parser | PASS | PyArrow 24.0.0; 2 rows; 1 row group; parser PASS |
| frozen route/header request | BLOCKED | first request returned non-retryable HTTP 302 |
| 151an package validator | NOT REACHED | no package existed after fail-closed source stop |
| post-run audit | PASS | root absent; 0 files; 0 bytes; status unchanged |

## 3. Decision

```text
decision = BLOCKED
primary narrow blocker = route_integrity / non_retryable_http_302
operational gate = blocked_by_operational_access
global gate = blocked_by_measurement_design
ready_to_measure = false
ready_to_train = false
```

The frozen direct immutable `/resolve/` route produced an HTTP 302 to a CDN. The executor did not
follow the redirect because the 151an contract requires direct route and redirect-chain evidence
within the frozen route vocabulary. The result does not prove that the source is unavailable; it
proves only that this frozen route attempt is not contract-compliant in the observed environment.

The one allowed attempt consumed no retained response bytes, created no evidence artifact and
performed no retry. The successful preflight and fast-forward close the earlier HU checkout
blocker, but they do not close the route-integrity blocker or the global measurement-design gate.

## 4. Required next authorization

No automatic retry is authorized. Any future work must first prepare and separately freeze a route
correction that preserves immutable revision/path identity, direct-versus-redirect semantics,
response-byte accounting and the existing no-corpus-row scope. A new execution would require a
new explicit authorization after that contract correction. Nothing in this gate authorizes
151ah/151ak, corpus materialization, benchmark scoring, evaluation, model/tokenizer access,
GPU/Slurm, training or Documents 152–154.

## 5. Preserved artifacts and hashes

```text
151an = 937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79
151ao = 5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46
151ap = aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468
151aq = 5a48d297ef5475550df41fd7e2baace4278acf54bbfb32bbfe455909dde7dbea
```
