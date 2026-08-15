# Document 151an — BOUNDED VNGRS ROUTE, FOOTER, BYTE AND SAMPLING-SCHEDULE EVIDENCE RESOLUTION CONTRACT (TR)

## 1. Amaç, statü ve kapsam

Bu belge yalnızca Document 151ak'nın execution öncesi çözülmemiş source-evidence, route/footer,
byte-binding ve deterministic sampling-schedule boşluklarını kapatmak için hazırlanmış minimal,
frozen ve **unexecuted** bir resolution contract'tır. Bu belge bu turda çalıştırılmamıştır ve
çalıştırılmasını yetkilendirmez.

```text
status                 = FROZEN — UNEXECUTED — PREPARATION_BLOCKED
source_access          = not performed by this preparation task
network                = not used by this preparation task
151ah/151ak execution  = forbidden
result/gate documents  = 151ao/151ap reserved, not created
primary gate           = blocked_by_measurement_design
ready_to_measure      = false
ready_to_train        = false
```

No HU/SSH, network, corpus-row or shard access, full download, materialization, scoring, inference,
model/tokenizer access, GPU/Slurm, training, cleanup, deletion, overwrite or Documents 152–154
operation is authorized. A later execution requires a separate explicit authorization that names
this exact contract and its then-current SHA-256.

## 2. Immutable source identity and exact candidate path set

The route-resolution wave may inspect only this source identity, and may not substitute a release,
split, schema or revision:

```text
source_repository  = vngrs-ai/vngrs-web-corpus
immutable_revision = ee5c6201ee84457a18182bfc483a7d8a7f3655ba
split              = train
schema             = text / corpus / original_id
license            = CC BY-NC-SA 4.0
total_shards       = 284
selected_shards    = 32
selection_version  = vngrs_systematic_midpoint_32_of_284_v1
selection_formula  = floor((rank + 0.5) * total_shards / selected_shards)
selection_payload_sha256 = dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686
```

The ordered path set is frozen before any request:

```text
data/train-00004-of-00284.parquet
data/train-00013-of-00284.parquet
data/train-00022-of-00284.parquet
data/train-00031-of-00284.parquet
data/train-00039-of-00284.parquet
data/train-00048-of-00284.parquet
data/train-00057-of-00284.parquet
data/train-00066-of-00284.parquet
data/train-00075-of-00284.parquet
data/train-00084-of-00284.parquet
data/train-00093-of-00284.parquet
data/train-00102-of-00284.parquet
data/train-00110-of-00284.parquet
data/train-00119-of-00284.parquet
data/train-00128-of-00284.parquet
data/train-00137-of-00284.parquet
data/train-00146-of-00284.parquet
data/train-00155-of-00284.parquet
data/train-00164-of-00284.parquet
data/train-00173-of-00284.parquet
data/train-00181-of-00284.parquet
data/train-00190-of-00284.parquet
data/train-00199-of-00284.parquet
data/train-00208-of-00284.parquet
data/train-00217-of-00284.parquet
data/train-00226-of-00284.parquet
data/train-00235-of-00284.parquet
data/train-00244-of-00284.parquet
data/train-00252-of-00284.parquet
data/train-00261-of-00284.parquet
data/train-00270-of-00284.parquet
data/train-00279-of-00284.parquet
```

The path set is an exact selection identity, not proof that the files, footer values, license
bytes or route responses have been retrieved. No response-dependent shard replacement or extra
shard is permitted.

## 3. Frozen official route forms and route-choice decision

The later resolution wave must record exact immutable URLs, not wildcard paths. The only permitted
official route forms are:

```text
immutable_tree_route =
https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/tree/ee5c6201ee84457a18182bfc483a7d8a7f3655ba/data

parquet_resolve_route(path) =
https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/resolve/ee5c6201ee84457a18182bfc483a7d8a7f3655ba/<path>?download=true

rows_route(offset, length) =
https://datasets-server.huggingface.co/rows?dataset=vngrs-ai/vngrs-web-corpus&config=default&split=train&offset=<offset>&length=<length>
```

