# 152 — Bounded M1 Provenance Screen Execution Contract

**Tarih:** 2026-08-09 (Europe/Berlin)  
**Durum:** `BLOCKED — FROZEN CANDIDATE PANEL FAILS NATIVE-ASSET PROVENANCE GATE; HU EXECUTION NOT STARTED`
**Kapsam:** OLMo-2-0425-1B, Pythia-1.4B ve Falcon-RW-1B için tek-seed İngilizce M1 screen'i

## 1. Yetki ve bilimsel sınır

Kullanıcı 9 Ağustos 2026'da üç modelin ayrı worker'lar tarafından HU üzerinde M1 eğitilip aynı
evaluation paketiyle değerlendirilmesini açıkça yetkilendirdi. Bu belge yalnız bu bounded M1
screen'ini açar. Yeni M2-A/M2-B ailesi, Türkçe corpus seçimi, Turkish capability manipulation
check, seed-43, 2,500/25,000-fact scale-up veya mevcut `blocked_by_measurement_design` kararının
değiştirilmesi bu belgeyle açılmaz.

Bu çalışma sonuç-gören model seçimi değildir: üç modelin her biri önceden sabitlenmiş aynı eğitim,
endpoint ve gate kurallarını kullanır. Başarısız adaylar sonuçlara göre yeniden eğitilmez.

## 2. Frozen model paneli

