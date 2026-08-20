# Corrected Exclusive-A100 M0 Recovery Authorization

Date: 2026-08-20  
Status: `AUTHORIZED_SINGLE_WAVE`

- Corrected contract SHA-256: `d2a6d9e35c60a00328380fe7ecfb68bfa3fdd0528ea469ecec0acfecdc849058`
- Corrected pre-authorization config SHA-256: `0fcd32da2c29eb9f2c8d0d838d160746890ddbec0d51d833bce9c1cc9943aa35`
- Corrected implementation commit: `1bf87f84cff5b67c1a45d5a2b4244a59fa226337`

The user explicitly authorized HU fast-forward, one final preflight and exactly one five-job
exclusive-A100 recovery DAG. The authorization preserves the 17 source lanes and both prior roots,
and does not authorize retry, threshold changes, normalization, M1/M2, cleanup or deletion.