The two data-access alternatives are mutually exclusive for the final wave:

1. **`/rows` route:** use only if the official response binds to the exact selected path, the
   route reports the frozen revision/split, all schedule windows satisfy exact row bounds, the
   complete midpoint schedule fits within 100 successful row requests, and every response stays
   within the request/byte ceilings below.
2. **bounded Parquet footer/range route:** use only if `/rows` cannot represent the schedule or
   cannot satisfy its response ceilings, and immutable Parquet responses provide exact footer
   row counts, row-group/byte ranges, schema, object identity and canonical record extraction
   evidence within the same ceilings. A range route may not silently change the row-count-weighted
   midpoint estimand or become a full-shard download.

The route-choice field must be one of `rows` or `parquet_footer_range`. If neither alternative
can be proven within the frozen bounds, the wave is `BLOCKED` and records the precise feasibility
contradiction. The current contract does not claim that either route has been resolved.

## 4. Exact sampling schedule and feasibility gate

The schedule is serialized before the first data request and is not derived from responses:

```text
target_records        = 10,000
allocation_rule       = largest_remainder_integer_then_lexicographic_path
position_rule         = floor((2*rank+1)*row_count/(2*sample_count))
request_mode          = contiguous_row_windows
max_rows_per_request  = 100
```

The schedule artifact contains:

```text
schedule_version
target_records
allocation_rule
position_rule
request_mode
max_rows_per_request
shards[] = {path, ordinal, exact_row_count, sample_count, sampled_positions[]}
schedule_sha256       # SHA-256 over every preceding field, excluding only itself
```

Exact footer `row_count` values are mandatory inputs; missing or guessed counts fail closed.
The integer allocation and every midpoint position are recomputed from the 32 selected rows.
Each successful request must bind to one source row and one route row and satisfy:
`0 <= offset`, `1 <= length <= 100`, and `offset + length <= exact_row_count`. Source windows
must be non-overlapping and non-duplicate. The record manifest must reproduce the exact scheduled
positions and exactly 10,000 unique source identities; arbitrary windows that happen to return
10,000 records are invalid.

Before request execution, compute the minimum number of contiguous windows of length at most 100
that cover all scheduled positions. If it exceeds 100, record
`sampling_schedule_infeasible_under_100_rows_requests`, stop before row retrieval and do not
replace the schedule. This is a design contradiction, not permission to increase the limit or
alter the estimand.

## 5. Required compact evidence artifacts and byte bindings

All evidence is compact and text-free with respect to corpus content. Each named artifact is
written once under a new explicit scratch root by a separately authorized wave. The exact artifact
bytes are hashed directly; a parent hash alone is never accepted.

### 5.1 Source-shard evidence ledger

Exactly one row per selected path, in frozen path order:

```text
path
ordinal
shard_count
exact_row_count
compressed_bytes
uncompressed_bytes
object_id
object_sha256
object_evidence_artifact
footer_sha256
footer_evidence_artifact
license_bytes_sha256
license_evidence_artifact
```

`object_evidence_artifact`, `footer_evidence_artifact` and `license_evidence_artifact` name
canonical compact byte payloads. The supplied bytes must hash to their corresponding fields. The
release license text/attribution bytes are captured separately from the Parquet object bytes.

### 5.2 Route ledger

Exactly one row per selected path:

```text
path
route_kind                 # /rows or parquet_footer_range
immutable_revision
split
route
status
route_evidence_artifact
route_evidence_sha256
redirect_chain
content_type
content_encoding
```

The route evidence artifact is the canonical compact request/route metadata payload, not a
placeholder hash. Its bytes are rehashed, and its route, revision, split, content type and
redirect chain must match the ledger. A `verified` status is forbidden when any binding is absent.

### 5.3 Request and record manifests

The request ledger separates response accounting from record bytes:

```text
request_id
attempt_id
attempt_ordinal
retry_ordinal
source_repo
immutable_revision
route
shard_path
row_range_or_metadata_target
request_start_utc
response_end_utc
http_status
response_transferred_bytes
response_evidence_artifact
content_encoding
content_type
redirect_chain
response_sha256
request_outcome
```