| Worker | Model | Exact HF revision | Scientific role |
|---|---|---|---|
| 0 | `allenai/OLMo-2-0425-1B` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | English-dominant provenance candidate |
| 1 | `EleutherAI/pythia-1.4b` | `0da31d8fb309463877ed8c40e54a8f911dced3ec` | Reproducible English-base candidate |
| 2 | `tiiuae/falcon-rw-1b` | `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | English-only documented comparator |

Primary source routes:

- [OLMo-2 model card](https://huggingface.co/allenai/OLMo-2-0425-1B) and [OLMo repository](https://github.com/allenai/OLMo)
- [Pythia-1.4B model card](https://huggingface.co/EleutherAI/pythia-1.4b) and [Pythia repository](https://github.com/EleutherAI/pythia)
- [Falcon-RW-1B model card](https://huggingface.co/tiiuae/falcon-rw-1b)

Model weights, tokenizers and resolved local file hashes are recorded only in the scratch
acquisition manifests. “English-only” or “English-dominant” is provenance language, not proof of
mathematically zero Turkish exposure.

## 3. Frozen dataset and training contract

The screen reuses the byte-identified Document 103/105 M1 population already materialized on HU
scratch; it does not create a competing dataset copy:

```text
/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets
```

Required inputs are `dataset_manifest.json`, `train.jsonl` and `validation.jsonl`. The preflight
must verify the observed hashes before any model acquisition or training task is submitted.

| Item | Frozen value |
|---|---:|
| Subjects / facts | 100 / 500 |
| Training rows | 3,500 |
| Validation rows | 500 |
| Relations | 5 Relation V2 relations |
| Seed / data seed | 42 / 42 |
| Epochs | 36 |
| Effective batch | 500 rows |
| Optimizer updates | exactly 252 |
| Objective | answer-only causal LM |
| EOS supervision | false |
| Learning rate | `5e-5` |
| Block size | 128 |
| Precision | BF16 where the pinned model/runtime supports it |
| Endpoint | update 252 only |

Per-device batch and gradient accumulation may be changed only for an operational A100 fit, with
the product and update count preserved and the change recorded as a failed/changed compatibility
condition. No post-result LR, recipe, checkpoint or prompt change is permitted.

## 4. Frozen evaluation suite and gates

Every completed endpoint receives the same existing Document 105 suite:

- 500 canonical exact-prefix probes;
- 4,000 Forms A/B/C/D probes across direct and QA scaffolds;
- eight-cell robust intersection and per-relation cells;
- relation-swapped/binding evaluation;
- frozen WikiText-2 generic perplexity for base and trained model;
- 30 generic prompt/completion controls;
- empty-output, EOS-ending and synthetic-subject-intrusion diagnostics.

The gates are fixed before execution:

| Gate | Requirement |
|---|---:|
| Exact prefix | `>= 90%` |
| Every trained A/B cell | `>= 80%` globally and per relation |
| Every held-out C/D cell | `>= 80%` globally and per relation |
| Eight-cell robust intersection | `>= 70%` globally and per relation |
| Trained/base generic PPL ratio | `<= 1.25` |
| Integrity | no leakage, relation collapse, empty-output collapse or synthetic intrusion |

All three outcomes remain diagnostic until the final comparison report is complete. No candidate is
promoted to final M1 by this screen alone; any seed-43 or Turkish adaptation decision requires a
new contract.

## 5. Scratch, storage and retention

All outputs use the new scratch root:

```text
/vol/tmp2/yesildau/m1_provenance_screen_v1
```

Expected subtrees are `models/`, `training/`, `evaluations/`, `cache/`, `configs/`, `logs/`,
`manifests/`, `preflight/` and `tmp/`. No output, cache, checkpoint, model, evaluation or log may
resolve into `/vol/fob-vol6/mi25/yesildau`.

The conservative planning estimate is approximately 709 GiB including three candidates, eleven
checkpoint slots per candidate and shared overhead. The actual combined preflight must replace
this estimate with live free capacity/inode observations before each wave. After verification,
retain update-252 model-only endpoints, native tokenizers/configs, manifests, SHA-256 hashes and
compact evaluations. Do not delete intermediate artifacts in this contract.

## 6. Worker and execution topology

One Orca worker is assigned to each model. The coordinator owns the single family-level storage,
path, inode and queue preflight for each unchanged wave. Workers may submit or inspect only their
assigned candidate task after the shared preflight has passed; they must not create duplicate
arrays, alter the registry, change the model revision, or submit a replacement job because a task
is pending.

Execution order:

```text
local validation and commit
→ HU fast-forward and authoritative test/preflight
→ acquisition wave
→ read-only acquisition audit
→ compatibility/tokenizer/smoke gates
→ training wave
→ endpoint audit
→ evaluation wave
→ metrics, hashes and post-run storage audit
```

If a model fails access, compatibility, GPU cleanliness, finite-loss, tokenizer, or checkpoint
round-trip checks, record `NOT RUN — <exact gate>` and do not silently replace it.

## 8. Provenance gate result and current block

The all-three frozen-candidate screen is blocked before HU execution. The frozen dataset and
repository revision are valid, but the shared native-asset contract is not satisfied:

Read-only evidence anchors are repository/origin `a4ab7f7` and the frozen dataset with 3,500
training rows and 500 validation rows. The recorded hashes are: manifest
`c11f779229af14b196f2063ecdeb956e34444a30bf4086c331168f5cb11d6a26`, train
`8eb65505b22f5c7f8e67f2d1877efad7503489dd8bdf2608cad08791f7d05a67`, and validation
`495cdcda9049b372159ef167f3da866e4cb82caf1977796efbb3baa9e07973e7`.

| Candidate | Read-only provenance result | Decision |
|---|---|---|
| OLMo-2-0425-1B | Official revision exposes `merges.txt`, `tokenizer.json` and `vocab.json`, but no required native `tokenizer.model` | `NOT RUN — NATIVE ASSET GATE` |
| Pythia-1.4B | Frozen official revision exposes model/config files but lacks the required tokenizer asset set, including `merges.txt`, `tokenizer.json` and `vocab.json` | `NOT RUN — NATIVE ASSET GATE` |
| Falcon-RW-1B | Acquisition preflight passed | Blocked by shared dependency; no training/evaluation result |

Direct read-only checks of the Pythia `main`, `step143000`, `step0`, and Pythia-v0 alternatives
also failed to establish the complete native-asset contract. No fallback tokenizer, fabricated or
reconstructed asset, community conversion, or unpinned revision is permitted. Consequently, no
valid training or evaluation metrics exist for this frozen three-model screen.

The only contract-preserving ways forward are:

1. directly verify an official, exact pinned Pythia revision that contains every native asset
   required by this contract; or
2. obtain explicit user authorization for a candidate and/or contract change, with the exact
   revision, asset policy, and scientific implications recorded before implementation.

Until one of these conditions is met, do not create orchestration Tasks or Dispatches, access
HU/SSH/Slurm, launch workers, or mutate this preparation Run or any older Run/root/job. After
authorization and successful evidence checks, the required order is a fresh Run, read-only
recovery, PASS gate, exactly one shared DAG, and three index monitors.

## 9. Explicit non-authorizations

This contract does not authorize Turkish corpus download/materialization, benchmark scoring beyond
the frozen English M1 suite, M2-A/M2-B, seed-43, scale-up, cleanup/deletion, HU-home model copies,
or changes to Documents 100/151. The final result must be appended as a new chronological report;
the current global scientific gate remains unchanged regardless of the screen outcome.
