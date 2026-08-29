# vngrs M2 OSCAR Phase-2 evidence contract v1

**Date:** 2026-08-29

**Lifecycle:** `FROZEN / UNEXECUTED`

**Contract ID:** `vngrs-m2-oscar-phase2-evidence-v1`

## Purpose

The exact OSCAR population, frozen split, quartile coverage and packet-bound human review are now
complete. The authoritative decision ledger contains 64/64 `usable` verdicts. This contract
freezes one possible offline CPU-only Phase-2 wave that revalidates those facts and computes exact
train/held-out token counts for the three mandatory M1 epoch-036 tokenizers.

This is corpus evidence completion, not M2 training readiness. The terminal success state remains
`ready_to_train=false` because the matched M2-A/M2-B training contract is not frozen.

This document authorizes no publication, push, HU access or execution by itself.

## Frozen inputs

### Corpus and split

- V3 source root: `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`, read-only
- materialization SHA-256:
  `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10`
- exact source objects / bytes: `32 / 9,502,315,428`
- exact lowercase OSCAR documents / UTF-8 bytes: `354,482 / 1,553,923,133`
- selected-ID SHA-256:
  `c252d6b54d488e898f534564ef6c16196e22ae78f4fe0e61f83d4ad0bf83a056`
- frozen split: `344,482` train / `10,000` held-out / zero overlap
- split SHA-256:
  `21f43359570ea66a73e969c1d0e8b4f08408f8ebbb71f50fc40dbd0d7e16f38f`

### Coverage and human decisions

- coverage root: `/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1`, read-only
- coverage final SHA-256:
  `6ce5f1f7b13fa61ae3f9c021b237b0464e4989ae179dc73fe32030049772c177`
- review packet file SHA-256:
  `621d8416f120803cc37f75453f0068a5fecaa60562698f11936b22caa3b75c61`
- review packet semantic SHA-256:
  `73329e45fd8ff2c6b24c36fa6f9b5bac767b9d25726b691d527c71f9fdf90af8`
- tracked decision ledger:
  `artifacts/corpora/vngrs_m2_d0/human_review_decisions_73329e45fd8f.jsonl`
- decision-ledger byte SHA-256:
  `f6e1e2989de4593ca56707db6c3582f5efc7cd0bbd652ca965ef92ceeded7225`
- required result: 64 unique rows, 64 `usable`, no `unusable`/`unsafe`, one non-empty reviewer

### Tokenizer-only assets

The manifest inventory SHA-256 is
`fd3901408e7dfa6f299b3c260229926ba5733bfd3a88f2af80e3ea522b143cb5`.
Only the exact `tokenizer.json` and `tokenizer_config.json` payloads identified there are eligible;
offline tokenizer-class metadata resolution may inspect the same frozen snapshot paths, but must
not open model-weight bytes:

| Role | M1 parent | Tokenizer asset-manifest SHA-256 |
|---|---|---|
| OLMo | epoch-036 | `1bb3f5ee04b6f32aab990e46fb99520b1e4ab04bdc3f1cfa75ea732c8f8dfd17` |
| Qwen | epoch-036 | `8e1cbce23938ba773e652fc767002a668f3ec4f538139d8b760b3fe0b33a2df` |
| SmolLM | epoch-036 | `1f41566541c514dcebac6168f0f2f83f2b54a969c6b36db4501ae4d0683fd652` |

No model weight, optimizer, checkpoint tensor or network fallback is eligible.

## Exact stage order

1. clean exact commit, fresh-root, predecessor-hash, duplicate-job, `2 GiB` free and
   `1,024`-inode preflight;
2. validate all 64 packet-bound decisions before tokenizer access;
3. reread the preserved source objects and verify OSCAR document count, UTF-8 byte count, ID SHA,
   split union, split disjointness and split SHA without rewriting any predecessor;
4. verify all six tokenizer asset sizes/hashes and load the three tokenizers offline;
5. require non-empty deterministic encodings for two frozen Turkish probes and vocabulary size
   greater than two;
6. encode each exact OSCAR document with `add_special_tokens=false`, no padding and no truncation;
7. persist train and held-out accounting separately for OLMo, Qwen and SmolLM;
8. write one compact self-reference-free artifact manifest and terminal audit.

For every model/split row, accounting includes document/byte/token totals, token-count quantiles,
zero/exception counts, token ratios, exact tokenizer identity and a streaming SHA-256 over sorted
`stable_document_id<TAB>decimal_token_count<LF>` pairs. Corpus text, token IDs, packed blocks and
per-document rows are not persisted.

## Fresh output and terminal meaning

The only success root is:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1
```

The pre-terminal compact payload contains exactly 12 files: state, population/split validation,
human-review validation, three tokenizer compatibility reports and six tokenizer-by-split
accounting reports. It is capped at 128 MiB. The manifest and one-way final audit follow.

Success is exactly:

```text
status = D0_EVIDENCE_COMPLETE
human_review_status = HUMAN_REVIEW_PASS
tokenizer_roles_complete = [olmo, qwen, smollm]
m2_training_contract_frozen = false
ready_to_train = false
```

A typed `control/d0_failure.json` may be written after a failure. Partial output is never a PASS.

## Frozen implementation

```text
config     1b2e8b3bf9a2db7d47db7998b867000c68e2d6eb61d388a300d6c2241ec9d82d
operator   5e770013c0128f281d23ddc257a35805a0fdc299418c50bc72c3c83a16ce5dbc
bundle     60fb5f3a56d6561a0c5f7ad93b17ccb0efa07d9456fe98c6b530b25ba9d97d18
runner     7a9a9c4eb0262b3d162de2b104dce766eddd154c30bc719828776adfc68ff661
submitter  b7684b36df203274d71270cf2558879d1898d5ab6d91960b4157ca8c599c6a8a
Slurm      f344efcc0393c8c738a93832a62dea4c4995cbeb11235c11f9bbf33a63cefcd0
```

Bindings:

```text
config:    configs/corpora/vngrs_m2_oscar_phase2_evidence_v1.yaml
operator:  transfer_vs_relearning.corpora.vngrs.d0_phase2
runner:    scripts/corpora/run_vngrs_m2_oscar_phase2_v1.py
submitter: scripts/corpora/submit_vngrs_m2_oscar_phase2_v1.sh
Slurm:     slurm/m2/phase2_vngrs_m2_oscar_v1.slurm
job name:  vngrs-m2-oscar-p2-v1
```

## One-wave boundary

A later explicit authorization bound to this document's final SHA-256 and exact implementation
commit may permit ordinary non-force push, preservation-checked HU fast-forward and one CPU pass.
It does not permit automatic retry.

Model-weight access, GPU, inference, evaluation, block materialization, corpus copying, split or
decision mutation, M2-A/M2-B training, Turkish factual re-exposure, budget/recipe selection,
cleanup and deletion remain forbidden. `trwiki-20260601` remains control-only with zero training
rows.
