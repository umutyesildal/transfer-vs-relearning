# 189 — VNGRS OSCAR Phase-2 V1A retry preparation and gate

**Tarih:** 2026-08-29
**Durum:** `LOCALLY PREPARED / FROZEN / UNEXECUTED`

Document 188'deki `481910` sonucu yalnızca eski inventory'deki tek karakterlik OLMo SHA
transkripsiyon hatası nedeniyle fail-closed oldu. Bu belge V1'i yeniden yorumlamaz veya
değiştirmez; tek minimal retry düzeltmesini kaydeder.

## 1. Korunan kanıtlar

- V1 failure root read-only kalır:
  `/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1`.
- `control/d0_failure.json` SHA-256:
  `a7c566f61427d67921091ac49ffb1debfc9632c7d401bfa99145755fab783c3f`.
- Hatalı tarihsel inventory değiştirilmez:
  `artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1.json`.
- Tarihsel inventory SHA-256:
  `fd3901408e7dfa6f299b3c260229926ba5733bfd3a88f2af80e3ea522b143cb5`.

## 2. Tek veri düzeltmesi

Yeni append-only corrected inventory:

```text
artifacts/corpora/vngrs_m2_d0/tokenizer_manifest_inventory_v1a.json
```

SHA-256:

```text
72e1c51538a0a801a0fc766faea8af771fb126e190faefd19a0705af3a8886f9
```

Tek payload değişikliği OLMo `tokenizer.json` SHA-256'sının `b460...` değerinden HU exact asset
ve frozen snapshot manifestinin ortak `c460...` değerine düzeltilmesidir. OLMo corrected two-file
asset-manifest SHA-256'sı:

```text
04223e922f3f062978b34968d6653a185f2b971505b7c707e7bc95df33a46191
```

Qwen ve SmolLM satırları değişmez.

## 3. Yeni savunma

V1A yalnızca corrected inventory hash'ine güvenmez. Her tokenizer yüklenmeden önce aynı snapshot
root altındaki `snapshot_manifest.json`:

1. inventory'deki exact snapshot-manifest SHA-256 ile doğrulanır;
2. yalnız tokenizer asset satırları yeniden çıkarılır;
3. path/byte/SHA listesi corrected inventory ile exact karşılaştırılır;
4. ancak bundan sonra asset byte SHA ve offline tokenizer load yapılır.

Bu kapı model-weight bytes açmaz. Corpus/split/human-review doğrulamaları tokenizer erişiminden
önce kalır.

## 4. Fresh retry sınırı

Yeni proposed root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_retry_v1
```

V1A, önceki bilimsel girdileri ve Phase-2 accounting semantiğini değiştirmez. Başarı hâlâ yalnızca
üç tokenizer için altı exact train/held-out raporu ve terminal
`D0_EVIDENCE_COMPLETE / ready_to_train=false` anlamına gelir.

## 5. Kapı

V1A hazırlanması push, HU fast-forward, tokenizer asset erişimi veya Slurm CPU retry yetkisi
vermez. Model ağırlığı, GPU, inference, evaluation, M2-A/M2-B training, cleanup, deletion ve
automatic retry yasaktır. Ayrı frozen sözleşmenin final SHA-256'sına ve exact implementation
commitine bağlı açık kullanıcı yetkisi gerekir.
