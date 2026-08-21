# M0 Three-Model Historical Exact-Prefix A100 Recovery Execution — 2026-08-21

Status: `TERMINAL / PARTIAL_VALID_2_OF_3 / SMOLLM_NOT_RUN_GPU_GUARD`

The single recovery wave authorized against contract SHA-256
`2469d25a78b552c82b6005b75f03b68199a1c7d2c2d8e0e557a2b8f585a80ac4` and
pre-authorization config SHA-256
`f6ebaa43d3517d55ad9311ab40f236530f69b0f07c9f43cc5bf2560f85c7cbb7` was submitted exactly
once. The authorized config SHA-256 was
`bd036ce229dc67829e7834bff1328de2f66bb1ade1e5c8405f72f36a12bc007c`.

Final preflight passed all 14 checks with no blockers. HU-home usage was 14,703,091,712 bytes
against the 32,212,254,720-byte limit. Captured preflight SHA-256:
`909a4bb0d8cbf80c053a3c08edcf251e0875ed050ea0273cc0ca42b0d4f81941`.

## Submission

- array: `473839`, specification `0-2%3`;
- effective task job IDs: task 0 `473841`, task 1 `473842`, task 2 `473839`;
- finalizer: `473840`, dependency `afterany:473839`;
- node/route: `gruenau9`, one A100-80GB per task;
- submission-manifest SHA-256:
  `fb8d8c958e68f33510c4a03577dc8e5c0c4bf108167c2cea7cfdd3676ef17eea`.

## Scientific and operational outcome

OLMo passed the execution guard with 55,052,402,688 free bytes, completed all 500 probes and
produced mean-logprob top-1 accuracy `0.022` (2.2%). Its lane-result SHA-256 is
`ec359ab7229aa898e39bc48af867794054ef9228a3e327870f31e6a907380712`.

Qwen passed with 67,692,134,400 free bytes, completed all 500 probes and produced mean-logprob
top-1 accuracy `0.030` (3.0%). Its lane-result SHA-256 is
`934c51f34fb35742b3424564ee3987cd0d7b883c202d864a72ff62762f590d6c`.

SmolLM exposed 19,032,768,512 free bytes against the unchanged 21,474,836,480-byte minimum. It
stopped before model load/scoring and remains operational `NOT_RUN`. Its lane-result SHA-256 is
`c08921800d72258a6f6de65e78ef2c2103de825957a3275e0baad484f895a8c3`.

The finalizer correctly reported `partial_invalid`: two complete scientific lanes and one missing
lane. Family-result SHA-256 is
`7e48400f742cbc6c8bf06f832de695bd9c272fbf6240b2c445190747186e4f1c`; family-inventory SHA-256
is `5d14362f8d64546064eeb46b93fcc658f6dea076dcf48a35a40fcadee4a0ddc5`.

No full three-model interpretation or normalization is authorized from this partial family. The
single recovery authorization is consumed. A SmolLM-only continuation would require a new fresh
root, frozen contract and exact user authorization. No completed OLMo/Qwen rescore, automatic
retry, cleanup, deletion, M1/M2 work, threshold change, or Qwen Pile DAG alteration is authorized.
