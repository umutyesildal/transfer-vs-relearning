# M0 eval-v2 projection v1a execution attempt — blocked

Date: 2026-08-22

Authorized contract SHA-256: `5f428ef85622867dcbe6f55db4333586862880b33afb9a8fc4eb84094cb53144`

Authorized config SHA-256: `5f10ca3713829df59027a5bc622615aaee023af17bec2a992829ff816d1761d6`

## Result

`NOT_RUN / blocked_by_execution_flag`

The implementation commit `fd3b4dbfe5a21ab1906f98cd190fa4de6afb7411` was pushed to
`origin/main` and fast-forwarded into the clean HU checkout. The first launcher invocation
stopped before importing the package because the HU `src/` layout requires `PYTHONPATH=src`;
the fresh output root remained absent. The corrected invocation then reached the projector and
failed closed at its explicit authorization gate because the authorized v1a config contains
`execution_authorized: false`.

No source manifest, lane result or artifact was read by the projector after the corrected
invocation. No output root or projection file was created. No normalization, evaluation,
training, scoring, model loading or historical mutation occurred.

## Required correction

The v1a contract/config pair remains immutable and must not be edited in place. A new
execution-enabled config/contract pair with a fresh output root and a new exact SHA-bound
authorization is required before projection can run. This failure does not invalidate the
24/24 read-only source-binding discovery recorded in
`documentation/evaluation/M0_EVAL_V2_SOURCE_BINDING_DISCOVERY_2026-08-22.md`.
