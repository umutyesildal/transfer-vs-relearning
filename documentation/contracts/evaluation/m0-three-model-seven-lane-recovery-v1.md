# Three-model scientific M0 seven-lane recovery v1

**Date:** 2026-08-20

**Status:** `FROZEN — UNEXECUTED — EXACT AUTHORIZATION REQUIRED`

**Scientific protocol:** unchanged `eval-v1`

**Training:** not authorized

## 1. Purpose

The single authorized three-model scientific M0 wave is terminal with 17 complete raw lanes and
seven `failed_pre_scoring` lanes. This contract permits one prospective recovery wave that evaluates
only those seven missing lanes, preserves the 17 complete source lanes byte-for-byte, and assembles
one hash-bound 24-lane composite raw bundle.

This is an operational recovery, not a new scientific condition. It does not change a task,
dataset, prompt, few-shot setting, metric, denominator, model/tokenizer revision, precision, seed,
factual registry, generation panel, gate or missingness rule. Any such change would require
`eval-v2`, not this recovery.

Preparation of this contract does not authorize HU fast-forward, Slurm, GPU, inference, scoring,
normalization, M1/M2, cleanup or deletion. A new user authorization must quote the exact final
SHA-256 of this document or the exact config SHA-256 below.

## 2. Frozen identities

- source family root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1`;
- source terminal raw-bundle SHA-256:
  `75fcd7cf1e388eb5a4e883264c6aa14db83797b2e7832a4bbc8e40bb38865db1`;
- recovery config:
  `configs/evaluation/m0_scientific_recovery_v1.yaml`;
- recovery config SHA-256:
  `4a603719dd43a65dd9b36a36786407993afe84cf8d1d48f6245656d235c6bfeb`;
- implementation commit:
  `07cbaa6d55f0713a08bae8a1c3c9cbe2df5e8942`;
- fresh recovery family root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_v1`;
- original M0 contract SHA-256:
  `013f6f638176cbfd15fbe65c7d07a9dbb8d0029879e217f65e4e69bbeef765d9`;
- original family manifest SHA-256:
  `7ae29ce2e8086cf7d00df22050158537869b98460572af1308db7d864c113867`;
- eval-v1 remains the unchanged scientific authority.

Implementation file identities:

| File | SHA-256 |
|---|---|
| `scripts/study/recover_three_model_m0.py` | `5aab6e2fb63c66793fcdcff7fab814dee213e3d670481aa7c835e7c7809b89de` |
| `src/transfer_vs_relearning/study/m0_family_recovery.py` | `9750aebfb7f1e68ef43122b1ae6bb3ad383bb801370344169f56bdeb6d03be9a` |
| `tests/study/test_m0_family_recovery.py` | `08738cc4a3842e0fb0766663444f744e6913f07cb41af05c64043338ad3b02b1` |

## 3. Exact source split

The recovery split is closed:

```text
24 required source lanes
├── 17 retained complete lanes (read-only, never rescored)
└── 7 recovery targets
```

### OLMo

Retained complete lane-result SHA-256 values:

| Lane | SHA-256 |
|---|---|
| WikiText | `f1bdec898bd7a06b259fbd6f778b7b601d4f22cdac92bbc09629f460379533a4` |
| Pile-10k | `7c3c6d8f6d3e077213db063dd7cd53fa8856ed8bbbc9e373002d24859da75f55` |
| BLiMP | `86df97c78e3c1a8d94785392676b7e1e79c2cacef35744f4a2c07dbc1f9a9a7d` |
| factual access | `a8a1154d02460c15a022c2a4dffa9801abe39463af161f3b20c57a58a5e7020a` |
| generation integrity | `2f3b4b025f8b24c39426ae874de7c7e6d813330ea81b64a6db1ff94ebe5784c4` |

Recovery targets:

| Lane | Failed source SHA-256 | Route | Runtime free-VRAM gate |
|---|---|---|---:|
| English capability | `a480cce3893396fa4108be021d774985b7946bd3785e4dcf5cc75f29eed714e1` | V100-32GB | 28 GiB |
| TurBLiMP | `e43666af28e186d9255437109e842a11042c83727785a25a180cdf31d2f3e43a` | V100-32GB | 28 GiB |
| trwiki BPB | `2292a078eabbbac2bee76282e1ea830f17cab1bcac139aa2b4721949ca3f6e64` | V100-32GB | 28 GiB |

### Qwen

Retained complete lane-result SHA-256 values:

| Lane | SHA-256 |
|---|---|
| WikiText | `05d4d113553047bbd43846b3b00aa4cb146c96a5c8df3c7ac1fb587542d881a0` |
| BLiMP | `644785cd842b620ef638effb3e155e62856702f99f85b1c5041edc5eccdf8f4f` |
| English capability | `86fd696f12c476fe87d80bb8988c222087427458b8bef073bde56e468b85130f` |
| factual access | `63b89002054c22f7b1ef74a182eb14bfc6524c7e2a3e0d64dde49a667d98cbb9` |
| generation integrity | `0a2bdf5efbec40f3d8cdcfe06ca512bfc603e20011df6fd2cd59a7c774a7300d` |

Recovery targets:

| Lane | Failed source SHA-256 | Route | Runtime free-VRAM gate |
|---|---|---|---:|
| Pile-10k | `d17bff419e6224cf06c97747092e54322c32300baa15f7d6f036cc31cc925ba0` | A100-80GB | 64 GiB |
| TurBLiMP | `e8ae3a6019965797fbc435a63a4e8c701c85974c1bdaacecf1baf639c4c0e404` | V100-32GB | 28 GiB |
| trwiki BPB | `6bcfdfaa589d09284e94d2d3e4ecc985acabfeaa904c4322311dd7fd5499dcad` | V100-32GB | 28 GiB |