Each response artifact is named once and its exact bytes are rehashed. The record manifest retains
only exact serialized-record payload bytes and normalized-text SHA-256 at record grain; it must
not copy a full response byte count to every row or sum repeated response-level values.

## 6. Frozen request, byte and output ceilings

The later wave inherits these strict 151ak ceilings:

| Bound | Maximum | Fail-closed rule |
|---|---:|---|
| total HTTP attempts | 128 | any 129th attempt blocks |
| successful `/rows` requests | 100 | any 101st request blocks |
| retry attempts | 28 | any 29th retry blocks |
| total response bytes | 64 MiB | exceeded total blocks |
| one response | 4 MiB | exceeded response blocks |
| final unique records | exactly 10,000 | shortfall or duplicate identity blocks |
| selected shards | exactly 32 | extra/missing path blocks |
| output regular files | contract-defined compact set only | undeclared file blocks |

Request and record byte ledgers are reconciled independently. Any failed request replacement,
response-dependent selection, duplicate source identity, missing response payload, incomplete
retry chain, status/outcome mismatch, or bound hit fails closed.

## 7. Final audit and decision rules

The wave writes a named ordered output-artifact manifest and a final audit last. The manifest
contains only declared pre-audit artifacts and excludes itself and the final audit. The final audit
contains the contract SHA, selection/schedule SHA, source/route/response artifact sets, all request,
record and byte counts, route-choice result, feasibility result, blocker list, storage audit and
no-cleanup claim. It must not self-reference.

```text
PASS:
  exact route-choice evidence, source/footer/license bytes, schedule, 10,000-record manifests,
  request/response bindings, quality/LID/dedup/PII/contamination inputs and final audit all pass.

CONDITIONAL:
  only if all operational evidence passes and an explicitly external scientific blocker remains;
  never ready_to_measure or ready_to_train.

BLOCKED:
  any missing/unbound artifact, schedule mismatch, infeasible route envelope, duplicate/overlap,
  byte/request bound hit, incomplete target or audit-chain failure.
```

Even a PASS from this operational contract cannot close `blocked_by_measurement_design`, authorize
training, or create a selected adaptation corpus without the separate scientific authority.

## 8. Reservation and next authorization

Documents `151ao` and `151ap` are reserved for a future execution result and post-execution gate;
they are not created by this preparation task. No result or gate document may be drafted as if this
contract had run. A future request must explicitly authorize one bounded execution of this exact
frozen contract, identify the new scratch root, repeat the mandatory storage/path/inode preflight,
and preserve all prior evidence roots read-only.

Document 151an remains:

```text
FROZEN — UNEXECUTED — PREPARATION_BLOCKED
```

## 9. Append-only correction — metadata/footer feasibility execution profile (2026-08-08)

Bölüm 9, önceki metni silmeden ve yeniden yazmadan eklenmiştir; dar metadata/footer kapsamındaki
Section 1 ve Section 8 status ifadelerinin güncel authority karşılığıdır. Section 3'teki iki
route-choice alternatifi ve Section 5.2'deki eski `/rows` alanları tarihsel kayıt olarak korunur,
ancak bu dar wave için Bölüm 9'un tek `parquet_footer_range` route-kind ve doğrudan immutable
route kurallarıyla supersede edilir. Document 151an'ın bu düzeltmeden önceki SHA-256 değeri
`435e0c25cedd7fd8fcb70862c637040300c2d5b201bfb5fa25c2b20232e71096` olarak korunur. Aşağıdaki
execution-ready statüsü yalnızca metadata/footer feasibility scope'u için
geçerlidir; herhangi bir execution yetkisi değildir.

```text
current_status                  = FROZEN — UNEXECUTED — EXECUTION_READY_METADATA_FOOTER_ONLY
execution_authorization         = not granted by this document
primary_gate                    = blocked_by_measurement_design
contributing_gate               = blocked_by_corpus_selection_or_materialization
ready_to_measure                = false
ready_to_train                  = false
result_gate_documents           = 151ao/151ap reserved, not created
```

