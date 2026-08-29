# VNGRS OSCAR insan incelemesi sonucu ve Phase 2 planı

**Tarih:** 2026-08-29

**Durum:** `HUMAN REVIEW PASS / PHASE 2 LOCAL PLAN / UNEXECUTED`

## 1. İnsan incelemesi sonucu

Job `481908` tarafından üretilen authoritative 64-doküman packet'i kullanıcı tarafından yerel,
packet-bound HTML arayüzünde incelendi. İndirilen karar ledger'ı projeye değişmeden eklendi:

```text
artifacts/corpora/vngrs_m2_d0/human_review_decisions_73329e45fd8f.jsonl
```

- dosya byte SHA-256: `f6e1e2989de4593ca56707db6c3582f5efc7cd0bbd652ca965ef92ceeded7225`
- canonical karar SHA-256: `f7e1c09d9a1135d9fc44ac702cdbf35c5ed23181bc979117af7102cc4ada466b`
- karar ID-set SHA-256: `92468c08ad28c3fd0846b9ce897d2ab61c2793c59c1b7b5574a50daa9edf7820`
- bound packet SHA-256: `73329e45fd8ff2c6b24c36fa6f9b5bac767b9d25726b691d527c71f9fdf90af8`
- karar satırı / benzersiz ID: `64 / 64`
- verdict: `usable=64`, `unusable=0`, `unsafe=0`
- reviewer alanı: her satırda dolu, tek tutarlı reviewer
- not: `0` non-null not

Mevcut validator kararların authoritative packet'i tam ve birebir kapsadığını doğruladı. Bu PASS,
64 örneğin insan tarafından kullanılabilir bulunmasıdır; bütün 354,482 dokümanın tek tek okunmuş
olduğu veya corpus'un kusursuz olduğu iddiası değildir. Önceki regex/duplicate/boilerplate
tanıları korunur ve daha sonraki temizleme politikasında kullanılmalıdır.

Karar ledger'ı bilimsel kayıt olarak Git'e uygundur. Excerpt içeren full packet ve HTML yerel-only
kalır ve `.gitignore` ile yayın dışıdır.

## 2. Phase 2 amacı

Phase 2'nin tek amacı frozen OSCAR nüfusu ve split'i üç zorunlu tokenizer altında saymak, exact
token bütçesi kanıtını üretmek ve sonraki M2-A/M2-B training contract'ına girdi hazırlamaktır.
Phase 2 model inference veya eğitim değildir.

Zorunlu model rolleri şunlardır; tek primary model seçilmez:

1. `olmo` — `allenai/OLMo-2-0425-1B`
2. `qwen` — `Qwen/Qwen2.5-1.5B`
3. `smollm` — `HuggingFaceTB/SmolLM2-1.7B`

## 3. Frozen read-only girdiler

- V3 source root ve 32 object: `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3`
- full-object byte: `9,502,315,428`
- exact lowercase OSCAR nüfusu: `354,482` doküman / `1,553,923,133` UTF-8 byte
- selected-ID SHA: `c252d6b54d488e898f534564ef6c16196e22ae78f4fe0e61f83d4ad0bf83a056`
- frozen split root: `/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1`
- split SHA: `21f43359570ea66a73e969c1d0e8b4f08408f8ebbb71f50fc40dbd0d7e16f38f`
- train / held-out: `344,482 / 10,000`, overlap `0`
- coverage root: `/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1`
- coverage final SHA: `6ce5f1f7b13fa61ae3f9c021b237b0464e4989ae179dc73fe32030049772c177`
- exact decision ledger and hashes in §1
- three-model tokenizer manifest inventory:
  `artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1.json`, SHA
  `fd3901408e7dfa6f299b3c260229926ba5733bfd3a88f2af80e3ea522b143cb5`

Every source, predecessor root, split ID list, M1 epoch-036 parent and tokenizer asset is read-only.

## 4. Planned Phase 2 gates

### P2-0 — provenance and capacity preflight

- clean exact commit and fresh output root;
- all predecessor and decision hashes exact;
- no duplicate matching job;
- output/cache/tmp paths resolve to approved scratch;
- minimum `2 GiB` free and `1,024` inodes for compact evidence;
- offline mode and zero network;
- no model-weight file may be opened.

Any mismatch stops before tokenizer access.

### P2-1 — population/split revalidation

Read the preserved Parquet objects once, select exact `corpus == "oscar"`, and revalidate:

- document count, UTF-8 bytes and selected-ID SHA;
- exact train and held-out membership;
- disjointness and full union;
- frozen split SHA;
- 64/64 packet-bound human decisions.

The pass must not rewrite split IDs, review packet or human decisions.

### P2-2 — tokenizer-native compatibility gate

Load only the six inventoried tokenizer assets from the three exact M1 epoch-036 parent snapshots.
For every role verify asset size/SHA, tokenizer save/reload identity, vocabulary/special-token
metadata, non-empty Turkish probe encodings and deterministic repeated encoding. Network fallback,
tokenizer substitution and model-weight access fail closed.

### P2-3 — exact tokenizer accounting

For `add_special_tokens=false`, no truncation and no padding, produce separately for train and
held-out, for all three tokenizer roles:

- documents and UTF-8 bytes;
- total tokens;
- zero-token document count, required `0`;
- min, median, p95, p99 and max tokens per document;
- tokens-per-UTF8-byte ratio;
- canonical SHA-256 of sorted `stable_document_id -> token_count` rows;
- tokenizer identity and asset-manifest hashes.

Per-document token IDs and corpus text are not persisted. Only compact counts/hashes are written.
No common token budget is chosen silently: the three exact totals become inputs to the later
matched M2-A/M2-B execution contract.

### P2-4 — terminal evidence gate

Success requires 3/3 tokenizer reports and every earlier invariant. Terminal status is:

```text
D0_EVIDENCE_COMPLETE / M2_TRAINING_CONTRACT_NOT_FROZEN
ready_to_train = false
```

The compact fresh root is proposed as:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1
```

Expected outputs are a preflight record, decision validation, split/population validation, three
tokenizer-compatibility reports, six split-by-tokenizer accounting rows, a self-reference-free
artifact manifest, terminal audit and typed failure artifact when needed. Success output is capped
at 128 MiB.

## 5. Explicitly outside Phase 2

- model weights, forward pass, inference, evaluation or GPU/Slurm-GPU;
- tokenized corpus cache, packed training blocks or corpus copy;
- filtering/removing documents or rewriting the frozen split;
- M2-A or M2-B training;
- Turkish factual re-exposure construction;
- optimizer/LR/batch/step/token-budget selection;
- cleanup, deletion, automatic retry or result-aware rerun;
- `trwiki-20260601` training rows; trwiki remains cross-domain control only.

## 6. Work order after this plan

1. implement the Phase 2 operator, compact bundle, config, CPU launcher and fixture tests locally;
2. freeze a separate execution contract with exact implementation/config hashes;
3. obtain exact SHA-bound user authorization for push, HU fast-forward and one Phase 2 CPU wave;
4. inspect and document the terminal accounting result;
5. only then design the matched sibling training contract: M2-A = OSCAR adaptation, M2-B = the
   same adaptation exposure plus controlled Turkish factual re-exposure, for OLMo/Qwen/SmolLM.

This document authorizes no external action or Phase 2 execution by itself.
