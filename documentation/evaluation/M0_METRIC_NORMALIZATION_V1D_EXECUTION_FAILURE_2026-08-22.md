# M0 eval-v2 normalization v1d — execution failure

**Date:** 2026-08-22  
**Classification:** `NOT_RUN / OPERATOR_FAILURE`  
**Scientific result:** none

The explicitly authorized v1d normalization invocation passed the source audit and then stopped
before writing any canonical table. The writer attempted to read the audit row under the internal
key `path`, while the audited row schema exposes the canonical key `raw_artifact_path`. It raised
`KeyError: "path"` during row assembly.

## Bound execution

- Contract SHA-256: `bc258b243c053f938e9e4fa6a30fe3b6628531aa62204a4c4386e8d6bcbe37cf`
- Config SHA-256: `206f0c23e4f16b5c02c2b4e897b8ead9960b00e3c12fa6ef640e03d63c964b66`
- Commit: `89133cc` (`Prepare M0 normalization v1d contract`)
- Input projection: `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`
- Proposed output root: `/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1d`

The audit had already verified 24 source rows and 42 metric observations. The operator created the
v1d directory before row assembly failed; a follow-up inspection found no normalization manifest
or output files. The partial root is preserved as failure evidence and must not be reused or
deleted without separate authorization.

No model load, inference, rescoring, source mutation, projection mutation or scientific gate ran.
The v1d authorization is consumed; there is no automatic retry. A code correction and a new fresh
root require a new exact contract/config authorization.
