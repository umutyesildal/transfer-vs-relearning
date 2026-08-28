# vngrs three-model M2 D0 corpus closure contract v3

**Status:** `FROZEN / UNEXECUTED — PHASE 1 ONLY`  
**Owner:** thesis project  
**Created:** 2026-08-28  
**Base scientific contract:** `vngrs-m2-three-model-d0-v1`

## Purpose

Run the still-unexecuted scientific D0 Phase 1 from a fresh root after V2 correctly downloaded the
first immutable Parquet object but rejected it because the source-registry repair had incorrectly
promoted a 64-hex LFS/Xet object identifier to the full-file byte SHA-256. V3 repairs only this
identity semantic. It changes no selected shard, revision, object size, audit, split, review,
tokenizer, storage or HTTP bound.

## Preserved V2 result

Job `481838` created `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2` and stopped fail-closed on the
first object before publishing any verified source object. Its terminal core is:

```text
status:                       BLOCKED
error_type:                   MaterializationBlocked
source_path:                  data/train-00004-of-00284.parquet
verified_objects:             0
response_transferred_bytes:   448,718,347
```

The preserved partial is exactly 448,718,347 bytes with SHA-256
`d72ae76652c1a3880288ebbea9d0004e17c03730971f62666ed09c6c87de0943`. It has `PAR1` leading and
trailing magic; its final 468,156-byte footer and final eight-byte trailer reproduce the accepted
footer package exactly. Therefore it is valid evidence, not an HTML/error payload.

V3 treats the whole V2 root as read-only. It does not move, copy, hard-link, resume, delete or
otherwise reuse the partial. The submitter and in-job preflight re-hash it only to prove that the
terminal evidence remains unchanged.

## Corrected identity semantics

The accepted ledger itself says `object_sha256=null` and
`object_sha256_status=unverified_footer_only`. Its `object_id`/ETag value
`a81097a7346a46825147c84b516be22fe70bdd1fd589d5d57df9da66ec7f91da` for the first shard is thus
an immutable transport object identifier, not a reviewed claim about the downloaded bytes.

V3 keeps three identities separate:

1. immutable Git revision, path, exact Content-Length and LFS/Xet object ID bind the HTTP route;
2. accepted footer and trailer SHA-256 values bind each response to the previously reviewed
   Parquet structure;
3. full-file byte SHA-256 is computed from the newly downloaded bytes and recorded as an output.

The first freshly downloaded shard must additionally reproduce V2's independently observed
full-byte SHA-256 `d72ae7…`. This is a cross-wave calibration gate. The remaining 31 full-byte
hashes were never previously observed, so V3 does not invent predeclared hashes for them; it
records their computed values only after size, route identity, Parquet magic, footer and trailer
all pass.

After all 32 objects pass, V3 atomically writes `control/materialization_v3.json`. The subsequent
Parquet loader re-hashes every published file and requires equality with the computed byte SHA in
that manifest before any row enters the audit. It never falls back to the transport object ID.

Any mismatch preserves the current partial plus a typed failure containing the observed byte SHA
when available. No retry, resume, cleanup or alternate route is automatic.

## Fresh V3 root and inherited protocol

V3 uses exactly:

```text
/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
```

It must be absent. Preflight verifies the complete accepted 104-file evidence package, its frozen
top-level hashes, all 32 ledger rows and footer/trailer artifacts; the exact V2 partial; a clean,
reviewed Git checkout; zero duplicate `vngrs-m2-d0-v3` jobs; read-only HU home below 30 GiB; and
at least 40 GiB plus 1,024 inodes on scratch.

All V1 scientific rules remain unchanged: the exact systematic 32-of-284 selection at revision
`ee5c6201ee84457a18182bfc483a7d8a7f3655ba`, 9,502,315,428 bytes, the Max-aligned audit, frozen
Relation V2 contamination surfaces, deterministic 10,000-document held-out split, 64-document
human-review packet, zero trwiki training rows and `ready_to_train=false`. A successful wave stops
at `AWAITING_HUMAN_REVIEW`.

Phase 1 loads no tokenizer or model weights, performs no inference/scoring, uses no GPU and does no
training. Phase 2 remains outside this contract.

## Exact implementation route

```text
config:    configs/corpora/vngrs_m2_three_model_d0_v3.yaml
preflight: transfer_vs_relearning.corpora.vngrs.d0_preflight_v3
inputs:    transfer_vs_relearning.corpora.vngrs.d0_inputs_v3
loader:    transfer_vs_relearning.corpora.vngrs.parquet_loader_v3
runner:    scripts/corpora/run_vngrs_m2_d0_v3.py
submitter: scripts/corpora/submit_vngrs_m2_d0_v3_phase1.sh
Slurm:     slurm/m2/materialize_vngrs_m2_d0_v3_phase1.slurm
job name:  vngrs-m2-d0-v3
```

The submitter performs one `sbatch --test-only` followed by exactly one real CPU submission.

## Authority boundary

This local preparation does not authorize push, HU fast-forward, SSH, Slurm, public HTTP retrieval,
corpus materialization, Phase 2, tokenizer/model access, inference, evaluation, training, cleanup,
deletion or automatic retry.

One separately supplied exact SHA-bound authorization may permit only ordinary non-force push of
the reviewed commit, preservation-checked HU fast-forward, HU tests/fresh preflight, and exactly
one V3 Phase-1 test-only plus real CPU wave. Phase 2, training, cleanup and automatic retry remain
forbidden.