Qwen Pile retains the original full Pile-10k request and `auto:4` Harness semantics. It is moved
to A100-80GB rather than changing batching, context segmentation, task data or scoring. This is a
pure resource relocation. The 64 GiB runtime guard runs inside the allocation before model load.

### SmolLM

Retained complete lane-result SHA-256 values:

| Lane | SHA-256 |
|---|---|
| WikiText | `94ec5cdd1a89fbfe626f93cb80cbd16555b29be0fd3ae07635c33010083cb811` |
| Pile-10k | `5b660081b3da1a22802e6d9f09ccb8824ec84c36d222bc6a1c3801182b6593e4` |
| BLiMP | `6d167633362465727a3f9dde10f94f8e34157e81f5485ba2f640ab65174333e2` |
| TurBLiMP | `a29cf167407d632653ec7fe0f20328121c6941e42238fdb05db61fbd5debac9b` |
| trwiki BPB | `3fd100aa59e473b2af0021f8fa7cedb368929ae54b6f3b539f43c4593fea4647` |
| factual access | `ad42c27c4e3502d6faa28ba58318de235e2af1743324eb49b5f7d16188997fb2` |
| generation integrity | `277389fe36db71abe55d4f523c718322836476a0d4e5ee7db86416025751bf70` |

Recovery target:

| Lane | Failed source SHA-256 | Route | Runtime free-VRAM gate |
|---|---|---|---:|
| English capability | `1122cf81114a3e3c226e5284da97c9f7bdd7a611be588da78f279d9b23812695` | V100-32GB | 28 GiB |

## 4. Preflight

Before any new namespace or Slurm job, the operator must fail closed on all of the following:

1. contract/config frozen and the exact recovery authorization flag enabled;
2. current project state equals terminal M0 `17/24` and remains `ready_to_train=false`;
3. all 24 source `lane_result.json` files match the exact SHA-256 ledger;
4. every retained lane is `complete`, return code zero, identity-matched and artifact-hash valid;
5. every target source lane is the exact preserved `failed_pre_scoring` record;
6. three source plan, preflight, bundle, scientific-result and final-inventory hashes match;
7. source family raw-bundle hash matches;
8. implementation commit is an ancestor of HU HEAD and all implementation file hashes match;
9. HU worktree is clean;
10. recovery family root is absent;
11. exact HU-home `du -sb` is at or below 30 GiB and HU-home writes remain forbidden;
12. no existing `m0r-v1-*` Slurm job is present.

A failed check creates zero jobs.

## 5. Exact DAG

After preflight passes, the operator creates one fresh scratch-only family namespace and submits:

```text
7 independent target lane jobs
├── OLMo: 3 × V100-32GB
├── Qwen: 2 × V100-32GB + 1 × A100-80GB
└── SmolLM: 1 × V100-32GB

each model's target jobs --afterany--> one model composite finalizer
three model finalizers --afterany--> one family composite finalizer
```

Total new Slurm jobs are exactly 11: seven GPU lanes, three CPU model finalizers and one CPU family
finalizer. The operator returns immediately after submission and never waits for evaluation.

## 6. Composite rules

For every model, the composite finalizer selects:

- the exact original source result for each retained lane;
- the fresh recovery result only for a named target lane.

Every selected lane must be complete, identity-matched and artifact-hash valid. A successful model
composite contains eight lanes and writes `evaluation_manifest.json`, `evaluation_results.json`,
`scientific_bundle_result.json`, `raw_artifact_manifest.jsonl`, `bundle_status.json` and a final
inventory. A successful family composite contains all three complete model manifests and exactly
17 source + seven recovery lanes.

The family finalizer may set `normalization_allowed=true` only after all 24 selected lane results
pass. It never computes a model PASS/FAIL or cross-model ranking. Missing or invalid evidence stays
`partial_invalid`; it is never zero-filled or omitted.

## 7. Recovery outcome classes

| Outcome | Meaning | Automatic next action |
|---|---|---|
| `complete_raw_pending_normalization` | 24/24 composite raw lanes valid | none; normalization remains separately controlled |
| `partial_invalid_no_cross_model_summary` | at least one target missing/invalid | none; no retry |
| `no_jobs_submitted_route_gate_failed` | exact V100/A100 route unavailable | none; authorization consumed only if submission attempted as defined by the later overlay |
| runtime free-memory guard blocked | contaminated/low-memory allocation | preserve ledger; no model load and no retry |

## 8. Prohibitions

This contract forbids:

- rescoring any of the 17 complete source lanes;
- writing to the original family root or any prior evidence root;
- changing eval-v1 or adding/removing tasks;
- batch/context/prompt/metric/precision/seed/model/tokenizer changes;
- route fallback beyond the exact V100/A100 bindings above;
- automatic retry or a second recovery wave;
- normalization of an incomplete composite;
- M1/M2 training or evaluation;
- corpus work, network retrieval, cleanup, deletion or HU-home writes;
- foreign-process intervention.

## 9. Authorization boundary

The config remains `execution_authorized: false`. Publication of this frozen contract and operator,
or HU read-only inspection, does not open the wave. Execution requires a new exact instruction
binding the final contract SHA-256 or config SHA-256 and authorizing all of:

1. publish/fast-forward of the frozen implementation;
2. one final fail-closed HU preflight;
3. creation of the one fresh recovery root;
4. exactly one 11-job recovery DAG;
5. read-only monitoring and preservation of its outputs.

That authorization will not cover normalization, scientific interpretation or M1/M2. Those stages
open only after the recovered composite is verified and their own local/contract gates are ready.