### 9.1 Wave boundary and immutable roots

The future wave is a **metadata/footer feasibility wave only**. It may retrieve and retain
compact metadata, immutable LFS/object identity evidence, response headers, bounded Parquet footer
bytes and exact license/attribution bytes. It must not retrieve corpus rows, compressed row-group
payloads or a full shard; it must not run LID, quality, PII, exact/near-dedup or calibration; and
it must not create a sample manifest. Any later row-retrieval/sample wave requires a separate
contract after this feasibility result.

```text
new_scratch_root        = /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
existing_evidence_roots = read-only; no overwrite, append or migration
HU_home                 = read-only
```

Before any future access, the executor must perform and record the mandatory HU storage/path/inode
preflight for HU home, `/vol/tmp` and `/vol/tmp2`, resolve the new root with `readlink -f`, verify
that it is on approved scratch, and fail closed on any path, capacity, inode or root mismatch.
No existing report, cache, sample, corpus, manifest or evidence file may be overwritten.

The only seven top-level outputs, in this order, are:

```text
selection_plan.json
shard_metadata_ledger.jsonl
route_ledger.jsonl
request_ledger.jsonl
evidence_artifact_manifest.jsonl
feasibility_projection.json
metadata_footer_audit.json
```

The manifest may name only compact evidence files under the same new root. Total regular files and
new inodes are each bounded by `128`; no undeclared file, wildcard output or full-shard fallback is
permitted. The named artifact manifest is written before `metadata_footer_audit.json`; it excludes
itself and the final audit. The final audit is self-reference-free and is written last.

### 9.2 Frozen route and request vocabulary

The only source route is the exact immutable direct-file form

```text
https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/resolve/ee5c6201ee84457a18182bfc483a7d8a7f3655ba/<selected_path>?download=true
```

where `<selected_path>` is one of the 32 already frozen paths in Section 2. The only route-kind
value in all route and request ledgers is:

```text
route_kind = parquet_footer_range
```

`route_kind` is a categorical field and is never substituted for `request_url`. Footer requests
use `GET`, `Range: bytes=-65536`, and must receive a bounded `206` response whose exact response
bytes end in the Parquet `PAR1` marker. Metadata/header checks use `HEAD` on the same exact direct
URL without a range header. License bytes use `GET` on the exact immutable README resolve URL and
are kept in a separate `license_attribution_bytes` artifact. Redirects, hosts, revisions, paths,
content types and encodings are recorded and must remain within this allowlist.

The Dataset Viewer `/rows` route is not part of this wave. Its dataset/config/split/offset/length
shape cannot itself bind the frozen immutable revision and selected shard, so `/rows`,
`datasets-server`, wildcard routes and response-dependent route selection fail closed. The 151ak
validator remains a row-wave validator and must not claim Parquet extraction support.

### 9.3 Separate object identity, compact evidence and forbidden payloads

Each selected shard row must include `object_id`/`object_id_kind` (immutable LFS identity),
`object_size_bytes`, optional full-object `object_sha256`, and an explicit
`object_sha256_status`. The canonical compact object-metadata payload is a different artifact and
is bound by `object_metadata_evidence_sha256`; its SHA-256 must never be compared with the full
Parquet object SHA. In a footer-only wave, full-object SHA verification is
`unverified_footer_only` unless a separately evidenced authoritative LFS identity is available.

`footer_sha256` binds the actual retained bounded footer bytes, and `license_bytes_sha256` binds
the exact retained license/attribution bytes. Artifact kinds are restricted to
`object_metadata`, `route_headers`, `parquet_footer_bytes` and `license_attribution_bytes`.
`corpus_rows`, `compressed_row_group`, `full_shard`, model weights and tokenizer snapshots are
forbidden artifact kinds and any occurrence fails closed.

### 9.4 Pre-row schedule and feasibility projection

