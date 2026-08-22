# M0 eval-v2 normalization v1e — execution failure

**Date:** 2026-08-22  
**Classification:** `NOT_RUN / CORRECTION_REGRESSION`  
**Scientific result:** none

The explicitly authorized v1e retry stopped before creating its output root. The first correction
had changed the source-audit row assembly instead of the post-audit writer: `audit_normalization`
then attempted `match["raw_artifact_path"]` on the adapter's internal match object, which only
contains `path`. The command raised `KeyError: "raw_artifact_path"` before `mkdir`.

## Bound execution

- Contract SHA-256: `c1be111e18a294db60baec57a0694089524f72458b76cdc8906a405546b71e0f`
- Config SHA-256: `b2eee5b475976cfe37061a001232846920ea2617e07d72515bb7a9b62f840c6c`
- Commit: `ec873dd` (`Prepare M0 normalization retry after v1d failure`)
- Input projection: `/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`
- Proposed output root: `/vol/tmp2/yesildau/eval_v2_m0_metric_normalization_v1e`

Inspection confirmed the v1e root is absent and no manifest or table was written. The v1d partial
root remains preserved separately. No model load, inference, rescoring, source mutation,
projection mutation or scientific gate ran. The v1e authorization is consumed; there is no
automatic retry. The correction now explicitly separates the adapter's `path` fields from the
audit row's `raw_artifact_path`/`raw_artifact_sha256` fields and requires a new fresh root.
