# Three-model study matrix v1 — mandatory exact-prefix amendment

**Status:** `prepared planning amendment`  
**Date:** 2026-08-21  
**Execution:** not authorized

This append-only amendment preserves the original 15-stage/27-node planning record and updates the
current control graph to make historical exact-prefix evaluation mandatory at M0, M1, M2-A and
M2-B. It remains a candidate-ranking supplement, not free generation.

The single-model controller now has 19 stages. The three-model cohort has 39 nodes in 13 waves:
24 evaluation, 9 training and 6 local preflight/analysis nodes. Downstream gates fail closed:

- M0 normalization requires M0 standard evaluation, robust probing and exact-prefix;
- M1 checkpoint selection requires M1 standard evaluation, robust probing and exact-prefix;
- branch analysis requires standard/probing and exact-prefix evidence from both M2 siblings.

Every exact-prefix manifest must bind the state, frozen probe-registry SHA-256, ordered checkpoint
set, exactly 500 complete probes per checkpoint, and hash-valid result artifacts. Missing or drifted
evidence is never converted to zero and cannot be skipped by the workflow.

Implementation commit: `f95d7418e901755cca4380d276f0395856fa975c`. Current workflow-template
SHA-256: `296e674f087d32b28dd3a0eef7a2aaf38a12eda4c523adb5e68e6a006912af0c`.
Current matrix-config SHA-256:
`9b22c719d6d04127e91db15017d6dd97274fdeac7f689ab5bd0e4b55e32bc214`.

This amendment changes planning and validation only. It authorizes no M0/M1/M2 evaluation,
training, HU action, Slurm submission, cleanup or deletion. Every future scientific wave still
requires its own frozen recipe/contract and explicit authorization.