The executor must serialize the existing row-count-weighted midpoint schedule before any possible
later row request, using the exact 32 real footer `row_count` values and row-group layout. It must
recompute allocation, midpoint positions, minimum contiguous windows/ranges, projected HTTP
request count, projected total response bytes and projected maximum response bytes. The structural
fixture's `373` windows is fixture-only evidence: it neither represents real source values nor
changes the frozen estimand. Missing, guessed or contradictory footer values fail closed.

The feasibility projection must declare `metadata_footer_only=true`,
`corpus_rows_retrieved=0`, `sample_manifest_created=false`, bind the schedule SHA-256 and report
the actual metadata/footer request and byte totals. A later row wave may be blocked by the real
schedule's request envelope; it may not alter the allocation, positions or estimand after seeing
the footer results.

### 9.5 Frozen ceilings and decision scope

The future wave freezes `128` total HTTP attempts, `28` total retries, `4 MiB` maximum single
response, `64 MiB` maximum total response bytes, `7,200` seconds maximum wall-clock duration,
`128` regular output files and `128` new inodes. It has no row-success target because rows are
forbidden. Any bound hit, duplicate path, duplicate source identity, missing/contradictory
revision or LFS identity, missing artifact bytes, footer/hash mismatch, forbidden payload,
manifest mismatch, route mismatch or audit-chain failure is `BLOCKED`.

For this narrow scope, `EXECUTION_READY` means that a separately authorized future executor may
perform only the bounded metadata/footer feasibility wave. It does not close
`blocked_by_measurement_design`, select/materialize vngrs, authorize 151ah/151ak, authorize
training, or create Documents 152–154. Documents 151ao and 151ap remain reserved and uncreated.

## 10. Append-only correction — strict footer/parser/ledger byte-integrity protocol (2026-08-08)

This section is append-only. The preceding Sections 1–9, including their historical route
alternatives and the pre-correction status, remain preserved. The pre-correction SHA-256 of this
document is `572a14636dfc44f23cdff5ac536838ea671a488ddcd24968097bc4942bb0d4e4`. This correction
was performed locally only; no HU/SSH, network, public metadata, source/footer access or 151an
execution occurred. It closes the local implementation and evidence-binding gaps without creating
Documents 151ao/151ap.

### 10.1 Complete Parquet footer framing and parser identity

The frozen parser is the pure-Python standard-library implementation identified as
`vngrs_parquet_footer_compact_thrift_parser_v1`. No optional dependency may be silently skipped.
It must parse, rather than suffix-check, a complete Parquet footer range:

1. The final eight bytes are exactly four little-endian unsigned bytes of metadata length followed
   by the four-byte `PAR1` magic.
2. The declared metadata length is positive, the complete payload is exactly
   `metadata_length + 8` bytes, and no undeclared prefix or trailing bytes are accepted.
3. The metadata is decoded as Parquet `FileMetaData` in Thrift compact protocol. The parser derives
   total `row_count`, `row_group_count`, every row-group `row_count`, compressed and uncompressed
   byte totals, file offsets and column-chunk counts from parsed metadata.
4. The shard ledger, schedule and projection are compared to these parsed values. Caller-supplied
   row counts, row-group counts, layouts or byte totals are never authoritative.
5. Truncated trailers, false `PAR1`, inconsistent metadata lengths, malformed compact metadata and
   fabricated row counts/layouts fail closed.

The accepted complete footer bound is `4 MiB`, independent of the historical suffix range. The
two-stage protocol is therefore:

```text
stage 1: GET  Range: bytes=-8
stage 2: GET  Range: bytes={object_size_bytes - (metadata_length + 8)}-
```

The first response must be an exact eight-byte trailer. The second response must contain the exact
complete declared metadata plus trailer and reconcile its exact `Content-Range` to the immutable
object size. The request ledger records both roles separately; an executor may not assume that all
footers fit in 65,536 bytes. Every range header, status, content length, final URL, redirect chain,
content type, content encoding, ETag and LFS OID is validated against the route and shard ledgers.

### 10.2 Shared HEAD and retry/response accounting

