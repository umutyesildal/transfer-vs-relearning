# M0 Exclusive-A100 Recovery Submission — 2026-08-20

Status: `SUBMITTED / RESOURCES_PENDING`

- controller: `471047` (`m0r-v1-isolated-wave`);
- model finalizers: OLMo `471048`, Qwen `471049`, SmolLM `471050`;
- family finalizer: `471051`;
- topology: one exclusive `gruenau10` `gpu:a10080gb:3` sequential controller plus four finalizers;
- scheduler test-only estimate: `2026-08-22T10:46:25`;
- submission manifest SHA-256:
  `32de77b5c7ae3c9d31cc9032f949e562fc38b64fe6f9410e4182ed86d4546e53`;
- route probe SHA-256:
  `50ebe71202acbd4679a7fa0803f73bf5dfd8db69a0f507ba83638bbb4f73b666`;
- fresh root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_isolation_v1`.

The controller was `PENDING(Resources)` at the first post-submit snapshot. No automatic retry or
duplicate submission is authorized. The 17 complete source lanes and both prior recovery roots
remain preserved.
