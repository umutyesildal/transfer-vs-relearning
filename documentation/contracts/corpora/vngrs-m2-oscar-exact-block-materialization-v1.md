# vngrs M2 OSCAR exact block materialization contract v1

**Date:** 2026-08-30  
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE CPU WAVE`  
**Contract ID:** `vngrs-m2-oscar-exact-block-materialization-v1`

## Purpose

This contract freezes one CPU-only wave that converts the already accepted lowercase OSCAR train
split into model-native, pretokenized, exactly matched M2-A/M2-B blocks for OLMo, Qwen and SmolLM.
It is the block-materialization stage in Document 191; it is not training authorization.

## Frozen inputs

- source root, read-only: `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`
- source manifest SHA-256:
  `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10`
- source: 32 objects / 9,502,315,428 bytes; exact lowercase OSCAR only
- split root, read-only: `/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1`
- train IDs: 344,482 rows; SHA-256
  `90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac`
- held-out IDs: 10,000 rows; SHA-256
  `dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91`
- split overlap: zero
- exact M1 100-subject selection SHA-256:
  `a975263abb03d887fa224fb94d402f1fad852afe1ec03cd69226c0874cc32d3b`
- canonical 5,000-profile registry SHA-256:
  `60dd741f8ef2815755beafa8bb5799f4112af3d94b1b8c4c171bfef28b07e6c1`
- corrected tokenizer inventory SHA-256:
  `72e1c51538a0a801a0fc766faea8af771fb126e190faefd19a0705af3a8886f9`
- tokenizer roles: exact epoch-036 OLMo, Qwen and SmolLM assets; offline only
- model weights and optimizer/checkpoint tensors: forbidden

## Exact packing rules

For each tokenizer independently:

1. order the train and held-out documents by the frozen SHA-256 namespace, seed 42 and stable
   document ID; input shard/row order must not affect the result;
2. append the native EOS after each document and use no special-token insertion, padding,
   truncation or corpus cycling;
3. materialize 97,536 train blocks of 512 tokens: exactly 49,938,432 tokens per arm;
4. materialize 2,048 shared held-out validation blocks of 512 tokens;
5. derive exactly 250 canonical Turkish facts from the 50 Branch-B subjects of the exact M1
   100-subject population;
6. create M2-A from the factsiz OSCAR stream;
7. create M2-B by replacing the prefixes of exactly 976 evenly spaced blocks with complete
   Branch-B fact encodings and retaining the corresponding M2-A generic tails;
8. require zero Branch-A exposure, zero extra tokens, equal M2-A/M2-B block and token counts, and
   per-fact and per-relation exposure imbalance no greater than one;
9. persist exact consumed-document IDs hash, discarded-tail count, fact exposures, relation
   exposures, factual-token share and SHA-256/byte size for every output.

The three tokenizers need not produce the same token IDs or consume the same count of OSCAR
documents. The mandatory equality is within each model's M2-A/M2-B sibling pair.

## Output and terminal state

The only output root is fresh and absent before execution:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_v1
```

Success requires all three role audits to report `EXACT_MATCHED_BLOCKS_PASS` and the family
manifest to report `EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED`. The output includes six train
block files, three shared validation files, three audits, one 250-row fact registry and one family
manifest. Raw OSCAR text is not copied. Token IDs are intentionally persisted under scratch.

Even on success:

```text
training_opened = false
model_weights_accessed = false
ready_to_train = false
```

The remaining blockers are bounded human review of the 250-row Turkish fact registry, exact M1
parent weight/config manifest capture, memory route/optimizer smoke, training/evaluation DAG
closure and a separate SHA-bound training contract.

## Frozen implementation

```text
config       d476b8f5f38d972d9c8d075c3af910a1355b3272c65255dd91787058f64f42ec
runner       e40cf78729a4de2e4834ea4f046138236594abf995e8b61eed6395407e71aa2e
packing      fe5455062eaa7de6eacbbb96dac7bf7af86420fd463c353d6e8028fd91fad005
Slurm        f6ecc5ae491d96a7a9cfc2e55f29c5888d40f8c13c7560d52214ad81f81e993d
submitter    5e0b91d444fa1160d8d454230d115240882716400fa7ad703a0a4e12b0b3fdee
```

Bindings:

```text
config:    configs/corpora/vngrs_m2_oscar_exact_blocks_v1.yaml
runner:    scripts/m2/materialize_three_model_oscar_m2_blocks.py
packing:   src/transfer_vs_relearning/data/qwen_pre_m2.py
Slurm:     slurm/m2/materialize_three_model_oscar_m2_blocks.slurm
submitter: scripts/m2/submit_three_model_oscar_m2_blocks.sh
job name:  vngrs-m2-oscar-blocks-v1
```

## Authority boundary

This frozen document authorizes nothing by itself. A later explicit authorization bound to this
document's final SHA-256 and exact implementation commit may permit ordinary non-force push,
preservation-checked HU fast-forward and exactly one CPU materialization wave.

It does not authorize GPU, model-weight access, optimizer smoke, M2-A/M2-B training, evaluation,
fact-review verdict entry, cleanup, deletion, automatic retry, a fresh second root or mutation of
any predecessor evidence.