One immutable direct-file `HEAD` may serve both object-metadata and route-header roles only as the
single named `head_metadata_route` artifact when the exact bytes and SHA-256 are identical. Its
canonical payload must bind the path, immutable revision, LFS/object ID, object size, request and
final URLs, empty redirect chain, status, ETag, content type and encoding. Arbitrary JSON is not
accepted as evidence.

`request_id` identifies a logical request and may repeat across attempts. Every `attempt_id` is
unique. For each logical request, `attempt_ordinal` and `retry_ordinal` are contiguous zero-based
sequences, the method/path/URL/route-kind/range foreign keys remain stable, retryable failures
precede the terminal attempt, and exactly one successful terminal attempt exists. Retries are
counted once as `number_of_attempt_rows - number_of_logical_requests`.

For every response artifact, `response_transferred_bytes` equals the actual supplied payload length,
`response_content_length` equals that same length, and `response_sha256` is recomputed over those
bytes. Request-level response bytes are never copied into record rows and are never multiplied by
the number of logical records. Missing, mismatched, unlinked or duplicate artifact bindings fail
closed.

### 10.3 Canonical manifest and final-audit binding

`evidence_artifact_manifest.jsonl` is the canonical JSONL serialization of the supplied manifest
rows, in their declared order. Its bytes, SHA-256, artifact paths, artifact kinds and byte lengths
must agree with every shard, route and request binding. The manifest excludes itself and
`metadata_footer_audit.json`.

`metadata_footer_audit.json` is written last and is bound to its supplied canonical JSON bytes. It
must contain the corrected 151an contract SHA, manifest SHA, exact artifact paths/count/bytes,
request and retry totals, response byte totals, output-file and inode counts, scratch root and the
frozen top-level write order. It must be self-reference-free; an arbitrary payload with a matching
caller hash, an unbound audit, a manifest hash-only update or a changed write order is invalid.

### 10.4 Reconciled bounded execution profile and gate

For the exact 32 selected shards plus one immutable license artifact, the nominal no-retry profile
is `97` logical requests and `97` evidence artifacts: one shared HEAD, one eight-byte trailer
range and one complete-footer range per shard, plus one license request. With the seven declared
top-level outputs, the nominal projection is `104` regular files and `104` new inodes. The hard
ceilings remain `128` total HTTP attempts, `28` retries, `64 MiB` total response bytes, `4 MiB`
per response, `7,200` seconds, `128` regular files and `128` new inodes. Any ceiling hit, route or
path mismatch, malformed header, duplicate identity, invalid retry chain, byte/hash mismatch,
incomplete footer, manifest mismatch or audit-chain failure is `BLOCKED`.

The corrected local implementation passed `36 passed, 1 skipped` in the focused
`tests/test_vngrs_preparation.py` suite and `266 passed, 8 skipped` in the compatible repository
suite with the same three documented collection exclusions. The tests include a real parseable
minimal footer fixture and fail-closed controls for truncated trailers, false magic, inconsistent
metadata lengths, fabricated row counts/layouts, malformed headers, invalid retry ordinals,
response-byte mismatch, unlinked manifest bytes and unbound audit bytes. These are local
implementation checks only. The contract remains:

```text
current_status          = FROZEN — UNEXECUTED — EXECUTION_READY_METADATA_FOOTER_ONLY
primary_gate            = blocked_by_measurement_design
contributing_gate      = blocked_by_corpus_selection_or_materialization
ready_to_measure        = false
ready_to_train          = false
result_gate_documents   = 151ao/151ap reserved and uncreated
```

Execution still requires a separate explicit authorization and the mandatory HU storage/path/inode
preflight. This correction does not authorize source access, route resolution, row sampling,
corpus materialization, scoring, inference, evaluation, GPU/Slurm, training, cleanup or any later
numbered document.

## 11. Append-only correction — retry semantics and worst-case artifact bounds (2026-08-08)

This section is append-only and preserves Sections 1–10 and their hashes as chronological
evidence. The pre-correction SHA-256 immediately before this addendum was
`e23ae18d35791e91d05f094fe7c675871214df6a9fe9714a660ae703fe84a0ac`. This is a local-only
correction: no HU/SSH, network, public route/source/footer access or 151an execution occurred.

