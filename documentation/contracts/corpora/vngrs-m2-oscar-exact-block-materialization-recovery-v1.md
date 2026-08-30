# vngrs M2 OSCAR exact block materialization recovery contract v1

**Date:** 2026-08-30  
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE CPU RECOVERY WAVE`  
**Contract ID:** `vngrs-m2-oscar-exact-block-materialization-recovery-v1`

## Purpose and predecessor

This contract freezes one fresh-root CPU-only recovery for the terminal partial result recorded in
Document 195. The consumed predecessor job is `481990`; its immutable root is
`/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_v1`. That root contains exactly one 250-row fact
registry with SHA-256
`784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec`, zero block files and no
terminal manifest. The predecessor remains read-only and is never reused or cleaned.

This recovery changes no corpus, tokenizer, factual dose, token budget, document ordering or
scientific training recipe. It addresses only the operational failure surface that lost the exact
exception and retained the full non-OSCAR population while token blocks were being constructed.

## Frozen scientific identity

- source root, read-only: `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`;
- source manifest SHA-256:
  `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10`;
- exact lowercase OSCAR population: 354,482 documents / 1,553,923,133 UTF-8 bytes;
- train split: 344,482 IDs, SHA-256
  `90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac`;
- held-out split: 10,000 IDs, SHA-256
  `dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91`;
- roles: exact epoch-036 OLMo, Qwen and SmolLM tokenizers, offline only;
- 97,536 × 512 train blocks and 49,938,432 tokens per sibling arm and model;
- 2,048 × 512 shared validation blocks per model;
- exact 250 Branch-B Turkish facts and zero Branch-A fact exposure;
- exact 976 evenly spaced factual replacement blocks;
- M2-A and M2-B generic stream, token count and optimizer-update budget remain matched;
- document-order namespace `vngrs-m2-oscar-exact-blocks-v1`, seed 42;
- model weights, optimizer tensors, GPU, training and evaluation remain forbidden.

## Operational correction

The recovery makes only these implementation changes:

1. use the fresh root
   `/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_v1`;
2. verify the predecessor's exact one-file terminal state before reading other inputs;
3. release the 5.3-million-document non-OSCAR population before tokenizer/block construction;
4. stream M2-A, M2-B and validation JSONL atomically instead of retaining/copying full 50-million-
   token sibling families in Python memory;
5. fixture-prove byte/row equivalence of the streaming writer to the frozen in-memory algorithm;
6. persist `progress.json` with stage, Slurm job ID and process max-RSS/CPU observations;
7. persist Slurm stdout/stderr, `/usr/bin/time -v`, shell exit audit and Python exception type,
   message, traceback and resource snapshot;
8. keep incomplete `*.tmp` artifacts as bounded terminal evidence rather than publishing them as
   completed block files;
9. run one role at a time and release role-specific ordered rows/tokenizer state before the next;
10. prohibit automatic retry even if the recovery fails before scientific block publication.

The recovery does not claim that memory pressure caused job `481990`; Document 195 correctly
keeps that trigger unresolved. These changes remove the identified memory risk and guarantee a
materially stronger failure record.

## Success and failure closure

Success requires all three role audits to report `EXACT_MATCHED_BLOCKS_PASS`, the family manifest
to report `EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED`, and `control/final_audit.json` to report
`PASS`. Six train files, three validation files, three role audits, the exact fact registry and the
family manifest must be hash/byte closed. Even on PASS:

```text
training_opened = false
model_weights_accessed = false
ready_to_train = false
```

Any exception, signal, missing terminal manifest, role omission, shell nonzero exit or drift is
`BLOCKED`. The new root is then preserved; it is never reused. A missing Python failure file does
not erase the persistent Slurm logs, last atomic progress stage or submission/exit evidence.

## Frozen implementation

```text
config       8877a8718fff3ee906bad9b5f51a778ec0f32a4ea9f9b39b5149df9d2d81543e
runner       5820113e09e45d5bfb2d2cabb4f9c110fc6c3b5cf123f18f541055b9d2f6f196
streaming    874b4af79966cb7ea142938e729a8f515a0ce5632fe4c8039ecb8a141e77cc36
fact/order   fe5455062eaa7de6eacbbb96dac7bf7af86420fd463c353d6e8028fd91fad005
Slurm        e67c30629730f0bfaddd62182df23caa9830eb4a6e866b9192fcd29e00bb2082
submitter    3c320dd1f4210b65e4cb86466be49a5780102473f297da898a3e8f571b64547f
tests        784fbe3b433fcbf77ffe983ea3b3724e8efa145551a9b40ed4e23ff96e828803
```

Bindings:

```text
config:    configs/corpora/vngrs_m2_oscar_exact_blocks_recovery_v1.yaml
runner:    scripts/m2/materialize_three_model_oscar_m2_blocks_recovery.py
streaming: src/transfer_vs_relearning/pipeline/m2_block_streaming.py
fact/order: src/transfer_vs_relearning/data/qwen_pre_m2.py
Slurm:     slurm/m2/materialize_three_model_oscar_m2_blocks_recovery.slurm
submitter: scripts/m2/submit_three_model_oscar_m2_blocks_recovery.sh
tests:     tests/test_m2_oscar_exact_blocks_recovery.py
job name:  vngrs-m2-oscar-blocks-recovery-v1
```

Compatible focused suite: `20 passed`.

## Authority boundary

This document authorizes nothing by itself. A later explicit authorization bound to this
contract's final SHA-256 and exact implementation commit may permit ordinary non-force push,
preservation-checked HU fast-forward and exactly one CPU recovery wave.

It does not authorize a second recovery attempt, automatic retry, predecessor mutation, GPU,
model-weight access, optimizer smoke, M2-A/M2-B training, evaluation, human verdict entry,
cleanup or deletion. A terminal recovery result must be inspected and documented before any next
scientific contract can be opened.
