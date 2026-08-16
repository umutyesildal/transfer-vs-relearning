# Three-model scientific M0 single-wave authorization

**Status:** authorized once | **Date:** 2026-08-16 | **Training:** not authorized

## User authorization

The user explicitly authorized the single wave bound to:

- frozen M0 contract SHA-256:
  `013f6f638176cbfd15fbe65c7d07a9dbb8d0029879e217f65e4e69bbeef765d9`;
- pre-authorization family-manifest SHA-256:
  `264525095a3f67b5899771069ad227a41ed431de14fd98c38168690787d2bf5d`;
- exact OLMo, Qwen and SmolLM identities and unchanged eval-v1 semantics in that contract;
- one three-model submission only.

The authorization instruction was:

> 013f6f... M0 kontratı ve 264525... family manifestine bağlı tek üç-model bilimsel M0
> wave'ini authorize ediyorum; execution flag'lerini aç, push/FF yap ve 24 lane'i bir kez
> submit et.

## HU-home and storage gate

The explicit HU home is `/vol/fob-vol6/mi25/yesildau`. An exact read-only `du -sb` measurement
before publication returned `14,545,990,549` bytes. The hard ceiling is 30 GiB or
`32,212,254,720` bytes, leaving `17,666,264,171` bytes of headroom.

Every model/result/cache/tmp/log path remains scratch-bound. The family root is
`/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1`; it was absent at authorization time.
Scratch reported `123,580,110,077,952` available bytes and `2,284,301,731` free inodes. HU-home
writes are forbidden. The operator must repeat the exact home measurement immediately before
submission and stop with zero new jobs if the limit is exceeded or cannot be measured.

## Exact scope

This overlay authorizes:

1. publishing deterministic authorization flags bound to the two hashes above;
2. HU fast-forward of the clean active monorepo checkout;
3. one final fail-closed preflight;
4. one submission creating three model DAGs, 24 GPU lanes and their control/finalizer jobs;
5. read-only status inspection and preservation of produced evidence.

It does not authorize a second M0 wave, automatic retry, outcome-aware rerun, M1/M2 training or
evaluation, corpus materialization, network retrieval, source-cache mutation, HU-home writes,
cleanup, deletion, foreign-job intervention or threshold/protocol changes. The fresh fixed family
root makes the authorization non-reusable after the first submission attempt.