### 11.1 Explicit retry state machine

Every request-ledger attempt now carries these frozen fields in addition to the existing request
and response fields:

```text
failure_class
retryable_error
response_present
```

The only successful state is `request_outcome=metadata_success` with
`failure_class=none`, `retryable_error=null` and `response_present=true`. A successful HEAD,
trailer or complete-footer attempt must satisfy its original `200`/`206`, exact-range, parser and
shard-ledger bindings.

The only retryable HTTP statuses are `429` and `503`, with matching error codes `http_429` and
`http_503`, `failure_class=http_retryable` and `response_present=true`. A response-bearing retry
must name a unique artifact under `evidence/retry/`, use artifact kind `retry_response`, and bind
the exact supplied payload length and SHA-256. It is not parsed or promoted to a terminal success
artifact merely because its bytes happen to resemble a valid metadata response.

The supported no-response transport states are `failure_class=transport_no_response` with
`retryable_error` equal to `transport_timeout` or `transport_connection_error`,
`http_status=null`, `final_url=null`, `response_present=false`, no response artifact, no response
SHA, `response_content_length=null` and `response_transferred_bytes=0`. This makes a transport
failure representable without inventing response bytes. A valid `200` or `206` attempt relabelled
as `retryable_failure` is rejected. Non-terminal attempts must be retryable failures, and each
logical request must end with exactly one successful terminal attempt.

### 11.2 Reconciled retry and artifact ceilings

The effective retry bound is reduced from the historical `28` to `24`. The total HTTP-attempt
ceiling remains `128`; the response-byte, single-response, wall-clock and top-level output limits
remain unchanged. The worst-case retained-artifact arithmetic is now internally consistent:

```text
base response artifacts                 = 97
maximum response-bearing retry artifacts = 24
declared top-level output files          = 7
maximum regular files and new inodes     = 128
```

No-response transport retries consume an attempt and retry allowance but no response-artifact
file. Every response-bearing retry consumes exactly one unique `retry_response` artifact. The
feasibility projection, artifact manifest, request/retry totals and final audit must all be
recomputed from the same rows and bytes. A 25th retry, a 129th file/inode, an unbound retry
artifact or a mismatch in any derived total is `BLOCKED`; the contradictory `28 retries / 132
files` profile is no longer effective.

### 11.3 Local controls and independent-writer compatibility

The local tests include a positive chain with one real `429` response-bearing retry followed by a
terminal success, a positive no-response transport retry, an exact 24-retry/128-file/inode
boundary, a 25-retry overflow, and a negative relabelled-success control. Request totals, retry
counts, artifact-manifest bytes, feasibility projection and final-audit bytes are mutually
recomputed in each control.

An independent-writer compatibility preflight is also defined using PyArrow when available. PyArrow
was unavailable in this local environment, so that test is explicitly skipped; the handcrafted
compact-Thrift fixture is not claimed as independent-writer evidence. The executor must run the
independent-writer preflight before any source/footer request and fail closed if it is unavailable
or fails at execution time.

The corrected local test record is `40 passed, 2 skipped` for the focused suite and `270 passed,
9 skipped` for the compatible suite with the same three documented collection exclusions plus the
explicit independent-writer compatibility skip. The contract remains:

```text
current_status          = FROZEN — UNEXECUTED — EXECUTION_READY_METADATA_FOOTER_ONLY
max_total_http_attempts = 128
max_total_retries       = 24
max_output_files        = 128
max_new_inodes          = 128
primary_gate            = blocked_by_measurement_design
contributing_gate       = blocked_by_corpus_selection_or_materialization
ready_to_measure        = false
ready_to_train          = false
result_gate_documents   = 151ao/151ap reserved and uncreated
```

This execution-ready label remains limited to a future separately authorized metadata/footer-only
wave. It does not authorize HU access, source/footer retrieval, row or full-shard access, corpus
materialization, scoring, inference, evaluation, GPU/Slurm, training, cleanup or any later
numbered document.
