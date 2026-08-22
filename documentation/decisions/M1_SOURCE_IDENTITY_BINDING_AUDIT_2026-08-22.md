# M1 source identity binding audit

**Date:** 2026-08-22
**Status:** `LOCAL_REFERENCE_BOUND_EXTERNAL_PATHS_NOT_READ_THIS_TURN`
**Scope:** read-only reconciliation of already recorded M0 model manifest identities

## Frozen references

The current three-model M0 source matrix already records the following manifest paths and hashes.
This audit does not SSH, read, copy, hash or mutate those external files; it only reconciles the
existing tracked references into the fresh M1 draft configs.

| Model | Revision | External manifest path | Recorded SHA-256 |
|---|---|---|---|
| OLMo-2-0425-1B | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | `/vol/tmp2/yesildau/m1_provenance_screen_v3/models/allenai__OLMo-2-0425-1B/model_manifest.json` | `8702b80d5b7e4c996c8ce2ff5fe771ada08ab0080bde1926c0b1f53c607303dc` |
| Qwen2.5-1.5B | `8faed761d45a263340a0528343f099c05c9a4323` | `/vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json` | `c9d3562b717784251fe14c2b7972660fe4a20fe4687e15f69746bc1713d2d4fb` |
| SmolLM2-1.7B | `effd688a12921b4cc83e3312b6feb579f70f9c71` | `/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json` | `e5d04302087b8b41828f734c1d88c4620a74bb80d6919de62df37b9d57dadbfc` |

Source of these references: `configs/studies/three_model_m0_to_m2_matrix_v1.yaml` and the frozen
M0 scientific configs. The exact model revisions remain the fixed M1 cohort; no model selection
or substitution is introduced.

## Boundary

The three M1 training drafts and three M1 eval drafts now point at these recorded M0 manifest
identities. They remain non-executable because:

- the external paths have not been read or re-hashed in this turn;
- tokenizer inventory/compatibility is not independently closed for this new wave;
- the M1 training/checkpoint manifests are future outputs and remain placeholders in eval inputs;
- `ready_to_train` is still false and no SHA-bound execution authorization exists.

The next safe external action is one bounded HU read-only preflight that verifies exact path,
manifest bytes, tokenizer identity, storage/inode capacity and clean 3090 candidate availability.
That preflight must be attached to a separately frozen M1 execution contract; it does not authorize
training by itself.
