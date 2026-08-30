# vngrs M2 OSCAR Phase-2 evidence contract v1a

**Date:** 2026-08-29

**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE RETRY`

**Contract ID:** `vngrs-m2-oscar-phase2-evidence-v1a`

## Purpose and correction boundary

Job `481910` consumed V1 and stopped fail-closed before tokenizer accounting because the tracked
inventory recorded OLMo `tokenizer.json` SHA-256 with first character `b`, while both the exact HU
asset and its frozen authoritative snapshot manifest record `c`. File size and the remaining 63
hexadecimal characters matched. The other five tokenizer assets matched exactly.

This contract freezes one fresh-root CPU-only retry that changes only:

1. an append-only corrected tokenizer inventory;
2. mandatory runtime cross-check of that inventory against each frozen `snapshot_manifest.json`;
3. fresh output/job/version identities.

The V1 corpus, split, decisions, tokenizer/model identities, accounting semantics, output schema,
resource bounds and terminal meaning remain unchanged. This document authorizes no publication,
HU access or execution by itself.

## Preserved V1 evidence

- V1 contract SHA-256:
  `48dfa11058597e80df30e30e063d484772741a4632d1b1f042e703e200b76301`
- V1 implementation commit: `5219b717f229158605577f901393e24ef2690b53`
- V1 job: `481910`
- V1 root, immutable/read-only:
  `/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1`
- V1 typed failure SHA-256:
  `a7c566f61427d67921091ac49ffb1debfc9632c7d401bfa99145755fab783c3f`
- V1 original inventory SHA-256:
  `fd3901408e7dfa6f299b3c260229926ba5733bfd3a88f2af80e3ea522b143cb5`
- execution result: `documentation/188_VNGRS_OSCAR_PHASE2_V1_EXECUTION_FAILURE_RESULT_TR.md`
- result SHA-256:
  `009b2561c1ac0907da929d7b8e2ffc96f485b4aef13e3e402f86b2b3076ebe3f`

V1 root and original inventory must not be rewritten, reused, deleted or cleaned.

## Corrected inventory

Tracked V1A inventory:

```text
artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1a.json
```

Its SHA-256 is
`72e1c51538a0a801a0fc766faea8af771fb126e190faefd19a0705af3a8886f9`.

The only corrected asset row is:

```text
role = olmo
path = tokenizer.json
bytes = 7,137,656
old recorded SHA-256 = b460dae76d074f5686b2b9cd143bee5cd118be73a7b74196a03d61432b2908b5
correct SHA-256      = c460dae76d074f5686b2b9cd143bee5cd118be73a7b74196a03d61432b2908b5
```

The corrected OLMo two-file tokenizer asset-manifest SHA-256 is
`04223e922f3f062978b34968d6653a185f2b971505b7c707e7bc95df33a46191`.
Qwen and SmolLM rows and hashes remain unchanged.

## Frozen scientific inputs

- source root: `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`, read-only
- materialization SHA-256:
  `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10`
- 32 objects / `9,502,315,428` bytes
- lowercase OSCAR: 354,482 documents / `1,553,923,133` UTF-8 bytes
- OSCAR ID SHA-256:
  `c252d6b54d488e898f534564ef6c16196e22ae78f4fe0e61f83d4ad0bf83a056`
- split: 344,482 train / 10,000 held-out / zero overlap
- split SHA-256:
  `21f43359570ea66a73e969c1d0e8b4f08408f8ebbb71f50fc40dbd0d7e16f38f`
- review packet SHA-256:
  `73329e45fd8ff2c6b24c36fa6f9b5bac767b9d25726b691d527c71f9fdf90af8`
- decisions SHA-256:
  `f6e1e2989de4593ca56707db6c3582f5efc7cd0bbd652ca965ef92ceeded7225`
- required decisions: 64/64 unique `usable`
- tokenizer roles: exact M1 epoch-036 OLMo, Qwen and SmolLM
- `trwiki-20260601` training rows: zero

## Mandatory stage order

1. exact clean commit, absent fresh root, duplicate-job, predecessor hashes, V1 failure hash,
   original/corrected inventory hashes, `2 GiB` free and `1,024` inode preflight;
2. validate all 64 decisions and exact OSCAR population/split before tokenizer access;
3. for each role, verify frozen `snapshot_manifest.json` SHA-256 and exact tokenizer rows against
   corrected inventory;
4. verify the two exact tokenizer asset byte sizes and SHA-256 values;
5. offline tokenizer load, vocabulary gate and two deterministic Turkish probes;
6. exact `add_special_tokens=false`, no-padding, no-truncation train/held-out accounting for all
   three roles;
7. persist the same 12 compact pre-terminal files, self-reference-free manifest and terminal
   audit as V1.

No model weight, optimizer, checkpoint tensor, network fallback, corpus copy, token-ID cache,
packed block or per-document row may be opened or persisted outside those exact rules.

## Fresh output and terminal meaning

The only V1A output root is:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_retry_v1
```

Success remains exactly:

```text
status = D0_EVIDENCE_COMPLETE
human_review_status = HUMAN_REVIEW_PASS
tokenizer_roles_complete = [olmo, qwen, smollm]
m2_training_contract_frozen = false
ready_to_train = false
```

The compact success payload is capped at 128 MiB. A typed V1A failure is not a PASS.

## Frozen implementation

```text
config       a783260a8e00f476455ab7695dd9b0f1a2a2ba6ca7188faf7d001f804e57c26a
inventory    72e1c51538a0a801a0fc766faea8af771fb126e190faefd19a0705af3a8886f9
operator     5e770013c0128f281d23ddc257a35805a0fdc299418c50bc72c3c83a16ce5dbc
bundle       60fb5f3a56d6561a0c5f7ad93b17ccb0efa07d9456fe98c6b530b25ba9d97d18
runtime      6276cc68c5a98893b2e88cea078f380061208bc295f44b50a3c5e3ad0d589abc
runner       6dfa77be4f99dda0fa29a9e82898a9efd7e6df4a5bed6727d19137fbcf800b0c
submitter    a95e9010a35522ae835b41a80b62e1434bbf21726fa2e1ddf39e0fed88b0e3e3
Slurm        84debee09ec625c8ad4ca6ece7bc9146bbad0c29f19e5760ee9c3a5aae4f0f5c
```

Bindings:

```text
config:    configs/corpora/vngrs_m2_oscar_phase2_evidence_v1a.yaml
inventory: artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1a.json
runner:    scripts/corpora/run_vngrs_m2_oscar_phase2_v1a.py
submitter: scripts/corpora/submit_vngrs_m2_oscar_phase2_v1a.sh
Slurm:     slurm/m2/phase2_vngrs_m2_oscar_v1a.slurm
job name:  vngrs-m2-oscar-p2-v1a
```

## One-wave boundary

A later explicit authorization bound to this document's final SHA-256 and exact implementation
commit may permit ordinary non-force push, preservation-checked HU fast-forward and exactly one
V1A CPU pass. It does not permit a second retry.

GPU, model-weight access, inference, evaluation, corpus/split/decision mutation, block
materialization, M2-A/M2-B training, factual re-exposure, recipe/budget selection, cleanup,
deletion and automatic retry remain forbidden.
