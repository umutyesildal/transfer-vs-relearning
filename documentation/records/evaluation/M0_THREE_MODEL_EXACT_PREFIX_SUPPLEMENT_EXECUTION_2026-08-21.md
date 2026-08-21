# M0 Three-Model Historical Exact-Prefix Supplement Execution — 2026-08-21

Status: `TERMINAL / NOT_RUN_GPU_MEMORY_GUARD_ALL_THREE / NO SCIENTIFIC SCORES`

The single wave authorized against contract SHA-256
`83f43a3ebbc981f4e8f99609587a6a3c0d3fc1eabda95d3e640671aa109a633b` and
pre-authorization config SHA-256
`4d42a3700fb1f5302d38cba7fcb06f40a3eb0c288642d5e254f81b7c41f1178a` was submitted exactly
once. The authorized config SHA-256 was
`5adc22f0512bd3e6331622d40b705893341990cea90ed58e4d23550a9ad1ae62`.

## Synchronization and final preflight

The canonical HU checkout was at cleanly ancestral commit `9314a02`, but its preserved artifact
symlink overlay caused `git merge --ff-only` to abort before changing any file. Nothing was moved,
deleted or overwritten. A fresh clean detached HU scratch worktree was created at authorized commit
`409cc4bf0f6e123e51cdbe328c873f471733fc16` under
`/vol/tmp2/yesildau/eval_v1_code_m0_exact_prefix_supplement_v1`.

The final preflight passed all 14 checks with no blockers. It verified 500 unique facts, 100
subjects, 100 facts in each of five relations, exact fact/answer identity with the robust registry,
zero prompt overlap with robust A--D, all three model manifests, implementation/runtime hashes,
clean Git identity, fresh output root and zero duplicate jobs. HU-home usage was 14,702,747,648
bytes against the 32,212,254,720-byte limit. Captured preflight SHA-256:
`52a7df0d1700ac16c317f82869dc8e32ec01668e633ed967218df3a61560ed32`.

## Submission and terminal outcome

- array: `473834`, specification `0-2%3`;
- effective task job IDs: task 0 `473836`, task 1 `473837`, task 2 `473834`;
- finalizer: `473835`, dependency `afterany:473834`;
- route test-only observation: eligible RTX A6000 route on `gruenau8`;
- submission manifest SHA-256:
  `c9337f506ddea6eada5b735a7ab3b03186352a8d9293cf306c5625209266f9f2`.

All three tasks reached the execution-time GPU guard with the same visible RTX A6000 totals:
50,897,289,216 total bytes and 3,142,844,416 free bytes. The frozen minimum was 21,474,836,480
free bytes. Each task stopped before model load and candidate scoring. Therefore OLMo, Qwen and
SmolLM are all `NOT_RUN` operational outcomes; no exact-prefix accuracy exists.

Lane-result SHA-256 values:

- OLMo: `4713dbfb22fa9f40de92bf60a1e22c416c46d09e20b5bc691cc9424f1d5951e3`;
- Qwen: `8687d2b42e550c134d6f2c5c7c2be07555e17180f9bfdff4f4a1b874c02f9984`;
- SmolLM: `23048f5f5e5baa0a26d03dcc7065d53f521b1bf6c587855567113721d5bf8031`.

The `afterany` finalizer correctly produced `partial_invalid` without scientific interpretation.
Family-result SHA-256 is
`fee84e1ec4604c4a1a1dbc96a7f2a52a50d48a00ca9f6dbc2f1347b9bf3aaaa9`; family-inventory
SHA-256 is `cbf35264fc5eef8394e2821bd63eeb047e64ac35b6712bff577595d4262d78c0`.

The single-wave authorization is consumed. No retry, second wave, threshold/route change,
normalization, M1/M2 work, cleanup or deletion follows from this record. The independent active
Qwen Pile-10k recovery DAG was not altered.
